import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget

import av_api
from company_info_widget_ui import Ui_Form


class CompanyInfoWidget(QWidget, Ui_Form):
    def __init__(self, api: av_api.Connection, symbol: str, name: str):
        super().__init__()
        self.setupUi(self)
        self.api = api
        self.view = pg.PlotWidget()
        self.curve = self.view.plot(name="Stocks")
        self.replaceInfo(symbol, name)
        self.widget_graph.layout().addWidget(self.view)

    def replaceInfo(self, symbol: str, name: str):
        resp = self.api.time_series_monthly(symbol).get('Monthly Time Series', {})
        self.symbol.setText(symbol)
        self.name.setText(name)
        prices = list()
        for date, val in resp.items():
            prices.append(float(val.get('4. close')))
        first_item = list(list(resp.values())[0].values())
        self.curve.setData(prices)
        self.p_close.setText(str(prices[0]))
        self.p_open.setText(first_item[0])
        self.p_high.setText(first_item[1])
        self.p_low.setText(first_item[2])
