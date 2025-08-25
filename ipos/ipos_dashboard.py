import marimo

__generated_with = "0.15.0"
app = marimo.App(width="medium", app_title="iPos Analytics Dashboard")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import ibis

    from format_currency import format_currency

    import plotly.express as px
    import plotly.graph_objects as go

    colors = [
        "cornflowerblue",
        "darkcyan",
        "coral",
        "chocolate",
        "blueviolet",
    ]

    ibis.options.interactive = True
    return colors, format_currency, go, mo, np, pd, px


@app.cell
def _(mo, pd):
    min = "2025-01-01"
    max = "2025-08-30"

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
            mo.md(f"{start_date} → {end_date}"),
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
    mo.md(f"""> Dalam <b>periode</b>: {get_start_date().strftime("%Y-%m-%d")} - {get_end_date().strftime("%Y-%m-%d")}""")
    return


@app.cell
def _():
    from iposconnect import IposConnect

    iposConnect = IposConnect()
    return (iposConnect,)


@app.cell
def _(format_currency, get_end_date, get_start_date, iposConnect, mo):
    journal = (
        # call iposConnect.journal() for version 4
        iposConnect.journalV5()
        .between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
    )

    income = journal.income()

    total_revenue = mo.stat(
        label="Total Revenue",
        bordered=True,
        caption=f"Jumlah pendapatan.",
        value=f"{format_currency(income.totalRevenue().to_pandas(), 'ID')}"
    )

    total_cogs = mo.stat(
        label="Total COGS",
        bordered=True,
        caption=f"Jumlah HPP & lain-lain.",
        value=f"{format_currency(income.totalCOGS().to_pandas(), 'ID')}"
    )

    total_expense = mo.stat(
        label="Total Expense",
        bordered=True,
        caption=f"Jumlah beban operasional.",
        value=f"{format_currency(income.totalExpense().to_pandas(), 'ID')}"
    )

    gross_profit = mo.stat(
        label="Gross Profit",
        bordered=True,
        caption=f"Keuntungan kotor.",
        value=f"{format_currency(income.grossProfit().to_pandas(), 'ID')}"
    )

    net_profit = mo.stat(
        label="Net Profit",
        bordered=True,
        caption=f"Keuntungan bersih selama periode.",
        value=f"{format_currency(income.netProfit().to_pandas(), 'ID')}"
    )

    mo.hstack(
        [total_revenue, total_cogs, total_expense, gross_profit, net_profit],
        justify="space-around"
    )
    return (journal,)


@app.cell
def _(journal, mo, np):
    currentRatio = np.round(float(journal.financialRatio().currentRatio()), decimals=2)
    quickRatio = np.round(float(journal.financialRatio().quickRatio()), decimals=2)
    md_liqudity = f"""
    \n<b>Current Ratio</b>: {currentRatio}
    \n<b>Quick Ratio</b>: {quickRatio}
    """

    debtToAssetRatio = np.round(float(journal.financialRatio().debtToAssetRatio()*100), decimals=2)
    md_solvency = f"""
    \n<b>Debt To Asset Ratio</b>: {debtToAssetRatio}%, ini berarti {debtToAssetRatio}% dari aset perusahaan <b>dibiayai</b> oleh <b>utang</b>.
    """

    grossProfitMarginRatio = np.round(float(journal.financialRatio().grossProfitMarginRatio()*100), decimals=2)
    netProfitMarginRatio = np.round(float(journal.financialRatio().netProfitMarginRatio()*100), decimals=2)
    md_profitability = f"""
    \n<b>Gross Profit Margin Ratio</b>: {grossProfitMarginRatio}%, adalah selisih laba kotor dari <b>Total Pendapatan (Revenue)</b>.
    \n<b>Net Profit Margin Ratio</b>: {netProfitMarginRatio}%, adalah selisih laba bersih dari <b>Total Pendapatan (Revenue)</b>.
    """

    socialResponsibilityToProfitRatio = np.round(float(journal.financialRatio().socialResponsibilityToProfitRatio()*100), decimals=2)
    md_csr = f"""
    \n<b>CSR To Profit Ratio</b>: {socialResponsibilityToProfitRatio}%, ini berarti {socialResponsibilityToProfitRatio}% telah disalurkan dalam bentuk <b>Amal</b> dari <b>Laba bersih (Net Profit)</b>.
    \n<b>اَلشَّيْطٰنُ يَعِدُكُمُ الْفَقْرَ وَيَأْمُرُكُمْ بِالْفَحْشَاۤءِۚ وَاللّٰهُ يَعِدُكُمْ مَّغْفِرَةً مِّنْهُ وَفَضْلًاۗ وَاللّٰهُ وَاسِعٌ عَلِيْمٌۖ </b>
    \n<b>"Setan menjanjikan (menakut-nakuti) kamu kemiskinan dan menyuruh kamu berbuat keji (kikir), sedangkan Allah menjanjikan kamu ampunan dan karunia-Nya. Allah Mahaluas lagi Maha Mengetahui." QS. Al-Baqarah: 268</b>
    """

    mo.accordion(
        {
            "Rasio Liquditas": mo.md(md_liqudity),
            "Rasio Solvabilitas": mo.md(md_solvency),
            "Rasio Profitabilitas": mo.md(md_profitability),
            "Rasio Keuangan Islam": mo.md(md_csr),
        },
    )
    return


@app.cell
def _(get_end_date, get_start_date, iposConnect):
    purchase_receipt = (
        iposConnect.purchaseReceipt()
            .between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
    )

    purchase_receipt_details = (
        iposConnect.purchaseReceiptDetails()
            .between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
    )

    sales_invoice = (
        iposConnect.salesInvoice()
            .between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
    )

    sales_invoice_details = (
        iposConnect.salesInvoiceDetails()
            .between(get_start_date().strftime("%Y-%m-%d"), get_end_date().strftime("%Y-%m-%d"))
    )
    return (
        purchase_receipt,
        purchase_receipt_details,
        sales_invoice,
        sales_invoice_details,
    )


@app.cell
def _(go, mo, px, sales_invoice_details):
    revenue_by_item_code_pd = (
        sales_invoice_details.parts()
            .revenueByItemCode()
            .to_pandas()
    )

    figure_revenue_ratio_by_item_code = go.Figure()

    trace_pie_revenue_ratio_by_item_code = go.Pie(
        labels=revenue_by_item_code_pd["kode_item"],
        values=revenue_by_item_code_pd["rasio_pendapatan"],
        # https://plotly.com/python/builtin-colorscales/
        marker=dict(colors=px.colors.sequential.Magenta),
    )

    figure_revenue_ratio_by_item_code.add_trace(trace_pie_revenue_ratio_by_item_code)

    figure_revenue_ratio_by_item_code.update_layout(
        title=f"Rasio Pendapatan Berdasarkan Kode Item",
        title_font_size=15,
        width=400,
        height=350,
        margin=dict(l=20, r=20, t=35, b=20),
        legend=dict(orientation="h", yanchor="top", y=1.01, xanchor="left", x=0),
    )

    revenue_by_category_pd = (
        sales_invoice_details.parts()
            .revenueByItemCategory()
            .to_pandas()
    )

    figure_revenue_ratio_by_category = go.Figure()

    trace_pie_revenue_ratio_by_category = go.Pie(
        labels=revenue_by_category_pd["jenis"],
        values=revenue_by_category_pd["rasio_pendapatan"],
        marker=dict(colors=px.colors.sequential.Aggrnyl),
    )

    figure_revenue_ratio_by_category.add_trace(trace_pie_revenue_ratio_by_category)

    figure_revenue_ratio_by_category.update_layout(
        title=f"Rasio Pendapatan Berdasarkan Jenis Item",
        title_font_size=15,
        width=400,
        height=250,
        margin=dict(l=20, r=20, t=35, b=20),
    )

    mo.hstack(
        [
            mo.ui.plotly(figure_revenue_ratio_by_item_code) if figure_revenue_ratio_by_item_code else mo.md("Rasio pendapatan berdasarkan produk tidak tersedia."),
            mo.ui.plotly(figure_revenue_ratio_by_category) if figure_revenue_ratio_by_category else mo.md("Rasio pendapatan berdasarkan Jenis Item tidak tersedia."),
        ],
        justify="space-around"
    )
    return


@app.cell
def _(go, mo, px, sales_invoice_details):
    revenue_by_customer_pd = (
            sales_invoice_details.parts()
            .revenueByCustomer()
            .to_pandas()
    )

    figure_revenue_ratio_by_customer = go.Figure()

    trace_pie_revenue_ratio_by_customer = go.Pie(
        labels=revenue_by_customer_pd["kode_pelanggan"],
        values=revenue_by_customer_pd["rasio_pendapatan"],
        marker=dict(colors=px.colors.sequential.Oryel),
    )

    figure_revenue_ratio_by_customer.add_trace(trace_pie_revenue_ratio_by_customer)

    figure_revenue_ratio_by_customer.update_layout(
        title=f"Rasio Pendapatan Berdasarkan Pelanggan",
        title_font_size=15,
        width=400,
        height=250,
        margin=dict(l=20, r=20, t=35, b=20),
        legend=dict(orientation="h", yanchor="top", y=1.01, xanchor="left", x=0),
    )

    revenue_by_warehouse_pd = (
            sales_invoice_details.parts()
            .revenueByWarehouse()
            .to_pandas()
    )

    figure_revenue_ratio_by_warehouse = go.Figure()

    trace_pie_revenue_ratio_by_warehouse = go.Pie(
        labels=revenue_by_warehouse_pd["lokasi_keluar"],
        values=revenue_by_warehouse_pd["rasio_pendapatan"],
        marker=dict(colors=px.colors.sequential.Tealgrn),
    )

    figure_revenue_ratio_by_warehouse.add_trace(trace_pie_revenue_ratio_by_warehouse)

    figure_revenue_ratio_by_warehouse.update_layout(
        title=f"Rasio Pendapatan Berdasarkan Kantor/Gudang",
        title_font_size=15,
        width=400,
        height=350,
        margin=dict(l=20, r=20, t=35, b=20),
    )

    mo.hstack(
        [
            mo.ui.plotly(figure_revenue_ratio_by_customer) if figure_revenue_ratio_by_customer else mo.md("Rasio pendapatan berdasarkan pelanggan tidak tersedia."),
        mo.ui.plotly(figure_revenue_ratio_by_warehouse) if figure_revenue_ratio_by_warehouse else mo.md("Rasio pendapatan berdasarkan kantor/gudang tidak tersedia."),
        ],
        justify="space-around"
    )
    return


@app.cell
def _(get_end_date, get_start_date, mo):
    mo.md(f"""> Data <b>penerimaan pembelian produk</b> dari: {get_start_date().strftime("%Y-%m-%d")} - {get_end_date().strftime("%Y-%m-%d")}""")
    return


@app.cell
def _(purchase_receipt_details):
    receipt_by_warehouse = (
        purchase_receipt_details.parts().receiptByWarehouse()
    )
    return (receipt_by_warehouse,)


@app.cell
def _(
    colors,
    go,
    mo,
    purchase_receipt,
    purchase_receipt_details,
    receipt_by_warehouse,
):
    def purchaseReceiptRecap():
        return mo.ui.table(purchase_receipt.parts().recap(), selection=None)

    def purchaseReceiptDaily():
        return mo.ui.table(purchase_receipt_details.parts().byDaily(), selection=None)

    def purchaseReceiptGraphic():
        total_receipt_by_warehouse = (
            purchase_receipt_details.parts()
                .agg(["kode_item", "nama_item", "lokasi_masuk"])
                .select("kode_item", "nama_item", "lokasi_masuk", "jumlah_item")
        )

        total_receipt_by_warehouse_pd = total_receipt_by_warehouse.to_pandas()

        total_receipt_by_warehouse_plot = go.Figure()

        for index, row in receipt_by_warehouse.to_pandas().iterrows():
            trace_total_receipt_by_warehouse = go.Bar(
                x=total_receipt_by_warehouse_pd.kode_item[total_receipt_by_warehouse_pd.lokasi_masuk == row["lokasi_masuk"]],
                y=total_receipt_by_warehouse_pd.jumlah_item[total_receipt_by_warehouse_pd.lokasi_masuk == row["lokasi_masuk"]],
                name=row["lokasi_masuk"],
                text=total_receipt_by_warehouse_pd.jumlah_item[total_receipt_by_warehouse_pd.lokasi_masuk == row["lokasi_masuk"]],
                marker=dict(color=colors[index])
            )
            total_receipt_by_warehouse_plot.add_trace(trace_total_receipt_by_warehouse)

        total_receipt_by_warehouse_plot.update_layout(
            title=f"Grafik Total Penerimaan Produk",
            title_font_size=15,
            xaxis_title="Kode Item",
            yaxis_title="Total Penerimaan",
            font=dict(
                family="Inter, sans-serif",
                size=12,
            ),
            height=400,
            margin=dict(l=20, r=20, t=35, b=20),
            legend=dict(orientation="h", yanchor="top", y=1.01, xanchor="left", x=0)
        )

        return mo.ui.plotly(total_receipt_by_warehouse_plot)
    return purchaseReceiptDaily, purchaseReceiptGraphic, purchaseReceiptRecap


@app.cell
def _(mo, purchaseReceiptDaily, purchaseReceiptGraphic, purchaseReceiptRecap):
    mo.ui.tabs({
        "Harian": purchaseReceiptDaily(),
        "Recap": purchaseReceiptRecap(),
        "Grafik": purchaseReceiptGraphic(),
    })
    return


@app.cell
def _(get_end_date, get_start_date, mo):
    mo.md(f"""> Data <b>penjualan produk & layanan</b> dari: {get_start_date().strftime("%Y-%m-%d")} - {get_end_date().strftime("%Y-%m-%d")}""")
    return


@app.cell
def _(sales_invoice_details):
    revenue_by_warehouse = (
        sales_invoice_details.parts().revenueByWarehouse()
    )
    return (revenue_by_warehouse,)


@app.cell
def _(
    colors,
    go,
    mo,
    revenue_by_warehouse,
    sales_invoice,
    sales_invoice_details,
):
    def salesInvoiceRecap():
        return mo.ui.table(sales_invoice.parts().recap(), selection=None)

    def salesInvoiceDaily():
        return mo.ui.table(sales_invoice_details.parts().byDaily(), selection=None)

    def salesInvoiceGraphic():
        total_sales_by_warehouse = (
            sales_invoice_details.parts()
                .agg(["kode_item", "nama_item", "lokasi_keluar"])
                .select("kode_item", "nama_item", "lokasi_keluar", "jumlah_item")
        )

        total_sales_by_warehouse_pd = total_sales_by_warehouse.to_pandas()

        total_sales_by_warehouse_plot = go.Figure()

        for index, row in revenue_by_warehouse.to_pandas().iterrows():
            trace_total_sales_by_warehouse = go.Bar(
                x=total_sales_by_warehouse_pd.kode_item[total_sales_by_warehouse_pd.lokasi_keluar == row["lokasi_keluar"]],
                y=total_sales_by_warehouse_pd.jumlah_item[total_sales_by_warehouse_pd.lokasi_keluar == row["lokasi_keluar"]],
                name=row["lokasi_keluar"],
                text=total_sales_by_warehouse_pd.jumlah_item[total_sales_by_warehouse_pd.lokasi_keluar == row["lokasi_keluar"]],
                marker=dict(color=colors[index])
            )
            total_sales_by_warehouse_plot.add_trace(trace_total_sales_by_warehouse)

        total_sales_by_warehouse_plot.update_layout(
            title=f"Grafik Total Penjualan Produk/Jasa",
            title_font_size=15,
            xaxis_title="Kode Item",
            yaxis_title="Total Penjualan",
            font=dict(
                family="Inter, sans-serif",
                size=12,
            ),
            height=400,
            margin=dict(l=20, r=20, t=35, b=20),
            legend=dict(orientation="h", yanchor="top", y=1.01, xanchor="left", x=0)
        )

        return mo.ui.plotly(total_sales_by_warehouse_plot)
    return salesInvoiceDaily, salesInvoiceGraphic, salesInvoiceRecap


@app.cell
def _(mo, salesInvoiceDaily, salesInvoiceGraphic, salesInvoiceRecap):
    mo.ui.tabs({
        "Harian": salesInvoiceDaily(),
        "Rekap": salesInvoiceRecap(),
        "Grafik": salesInvoiceGraphic(),
    })
    return


@app.cell
def _(mo):
    mo.md(f"""> Data <b>inventaris semua produk :</b> semua periode""")
    return


@app.cell
def _(iposConnect):
    item_stock = iposConnect.itemStock()
    return (item_stock,)


@app.cell
def _(colors, go, item_stock, mo, revenue_by_warehouse):
    def itemStockRecap():
        return mo.ui.table(item_stock.parts().load().select("kode_item", "kantor", "stok"), selection=None)

    def itemStockGraphic():
        item_stock_by_warehouse = (
            item_stock.parts()
                .agg(["kode_item", "kantor"])
        )

        item_stock_by_warehouse_pd = item_stock_by_warehouse.to_pandas()

        item_stock_by_warehouse_plot = go.Figure()

        for index, row in revenue_by_warehouse.to_pandas().iterrows():
            trace_item_stock_by_warehouse = go.Bar(
                x=item_stock_by_warehouse_pd.kode_item[item_stock_by_warehouse_pd.kantor == row["lokasi_keluar"]],
                y=item_stock_by_warehouse_pd.stok[item_stock_by_warehouse_pd.kantor == row["lokasi_keluar"]],
                name=row["lokasi_keluar"],
                text=item_stock_by_warehouse_pd.stok[item_stock_by_warehouse_pd.kantor == row["lokasi_keluar"]],
                marker=dict(color=colors[index])
            )
            item_stock_by_warehouse_plot.add_trace(trace_item_stock_by_warehouse)

        item_stock_by_warehouse_plot.update_layout(
            title=f"Grafik Inventaris Semua Produk",
            title_font_size=15,
            xaxis_title="Kode Item",
            yaxis_title="Stok",
            font=dict(
                family="Inter, sans-serif",
                size=12,
            ),
            height=400,
            margin=dict(l=20, r=20, t=35, b=20),
            legend=dict(orientation="h", yanchor="top", y=1.01, xanchor="left", x=0)
        )

        return mo.ui.plotly(item_stock_by_warehouse_plot)
    return itemStockGraphic, itemStockRecap


@app.cell
def _(itemStockGraphic, itemStockRecap, mo):
    mo.ui.tabs({
        "Rekap": itemStockRecap(),
        "Grafik": itemStockGraphic(),
    })
    return


@app.cell
def _(mo):
    item_code = mo.ui.text(
        label="Filter berdasarkan : ",
        placeholder="kode item ...",
    )

    mo.vstack(
        [item_code],
        justify="start"
    )
    return (item_code,)


@app.cell
def _(iposConnect, item_code, sales_invoice_details):
    item_code_fill = iposConnect.item().parts().byItemCode(item_code.value).load().to_pandas()
    item_code_support_forecast = sales_invoice_details.parts().byDaily().count().to_pandas() > 1
    return item_code_fill, item_code_support_forecast


@app.cell
def _(item_code, item_code_fill, mo):
    mo.stop(len(item_code_fill) > 0, mo.md(f"Berikut adalah <b>rasio & total pendapatan</b> berdasarkan kontribusi <b>harga jual</b> pada item <b>{item_code.value}</b>."))
    return


@app.cell
def _(item_code, item_code_fill, mo, sales_invoice_details):
    if len(item_code_fill) > 0:
        revenue_by_sell_price_table = (
            sales_invoice_details.parts().byItemCode(item_code.value).revenueByItemPrice()
            .select("harga", "jumlah_item", "total_pendapatan", "rasio_pendapatan")
        )

        mo.stop(len(item_code_fill) > 0, mo.ui.table(revenue_by_sell_price_table, selection=None))
    return


@app.cell
def _(
    item_code,
    item_code_fill,
    item_code_support_forecast,
    item_stock,
    mo,
    sales_invoice_details,
):
    step = 3
    prespective_by_stock_predict = ""

    if len(item_code_fill) > 0 and item_code_support_forecast:
        sales_predictions = (
            sales_invoice_details.forcast(item_kode=item_code.value)
                .prepare(target='jumlah_item')
                .fit()
        )

        sales_prediction_results = sales_predictions.predict(step=step)

        item_stock_by_item_code = (
            item_stock.parts()
                .byItemCode(item_code.value)
                .load().select("stok")
                .to_pandas().astype("float").values.item()
        )

        mean_stock_predict = sales_prediction_results.pred.mean()
        out_of_stock = mean_stock_predict - item_stock_by_item_code

        if item_stock_by_item_code < mean_stock_predict:
            prespective_by_stock_predict = f"<b>Hasil prediksi</b> menunjukan bahwa dibutuhkan <b>{int(out_of_stock)} stock</b> lagi untuk <b>{item_code.value}</b> sehingga memenuhi target dalam <b>{step} hari</b> kedepan."
        else:
            prespective_by_stock_predict = f"<b>Hasil prediksi</b> menunjukan bahwa jumlah stok cukup untuk target <b>{step} hari</b> kedepan."

    mo.md(prespective_by_stock_predict)
    return sales_prediction_results, sales_predictions


@app.cell
def _(item_code, item_code_fill, item_code_support_forecast, mo):
    mo.stop(len(item_code_fill) > 0 and item_code_support_forecast is False, mo.md(f"Data deret waktu pada <b>{item_code.value}</b> tidak memenuhi untuk dilakukan prediski."))
    return


@app.cell
def _(
    go,
    item_code,
    item_code_fill,
    item_code_support_forecast,
    mo,
    sales_prediction_results,
    sales_predictions,
):
    if len(item_code_fill) > 0 and item_code_support_forecast:
        sales_forecast_plot = go.Figure()

        tracesales_forecast1 = go.Scatter(x=sales_predictions.df.index, y=sales_predictions.df["jumlah_item"], name="train", mode="lines")
        tracesales_forecast2 = go.Scatter(x=sales_prediction_results.index, y=sales_prediction_results["pred"], name="prediction", mode="lines")
        sales_forecast_plot.add_trace(tracesales_forecast1)
        sales_forecast_plot.add_trace(tracesales_forecast2)

        sales_forecast_plot.update_layout(
            title=f"Grafik prediksi penjualan item {item_code.value} di semua kantor/gudang",
            title_font_size=15,
            xaxis_title="Tanggal",
            yaxis_title="Total Penjualan",
            font=dict(
                family="Inter, sans-serif",
                size=12,
            ),
            height=400,
            margin=dict(l=20, r=20, t=35, b=20),
            legend=dict(orientation="h", yanchor="top", y=1.01, xanchor="left", x=0)
        )
    else:
        sales_forecast_plot = None

    mo.ui.plotly(sales_forecast_plot) if sales_forecast_plot else mo.md("Input <b>kode item</b> untuk prediksi <b>perkiraan stok</b> selanjutnya.")
    return


if __name__ == "__main__":
    app.run()
