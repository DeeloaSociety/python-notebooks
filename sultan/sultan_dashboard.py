import marimo

__generated_with = "0.15.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import ibis

    import plotly.express as px
    import plotly.graph_objects as go

    ibis.options.interactive = True
    return go, mo, pd, px


@app.cell
def _(mo, pd):
    min = "2025-01-01"
    max = "2025-06-19"

    get_start_date, set_start_date = mo.state(pd.to_datetime(min))
    get_end_date, set_end_date = mo.state(pd.to_datetime(max))
    return get_end_date, get_start_date, set_end_date, set_start_date


@app.cell
def _(get_end_date, get_start_date, mo, pd, set_end_date, set_start_date):
    start_date = mo.ui.date(
        label="Start date",
        value=get_start_date().strftime("%Y-%m-%d"),
        on_change=lambda x: set_start_date(pd.to_datetime(x)),
    )

    end_date = mo.ui.date(
        label="End date",
        value=get_end_date().strftime("%Y-%m-%d"),
        on_change=lambda x: set_end_date(pd.to_datetime(x)),
    )
    return end_date, start_date


@app.cell
def _(mo, pd, set_end_date, set_start_date):
    def yearly_button(yearly):
        start = pd.to_datetime(f"{yearly}-01-01")
        end = pd.to_datetime(f"{yearly + 1}-01-01")

        def handle_click(v):
            set_start_date(start)
            set_end_date(end)
            return 1

        return mo.ui.button(
            label=f"{yearly}",
            on_click=handle_click
        )

    button_21 = yearly_button(2021)
    button_22 = yearly_button(2022)
    button_23 = yearly_button(2023)
    button_24 = yearly_button(2024)
    return button_21, button_22, button_23, button_24


@app.cell
def _(button_21, button_22, button_23, button_24, end_date, mo, start_date):
    mo.hstack(
        [
            mo.md(f"{start_date} - {end_date}"),
            mo.hstack(
                [
                    mo.md("Quick yearly:"),
                    button_21,
                    button_22,
                    button_23,
                    button_24,
                ],
                justify="end"
            ),
        ]
    )
    return


@app.cell
def _(get_end_date, get_start_date, mo):
    mo.md(f"""> Compared to: {get_start_date().strftime("%Y-%m-%d")} - {get_end_date().strftime("%Y-%m-%d")}""")
    return


@app.cell
def _():
    from sultanconnect import SultanConnect

    sultanConnect = SultanConnect()
    return (sultanConnect,)


@app.cell
def _(get_end_date, get_start_date, mo, sultanConnect):
    total_revenue = sultanConnect.selling().totalRevenue(get_start_date().strftime("%Y-%m-%d"),
                                                          get_end_date().strftime("%Y-%m-%d")).to_pandas()
    total_revenue_stat = mo.stat(
        label="Total Revenue",
        bordered=True,
        caption=f"Jumlah pendapatan Saat Ini.",
        value=f"Rp. {total_revenue:,.0f}"
    )

    total_cogs = sultanConnect.selling().totalCOGS(get_start_date().strftime("%Y-%m-%d"),
                                                       get_end_date().strftime("%Y-%m-%d")).to_pandas()
    total_cogs_stat = mo.stat(
        label="Total COGS",
        bordered=True,
        caption=f"Jumlah HPP (Harga Pembelian Produk).",
        value=f"Rp. {total_cogs:,.0f}"
    )

    total_gross = sultanConnect.selling().totalGross(get_start_date().strftime("%Y-%m-%d"),
                                                       get_end_date().strftime("%Y-%m-%d")).to_pandas()
    total_gross_stat = mo.stat(
        label="Gross Profit",
        bordered=True,
        caption=f"Keuntungan kotor selama periode.",
        value=f"Rp. {total_gross:,.0f}"
    )

    total_stock = sultanConnect.inventory().between(get_start_date().strftime("%Y-%m-%d"),
                                                    get_end_date().strftime("%Y-%m-%d")).totalStock().to_pandas()
    total_stocks_stat = mo.stat(
        label="Total Stocks",
        bordered=True,
        caption=f"Total nilai semua sisa stock saat Ini.",
        value=f"Rp. {total_stock:,.0f}"
    )
    return (
        total_cogs_stat,
        total_gross_stat,
        total_revenue_stat,
        total_stocks_stat,
    )


@app.cell
def _(
    mo,
    total_cogs_stat,
    total_gross_stat,
    total_revenue_stat,
    total_stocks_stat,
):
    mo.hstack(
        [total_revenue_stat, total_cogs_stat, total_gross_stat, total_stocks_stat],
        justify="space-around"
    )
    return


@app.cell
def _(get_end_date, get_start_date, go, mo, sultanConnect):
    revenue_by_category_pd = (
        sultanConnect.soldItem()
            .between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
            .revenue(type="category").to_pandas()
    )

    figure_revenue_ratio_by_category = go.Figure()

    trace_pie_revenue_ratio_by_category = go.Pie(
        labels=revenue_by_category_pd["category_name"],
        values=revenue_by_category_pd["revenue_ratio"],
        marker=dict(colors=["aliceblue"]),
    )

    figure_revenue_ratio_by_category.add_trace(trace_pie_revenue_ratio_by_category)

    figure_revenue_ratio_by_category.update_layout(
        title=f"Revenue Ratio by Category",
        title_font_size=16,
        width=500,
        height=300,
        margin=dict(l=20, r=20, t=35, b=20),
    )

    revenue_by_suplier_pd = (
        sultanConnect.soldItem()
            .between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
            .revenue(type="suplier").to_pandas()
    )

    figure_revenue_ratio_by_supplier = go.Figure()

    trace_pie_revenue_ratio_by_supplier = go.Pie(
        labels=revenue_by_suplier_pd["suplier_name"],
        values=revenue_by_suplier_pd["revenue_ratio"],
        marker=dict(colors=["darkkhaki"]),
    )

    figure_revenue_ratio_by_supplier.add_trace(trace_pie_revenue_ratio_by_supplier)

    figure_revenue_ratio_by_supplier.update_layout(
        title=f"Revenue Ratio by Supplier",
        title_font_size=16,
        width=500,
        height=300,
        margin=dict(l=20, r=20, t=35, b=20),
    )

    mo.hstack(
        [
            mo.ui.plotly(figure_revenue_ratio_by_category) if figure_revenue_ratio_by_category else mo.md("Revenue Ratio by category not found."),
            mo.ui.plotly(figure_revenue_ratio_by_supplier) if figure_revenue_ratio_by_supplier else mo.md("Revenue Ratio by supplier not found."),
        ],
        justify="space-around"
    )
    return


@app.cell
def _(get_end_date, get_start_date, go, mo, px, sultanConnect):
    frequently_purchased_ratio_pd = (
        sultanConnect.inventory()
            .between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
            .frequentlyPurchased().to_pandas().head(5)
    )

    figure_frequently_purchased_ratio = go.Figure()

    trace_pie_frequently_purchased_ratio = go.Pie(
        labels=frequently_purchased_ratio_pd["item_name"],
        values=frequently_purchased_ratio_pd["sales_ratio"],
        marker=dict(colors=px.colors.sequential.RdBu),
    )

    figure_frequently_purchased_ratio.add_trace(trace_pie_frequently_purchased_ratio)

    figure_frequently_purchased_ratio.update_layout(
        title=f"Top Frequently Purchased Ratio",
        title_font_size=16,
        title_x=0.03,
        width=950,
        height=300,
        margin=dict(l=20, r=20, t=35, b=20),
    )

    mo.hstack(
        [
            mo.ui.plotly(figure_frequently_purchased_ratio) if figure_frequently_purchased_ratio else mo.md("Frequently purchased ratio not found.")
        ],
        justify="space-around"
    )
    return


@app.cell
def _(get_end_date, get_start_date, mo):
    mo.md(f"""> Data <b>inventaris</b> dari: {get_start_date().strftime("%Y-%m-%d")} - {get_end_date().strftime("%Y-%m-%d")}""")
    return


@app.cell
def _(get_end_date, get_start_date, mo, sultanConnect):
    inventory_by = (
        sultanConnect.inventory()
            .between(get_start_date().strftime("%Y-%m-%d"),get_end_date().strftime("%Y-%m-%d"))
            .load().to_pandas().drop(columns=["item_created", "item_flag", "item_purchase_price"])
    )

    mo.ui.table(inventory_by, selection=None)
    return


@app.cell
def _(get_end_date, get_start_date, mo):
    mo.md(f"""> Data <b>penjualan</b> dari: {get_start_date().strftime("%Y-%m-%d")} - {get_end_date().strftime("%Y-%m-%d")}""")
    return


@app.cell
def _(mo):
    selling_by_item_name = mo.ui.text(
        label="Berdasarkan nama item : ",
        placeholder="nama item ...",
    )

    mo.vstack(
        [selling_by_item_name],
        justify="start"
    )
    return (selling_by_item_name,)


@app.cell
def _(get_end_date, get_start_date, mo, selling_by_item_name, sultanConnect):
    selling_by = (
        sultanConnect.selling().filter()
        .between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
    )

    if len(selling_by_item_name.value) > 0:
        selling_by_filter = (
            selling_by.itemName(selling_by_item_name.value).load()
            .to_pandas().drop(columns=["item_purchase_price", "item_profit_margin"])
        )
    else:
        selling_by_filter = (
            selling_by.load().to_pandas().drop(columns=["item_purchase_price", "item_profit_margin"])
        )

    mo.ui.table(selling_by_filter, selection=None)
    return


@app.cell
def _(mo, selling_by_item_name):
    mo.md(f"Berikut adalah <b>total revenue</b> dan <b>rasio</b> dari kontribusi <b>sell price</b> pada item <b>{selling_by_item_name.value}</b>.") if selling_by_item_name.value else mo.md("")
    return


@app.cell
def _(get_end_date, get_start_date, mo, selling_by_item_name, sultanConnect):
    if len(selling_by_item_name.value) > 0:
        revenue_by_sell_price = (
            sultanConnect.selling()
                .between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
                .bySellPrice(item_name=selling_by_item_name.value).to_pandas()
        )

        mo.stop(len(selling_by_item_name.value) > 0, mo.ui.table(revenue_by_sell_price, selection=None))
    return


@app.cell
def _(get_end_date, get_start_date, selling_by_item_name, sultanConnect):
    step = 3
    item_code_fill = sultanConnect.item().byItemName(selling_by_item_name.value).to_pandas()

    if len(item_code_fill) > 0:
        selling_for_predict = (
            sultanConnect.selling().filter()
                .between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
                .forecast(item_name=selling_by_item_name.value)
                .prepare(target='item_quantity')
                .fit()
        )

        selling_predict_result = selling_for_predict.predict(step=step)

        item_stock = (
            sultanConnect.item()
                .byItemName(item_name=selling_by_item_name.value).select("item_stock")
                .to_pandas().astype("float").values.item())
    return (
        item_code_fill,
        item_stock,
        selling_for_predict,
        selling_predict_result,
        step,
    )


@app.cell
def _(
    item_code_fill,
    item_stock,
    mo,
    selling_by_item_name,
    selling_predict_result,
    step,
):
    perspective_by_stock_predict = ""

    if len(item_code_fill) > 0:
        mean_stock_predict = selling_predict_result.pred.mean()
        out_of_stock = mean_stock_predict - item_stock
        if item_stock < mean_stock_predict:
            perspective_by_stock_predict = f"Hasil prediksi menunjukan bahwa dibutuhkan <b>{int(out_of_stock)} stock</b> lagi untuk <b>{selling_by_item_name.value}</b> sehingga memenuhi target dalam <b>{step} hari</b> kedepan."
        else:
            perspective_by_stock_predict = f"Hasil prediksi menunjukan bahwa jumlah stok cukup untuk target <b>{step} hari</b> kedepan."

    mo.md(perspective_by_stock_predict)
    return


@app.cell
def _(
    go,
    item_code_fill,
    mo,
    selling_by_item_name,
    selling_for_predict,
    selling_predict_result,
):
    if len(item_code_fill) > 0:
        figure = go.Figure()

        trace1 = go.Scatter(x=selling_for_predict.df.index, y=selling_for_predict.df["item_quantity"], name="train",
                                mode="lines")
        trace2 = go.Scatter(x=selling_predict_result.index, y=selling_predict_result["pred"], name="prediction",
                                mode="lines")

        figure.add_trace(trace1)
        figure.add_trace(trace2)
        figure.update_layout(
            title=f"Real vs predicted value for {selling_by_item_name.value}",
            title_font_size=16,
            xaxis_title="Data times",
            yaxis_title="Quantity Sales",
            height=400,
            margin=dict(l=20, r=20, t=35, b=20),
            legend=dict(orientation="h", yanchor="top", y=1.01, xanchor="left", x=0)
        )

    else:
        figure = None

    mo.ui.plotly(figure) if figure else mo.md("Input <b>nama item</b> untuk prediksi stok item.")
    return


if __name__ == "__main__":
    app.run()
