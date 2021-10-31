import sys

from PyQt5.QtCore import Qt

import search_widget
import error_info
from av_api import Connection
from av_api.extensions import APILimitError

from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QButtonGroup
from PyQt5 import QtGui

from company_info_widget import CompanyInfoWidget
from main_widget import Ui_Form


class SearchResultWidget(QWidget, search_widget.Ui_Form):
    def __init__(self, request, parent):
        super(SearchResultWidget, self).__init__()
        self.setupUi(self)
        self.parent_widget = parent
        self.results_group = QButtonGroup()
        self.results_group.buttonClicked.connect(self.open_company_info)
        self.request = request
        self.initUi()

    def initUi(self):
        self.label_request.setText(f'Результаты поиска по запросу '
                                   f'<i>{self.request}</i>')
        resp = self.parent_widget.api.symbol_search(self.request)
        for comp in resp.get('bestMatches'):
            symb = comp.get('1. symbol')
            name = comp.get('2. name')
            button = QPushButton(f'{name} ({symb})', self)
            button.ticker = symb
            button.company_name = name
            self.results_group.addButton(button)
            self.results.layout().addWidget(button)

    def open_company_info(self, item):
        self.parent_widget.open_company_info(item)
        self.close()


class ErrorWidget(QWidget, error_info.Ui_Form):
    def __init__(self, error):
        super(ErrorWidget, self).__init__()
        self.setupUi(self)
        self.error.setText(error)


class MainWidget(QWidget, Ui_Form):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.setupUi(self)
        self.list_of_rec = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOG': 'Alphabet Inc.',
            'LCID': 'Lucid Group Inc.',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'FB': 'Facebook Inc.',
            'NVDA': 'NVIDIA Corporation',
            'BABA': 'Alibaba Group',
            'V': 'Visa Inc.',
            'MA': 'Mastercard Incorporated',
            'HD': 'Home Depot Inc.',
            'DIS': 'Walt Disney Company',
            'ADBE': 'Adobe Inc.',
            'NFLX': 'Netflix Inc.',
            'BA': 'Boeing Company',
            'EADSF': 'Airbus SE',
            'YNDX': 'Yandex',
            'SSNLF': 'Samsung Electronics'
        }
        self.stocks_group = QButtonGroup()
        self.stocks_group.buttonClicked.connect(self.open_company_info)
        self.api = Connection()
        self.initUi()

    def initUi(self):
        search_icon = QtGui.QIcon('src/icons/loupe.png')
        self.ln_search.addAction(search_icon, QLineEdit.LeadingPosition)
        for i, val in self.list_of_rec.items():
            button = QPushButton(val, self)
            button.ticker = i
            button.company_name = val
            self.stocks_group.addButton(button)
            self.scrollAreaWidgetContents.layout().addWidget(button)

    def open_company_info(self, item):
        widget = self.layout().itemAt(1).widget()
        try:
            if not isinstance(widget, CompanyInfoWidget):
                self.graphs_widget = CompanyInfoWidget(self.api, item.ticker, item.company_name)
                self.layout().removeWidget(widget)
                widget.deleteLater()
                self.layout().addWidget(self.graphs_widget)
                self.horizontalLayout.setStretch(1, 3)
            else:
                widget.replaceInfo(item.ticker, item.company_name)
        except APILimitError as e:
            self.error_widget = ErrorWidget(str(e))
            self.error_widget.show()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() in [Qt.Key_Enter, Qt.Key_Return] and self.ln_search.hasFocus() \
                and (txt := self.ln_search.text()):
            self.results_widget = SearchResultWidget(txt, self)
            self.results_widget.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    ex.show()
    sys.exit(app.exec_())
