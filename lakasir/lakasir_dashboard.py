import marimo

__generated_with = "0.15.2"
app = marimo.App(
    width="medium",
    app_title="Lakasir Analytics Dashboard",
)


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import ibis
    import dlt

    import plotly.express as px
    import plotly.graph_objects as go

    ibis.options.interactive = True
    return dlt, go, ibis, mo, pd, px


@app.cell
def _(mo, pd):
    min = "2025-01-01"
    max = "2025-09-12"

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
def _(dlt):
    pipeline = dlt.pipeline(
        pipeline_name="lakasir",
        destination="duckdb",
    )

    dataset = pipeline.dataset()

    about = dataset.table("about")
    sells = dataset.table("sells")
    sell_details = dataset.table("sell_details")
    return sell_details, sells


@app.cell
def _(ibis, sells):
    sells_df = ibis.memtable(sells.df())

    sells_df = sells_df.mutate(
        created_at =sells_df.created_at.cast("date"),
        updated_at =sells_df.updated_at.cast("date"),
        payed_money =sells_df.payed_money.cast("decimal(19, 2)"),
        money_changes =sells_df.money_changes.cast("decimal(19, 2)"),
        total_qty =sells_df.total_qty.cast("decimal"),
        total_price =sells_df.total_price.cast("decimal(19, 2)"),
        total_discount_per_item =sells_df.total_discount_per_item.cast("decimal(19, 2)"),
        discount =sells_df.discount.cast("decimal(19, 2)"),
        total_discount =sells_df.total_discount.cast("decimal(19, 2)"),
        grand_total_price =sells_df.grand_total_price.cast("decimal(19, 2)"),
        total_cost =sells_df.total_cost.cast("decimal(19, 2)"),
        member_name =sells_df.member__name.fill_null("Guest"),
    )

    sells_df = sells_df.select("id", "member_name", "code", "cashier", "payed_money", "money_changes", "total_qty", "total_price", "total_discount_per_item", "discount", "total_discount", "grand_total_price", "total_cost", "created_at", "updated_at")
    return (sells_df,)


@app.cell
def _(ibis, sell_details):
    sell_details_df = ibis.memtable(sell_details.df())

    sell_details_df = sell_details_df.mutate(
        created_at =sell_details_df.created_at.cast("date"),
        updated_at =sell_details_df.updated_at.cast("date"),
        qty =sell_details_df.qty.cast("decimal"),
        initial_price =sell_details_df.initial_price.cast("decimal(19, 2)"),
        selling_price =sell_details_df.selling_price.cast("decimal(19, 2)"),
        price =sell_details_df.price.cast("decimal(19, 2)"),
        discount =sell_details_df.discount.cast("decimal(19, 2)"),
        discount_price =sell_details_df.discount_price.cast("decimal(19, 2)"),
    )

    sell_details_df = sell_details_df.select("id", "selling_id", "product_id", "unit", "type", "name", "category", "initial_price", "selling_price", "qty", "price", "discount", "discount_price", "created_at", "updated_at")
    return (sell_details_df,)


@app.cell
def _(get_end_date, get_start_date, ibis, sell_details_df, sells_df):
    sells_df_by_date = sells_df.filter(
        sells_df.created_at.between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
    )

    def sells_agg(group_by: list[str]) -> ibis.Table:
        return (
            sells_df_by_date.group_by(group_by)
            .aggregate(
                payed_money=sells_df_by_date.payed_money.sum(),
                money_changes=sells_df_by_date.money_changes.sum(),
                total_qty=sells_df_by_date.total_qty.count(),
                total_price=sells_df_by_date.total_price.sum(),
                total_discount_per_item=sells_df_by_date.total_discount_per_item.sum(),
                discount=sells_df_by_date.discount.sum(),
                total_discount=sells_df_by_date.total_discount.sum(),
                grand_total_price=sells_df_by_date.grand_total_price.sum(),
                total_cost=sells_df_by_date.total_cost.sum(),
            )
        )

    sell_details_df_by_date = sell_details_df.filter(
        sell_details_df.created_at.between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
    )

    def sell_details_agg(group_by: list[str]) -> ibis.Table:
        return (
            sell_details_df_by_date.group_by(group_by)
            .aggregate(
                qty=sell_details_df_by_date.qty.sum(),
                price=sell_details_df_by_date.price.sum(),
                discount=sell_details_df_by_date.discount.sum(),
                discount_price=sell_details_df_by_date.discount_price.sum(),
            )
        )
    return (
        sell_details_agg,
        sell_details_df_by_date,
        sells_agg,
        sells_df_by_date,
    )


@app.cell
def _(mo, sells_df_by_date):
    # total revenue
    total_revenue = sells_df_by_date.grand_total_price.sum()

    # total cogs
    total_cost = sells_df_by_date.total_cost.sum()

    # total discounts
    total_discount = sells_df_by_date.total_discount.sum()

    # gross profit
    gross_profit = total_revenue - (total_cost + total_discount)

    total_revenue_stat = mo.stat(
        label="Total Revenue",
        bordered=True,
        caption=f"Jumlah pendapatan saat ini.",
        value=f"Rp. {total_revenue.to_pandas():,.0f}"
    )

    total_cost_stat = mo.stat(
        label="Total COGS / Cost",
        bordered=True,
        caption=f"Jumlah HPP / Biaya (harga pembelian produk).",
        value=f"Rp. {total_cost.to_pandas():,.0f}"
    )

    total_discount_stat = mo.stat(
        label="Total Discount",
        bordered=True,
        caption=f"Total potongan pembelian selama periode.",
        value=f"Rp. {total_discount.to_pandas():,.0f}"
    )

    gross_profit_stat = mo.stat(
        label="Gross Profit",
        bordered=True,
        caption=f"Total pendapatan kotor saat ini.",
        value=f"Rp. {gross_profit.to_pandas():,.0f}"
    )
    return (
        gross_profit_stat,
        total_cost_stat,
        total_discount_stat,
        total_revenue_stat,
    )


@app.cell
def _(
    gross_profit_stat,
    mo,
    total_cost_stat,
    total_discount_stat,
    total_revenue_stat,
):
    mo.hstack(
        [total_revenue_stat, total_cost_stat, total_discount_stat, gross_profit_stat],
        justify="space-around"
    )
    return


@app.cell
def _(sell_details_agg, sells_agg):
    # revenue by member
    sells_agg_by_member = sells_agg(["member_name"])

    # revenue by product category
    sell_details_agg_by_category = sell_details_agg(["category"])

    # revenue and discount by product
    sell_details_agg_by_name = sell_details_agg(["name"])
    return (
        sell_details_agg_by_category,
        sell_details_agg_by_name,
        sells_agg_by_member,
    )


@app.cell
def _(mo, px, sell_details_agg_by_category, sells_agg_by_member):
    # revenue by member
    revenue_by_member = sells_agg_by_member.mutate(
        total_pendapatan=sells_agg_by_member.grand_total_price,
        rasio_pendapatan=(sells_agg_by_member.grand_total_price / sells_agg_by_member.grand_total_price.sum().as_scalar()) * 100
    )

    revenue_by_member_pd = revenue_by_member.to_pandas()

    revenue_by_member_pd_plot = px.pie(
        revenue_by_member_pd, values='rasio_pendapatan', names='member_name',
        color_discrete_sequence=px.colors.sequential.Magenta,
    )

    revenue_by_member_pd_plot.update_layout(
        title=f"Rasio Pendapatan Berdasarkan Keanggotaan",
        title_font_size=16,
        width=500,
        height=300,
        margin=dict(l=20, r=20, t=35, b=20),

    )

    # revenue by category
    revenue_by_category = sell_details_agg_by_category.mutate(
        total_pendapatan=sell_details_agg_by_category.discount_price,
        rasio_pendapatan=(sell_details_agg_by_category.discount_price / sell_details_agg_by_category.discount_price.sum().as_scalar()) * 100
    )

    revenue_by_category_pd = revenue_by_category.to_pandas()

    revenue_ratio_by_category_plot = px.pie(
        revenue_by_category_pd, values='rasio_pendapatan', names='category',
        color_discrete_sequence=px.colors.sequential.Aggrnyl,
    )

    revenue_ratio_by_category_plot.update_layout(
        title=f"Rasio Pendapatan Berdasarkan Kategori",
        title_font_size=16,
        width=500,
        height=300,
        margin=dict(l=20, r=20, t=35, b=20),

    )

    mo.hstack(
        [
            mo.ui.plotly(revenue_by_member_pd_plot) if revenue_by_member_pd_plot else mo.md("Rasio pendapatan berdasarkan keanggotaan tidak tersedia."),
            mo.ui.plotly(revenue_ratio_by_category_plot) if revenue_ratio_by_category_plot else mo.md("Rasio pendapatan berdasarkan kategori tidak tersedia."),
        ],
        justify="space-around"
    )
    return


@app.cell
def _(mo, px, sell_details_agg_by_name):
    # revenue by item name
    revenue_by_item_name = sell_details_agg_by_name.mutate(
        total_pendapatan=sell_details_agg_by_name.discount_price,
        rasio_pendapatan=(sell_details_agg_by_name.discount_price / sell_details_agg_by_name.discount_price.sum().as_scalar()) * 100
    )

    revenue_by_item_name_pd = revenue_by_item_name.to_pandas()

    revenue_ratio_by_item_name_plot = px.pie(
        revenue_by_item_name_pd, values='rasio_pendapatan', names='name',
        color_discrete_sequence=px.colors.sequential.Oryel,
    )

    revenue_ratio_by_item_name_plot.update_layout(
        title=f"Rasio Pendapatan Berdasarkan Produk",
        title_font_size=16,
        width=500,
        height=300,
        margin=dict(l=20, r=20, t=35, b=20),

    )

    # discount by item name
    discount_by_item_name = sell_details_agg_by_name.mutate(
        total_potongan=sell_details_agg_by_name.discount,
        rasio_potongan=(sell_details_agg_by_name.discount / sell_details_agg_by_name.discount.sum().as_scalar()) * 100
    )

    discount_by_item_name_pd = discount_by_item_name.to_pandas()

    discount_ratio_by_item_name_plot = px.pie(
        discount_by_item_name_pd, values='rasio_potongan', names='name',
        color_discrete_sequence=px.colors.sequential.Tealgrn,
    )

    discount_ratio_by_item_name_plot.update_layout(
        title=f"Rasio Potongan Harga Berdasarkan Produk",
        title_font_size=16,
        width=500,
        height=300,
        margin=dict(l=20, r=20, t=35, b=20),

    )

    mo.hstack(
        [
            mo.ui.plotly(revenue_ratio_by_item_name_plot) if revenue_ratio_by_item_name_plot else mo.md("Rasio pendapatan berdasarkan produk tidak tersedia."),
            mo.ui.plotly(discount_ratio_by_item_name_plot) if discount_ratio_by_item_name_plot else mo.md("Rasio potongan harga berdasarkan produk tidak tersedia."),
        ],
        justify="space-around"
    )
    return


@app.cell
def _(ibis, mo, px, sell_details_df_by_date):
    # 10 top best-selling product
    top_sells = (
        sell_details_df_by_date.group_by(["name"]).aggregate(
            qty=sell_details_df_by_date.qty.sum(),
        ).order_by(ibis.desc("qty"))
    ).head(10)

    top_sells_pd = top_sells.to_pandas()

    top_sells_plot = px.funnel_area(
        names=top_sells_pd["name"],
        values=top_sells_pd["qty"],
        color_discrete_sequence=px.colors.sequential.Teal,
    )

    top_sells_plot.update_layout(
        title=f"Top 10 Produk Paling Laris",
        title_font_size=16,
        title_x=0.03,
        width=1015,
        height=300,
        margin=dict(l=150, r=20, t=35, b=20),

    )

    mo.hstack(
        [
            mo.ui.plotly(top_sells_plot) if top_sells_plot else mo.md("Top 10 produk paling laris tidak tersedia."),
        ],
        justify="center"
    )
    return


@app.cell
def _(get_end_date, get_start_date, mo):
    mo.md(f"""> Data <b>penjualan</b> dari: {get_start_date().strftime("%Y-%m-%d")} - {get_end_date().strftime("%Y-%m-%d")}""")
    return


@app.cell
def _(mo):
    sell_details_by_item_name = mo.ui.text(
        label="Berdasarkan nama item : ",
        placeholder="nama item ...",
    )

    mo.vstack(
        [sell_details_by_item_name],
        justify="start"
    )
    return (sell_details_by_item_name,)


@app.cell
def _(mo, sell_details_by_item_name, sell_details_df_by_date):
    sell_details_df_by_date_pd = (
        sell_details_df_by_date.to_pandas()
        .drop(columns=["product_id", "type", "initial_price", "selling_price", "updated_at"])
    )

    if len(sell_details_by_item_name.value) > 0:
        sells_by_filter = (
            sell_details_df_by_date_pd[sell_details_df_by_date_pd["name"] == sell_details_by_item_name.value]
        )
    else:
        sells_by_filter = (
            sell_details_df_by_date_pd
        )

    mo.ui.table(sells_by_filter, selection=None)
    return (sell_details_df_by_date_pd,)


@app.cell
def _(mo, sell_details_by_item_name):
    mo.md(f"Berikut adalah rasio <b>total harga</b> berdasarkan kontribusi <b>selling price</b> pada item <b>{sell_details_by_item_name.value}</b>.") if sell_details_by_item_name.value else mo.md("")
    return


@app.cell
def _(mo, sell_details_by_item_name, sell_details_df_by_date):
    if len(sell_details_by_item_name.value) > 0:
        # sell price ratio
        sell_price_ratio_by_name = (
            sell_details_df_by_date.filter(
                sell_details_df_by_date.name == sell_details_by_item_name.value
            ).group_by(["name", "selling_price"]).aggregate(
                total_discount=sell_details_df_by_date.discount.sum(),
                total_price=sell_details_df_by_date.price.sum(),
            )
        )

        sell_price_ratio_by_name = (
            sell_price_ratio_by_name.mutate(
                total_price_ratio=(sell_price_ratio_by_name.total_price / sell_price_ratio_by_name.total_price.sum().as_scalar()) * 100
            )
        )

        mo.stop(len(sell_details_by_item_name.value) > 0, mo.ui.table(sell_price_ratio_by_name, selection=None))
    return (sell_price_ratio_by_name,)


@app.cell
def _(mo, px, sell_details_by_item_name, sell_price_ratio_by_name):
    if len(sell_details_by_item_name.value) > 0:
    
        sell_price_ratio_by_name_pd = sell_price_ratio_by_name.to_pandas()
    
        sell_price_ratio_by_name_plot = px.pie(
            sell_price_ratio_by_name_pd, values='total_price_ratio', names='selling_price',
            color_discrete_sequence=px.colors.sequential.Purp,
        )
    
        sell_price_ratio_by_name_plot.update_layout(
            title=f"Rasio Harga Jual Berdasarkan Produk {sell_details_by_item_name.value}",
            title_font_size=16,
            title_x=0.03,
            width=1015,
            height=300,
            margin=dict(l=150, r=20, t=35, b=20),
    
        )
    else:
        sell_price_ratio_by_name_plot = None
    
    mo.ui.plotly(sell_price_ratio_by_name_plot) if sell_price_ratio_by_name_plot else mo.md("")
    return


@app.cell
def _(sell_details_by_item_name, sell_details_df_by_date_pd):
    STEP_PREDICTION = 3
    item_code_fill = sell_details_df_by_date_pd[sell_details_df_by_date_pd["name"] == sell_details_by_item_name.value]
    minimum_for_predict = len(sell_details_df_by_date_pd[sell_details_df_by_date_pd["name"] == sell_details_by_item_name.value]) > 2
    return STEP_PREDICTION, item_code_fill, minimum_for_predict


@app.cell
def _(
    STEP_PREDICTION,
    item_code_fill,
    minimum_for_predict,
    pd,
    sell_details_agg,
    sell_details_by_item_name,
):
    if len(item_code_fill) > 0 and minimum_for_predict:
        sell_forecast = (
            sell_details_agg(["created_at", "name"])
            .select("created_at", "name", "qty")
        )
    
        sell_forecast_pd = (
            sell_forecast.filter(
                sell_forecast.name == sell_details_by_item_name.value
            )
            .to_pandas().astype({
                "created_at": "datetime64[ns]",
                "name": "category",
                "qty": "int32"
            })
        )
    
        date_index = pd.DatetimeIndex(sell_forecast_pd.created_at)
        df_with_index = sell_forecast_pd.set_index(date_index)
    
        start_date_range = date_index.min()
        end_date_range = date_index.max()
        # set specify datetime with frequency
        complete_date_range = pd.date_range(start=start_date_range, end=end_date_range, freq='D')
    
        # reindexing
        sell_forecast_pd = df_with_index.reindex(complete_date_range)
    
        # fill the rows
        sell_forecast_pd = sell_forecast_pd.fillna({
            'name': sell_forecast_pd["name"].bfill(),
            'qty': 0.0
        })
    
        # Modelling and Forecasting
        from lightgbm import LGBMRegressor
        from skforecast.recursive import ForecasterRecursive
    
        # create forecaster
        forecaster = ForecasterRecursive(
            regressor=LGBMRegressor(random_state=int(sell_forecast_pd.name.size / 2), verbose=-1),
            lags=(sell_forecast_pd.name.size - 1)
        )
    
        forecaster.fit(y=sell_forecast_pd['qty'])
    
        predictions = forecaster.predict(steps=STEP_PREDICTION, last_window=None)
        predictions = pd.DataFrame(data=predictions)
    return predictions, sell_forecast_pd


@app.cell
def _(
    STEP_PREDICTION,
    item_code_fill,
    minimum_for_predict,
    mo,
    predictions,
    sell_details_by_item_name,
):
    perspective_by_sells_predict = ""

    if len(item_code_fill) > 0 and minimum_for_predict:
        mean_of_sell = sum(predictions["pred"].to_numpy()) / len(predictions["pred"].to_numpy())
        perspective_by_sells_predict = f"Hasil <b>prediksi</b> menunjukan dibutuhkan <b>rata-rata {mean_of_sell}</b> buah produk yang <b>siap jual</b> untuk produk <b>{sell_details_by_item_name.value}</b>, sehingga memenuhi <b>target penjualan</b> dalam <b>{STEP_PREDICTION} hari</b> kedepan."

    mo.md(perspective_by_sells_predict)
    return


@app.cell
def _(
    go,
    item_code_fill,
    minimum_for_predict,
    mo,
    predictions,
    sell_details_by_item_name,
    sell_forecast_pd,
):
    if len(item_code_fill) > 0 and minimum_for_predict:
        sell_forecast_plot = go.Figure()
    
        sell_forecast_plot_trace1 = go.Scatter(x=sell_forecast_pd.index, y=sell_forecast_pd["qty"], name="train", mode="lines")
        sell_forecast_plot_trace2 = go.Scatter(x=predictions.index, y=predictions["pred"], name="prediction", mode="lines")
        sell_forecast_plot.add_trace(sell_forecast_plot_trace1)
        sell_forecast_plot.add_trace(sell_forecast_plot_trace2)
    
        sell_forecast_plot.update_layout(
            title=f"Prediksi Penjualan Produk {sell_details_by_item_name.value}",
            title_font_size=16,
            xaxis_title="Tanggal",
            yaxis_title="Total Penjualan",
            height=400,
            margin=dict(l=20, r=20, t=35, b=20),
            legend=dict(orientation="h", yanchor="top", y=1.01, xanchor="left", x=0)
        )

    else:
        sell_forecast_plot = None
        if minimum_for_predict is False:
            error_details = mo.md("Jumlah transaksi <b>belum memenuhi syarat</b> untuk prediksi penjualan.")
        else:
            error_details = mo.md("Input <b>nama item</b> untuk prediksi penjualan.")

    mo.ui.plotly(sell_forecast_plot) if sell_forecast_plot else error_details
    return


if __name__ == "__main__":
    app.run()
