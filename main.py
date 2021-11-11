import sys

from UserInterfaces import search_widget
from DBConnection import DBConnection
from fn_api import Connection
from fn_api.extensions import APIError

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, \
    QButtonGroup, QMessageBox, QMainWindow
from PyQt5 import QtGui

from company_info_widget import CompanyInfoWidget
from UserInterfaces.main_window import Ui_MainWindow


class SearchResultWidget(QWidget, search_widget.Ui_Form):
    def __init__(self, request, parent):
        """
        Окно(виджет) для вывода результатов поиска

        :param request: Запрос для поиска
        :type request: str
        :param parent: Класс родителя
        :type parent: QObject
        """
        super(SearchResultWidget, self).__init__()
        self.setupUi(self)
        self.parent_widget = parent

        # группа кнопок для результатов поиска
        self.results_group = QButtonGroup()
        self.results_group.buttonClicked.connect(self.open_company_info)

        self.request = request
        self.initUi()

    def initUi(self):
        self.label_request.setText(f'Результаты поиска по запросу '
                                   f'<i>{self.request}</i>')
        # ищем компании, подходящие под запрос
        resp = self.parent_widget.api.symbol_search(self.request)
        result = resp.get('result')
        if not result:
            # если ничего не найдено, говорим пользователю, что ничего не найдено
            self.parent_widget.not_found()
            self.deleteLater()
            return
        # обрабатываем каждый запрос:
        #   создаём кнопку с тикером и названием каждой компании, подходящей под запрос
        #   добавляем нужные аттрибуты кнопке и добавляем готовую кнопку в нашу группу
        for comp in result:
            symb = comp.get('symbol')
            name = comp.get('description')
            button = QPushButton(f'{name} ({symb})', self)
            button.ticker = symb
            button.company_name = name
            self.results_group.addButton(button)
            self.results.layout().addWidget(button)

        self.show()

    def open_company_info(self, item):
        # при нажатии на одну из кнопок, показываем информацию на главном окне и закрываем виджет
        self.parent_widget.open_company_info(item)
        self.close()


class MainWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.setupUi(self)
        # список рекомендуемых компаний
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
            'YNDX': 'Yandex'
        }
        # группа кнопок для открытия информации о компаниях
        self.stocks_group = QButtonGroup()
        self.stocks_group.buttonClicked.connect(self.open_company_info)
        # создаём соединение api и db
        self.api = Connection()
        self.db = DBConnection('CompaniesAndNotesDB.db')
        # пустые переменные, в которые позже будут записаны значения
        self.graphs_widget = None
        self.error_widget = None
        self.results_widget = None
        self.initUi()

    def initUi(self):
        # ставим иконку для line_edit
        search_icon = QtGui.QIcon('src/icons/loupe.png')
        self.ln_search.addAction(search_icon, QLineEdit.LeadingPosition)
        # меняем стиль и ставим иконку с подсказкой для кнопки поиска
        self.button_search.setIcon(QtGui.QIcon('src/icons/loupe_white.png'))
        self.button_search.setStyleSheet('background-color: rgb(65, 60, 230); color: #FFF')
        self.button_search.clicked.connect(self.search_listener)
        self.button_search.setToolTip('Искать')
        # обновляем список избранных и рекоммендованных компаний
        self.update_info()

    def update_info(self):
        # очищаем списки от прошлых объектов
        for i in reversed(range(self.scrollAreaWidgetContents.layout().count())):
            self.scrollAreaWidgetContents.layout().itemAt(i).widget().deleteLater()
        for i in reversed(range(self.scrollAreaWidgetContents_2.layout().count())):
            self.scrollAreaWidgetContents_2.layout().itemAt(i).widget().deleteLater()
        # если избранные компании есть, добавляем их в список
        # если нет, скрываем список избранных
        chosen_list = self.db.get_chosen_list()
        if chosen_list:
            self.groupBox.show()
            for ticker, name in chosen_list:
                button = QPushButton(name, self)
                button.ticker = ticker
                self.stocks_group.addButton(button)
                self.scrollAreaWidgetContents_2.layout().addWidget(button)
        else:
            self.groupBox.hide()
        # проверяем, какие компании есть и в избранных, и в рекоммендованных
        tickers_from_chosen = [ticker for ticker, _ in chosen_list]
        for ticker, name in self.list_of_rec.items():
            if ticker not in tickers_from_chosen:
                button = QPushButton(name, self)
                button.ticker = ticker
                self.stocks_group.addButton(button)
                self.scrollAreaWidgetContents.layout().addWidget(button)
        # если список рекоммендованных пуст, скрываем
        # если всё нормально, показываем
        if self.scrollAreaWidgetContents.layout().count() > 0:
            self.groupBox_2.show()
        else:
            self.groupBox_2.hide()

    def open_company_info(self, item):
        # получаем виджет, который стоял до обновления информации
        widget = self.centralWidget().layout().itemAt(1).widget()
        try:
            # если этот виджет - это приветствие, ставим вместо него информацию о компании
            # если этот виджет - информация о компании, заменяем информацию в виджете на новую
            if not isinstance(widget, CompanyInfoWidget):
                self.graphs_widget = CompanyInfoWidget(self.api, item.ticker, self.db)
                self.graphs_widget.setParent(self)
                self.centralWidget().layout().removeWidget(widget)
                widget.deleteLater()
                self.centralWidget().layout().addWidget(self.graphs_widget)
                self.centralWidget().layout().setStretch(1, 2)
            else:
                widget.replaceInfo(item.ticker)
        except APIError as e:
            # если ошибка APIError, выставляем нулевые значения и показываем текст ошибки
            if isinstance(widget, CompanyInfoWidget):
                widget.replaceInfo('null')
            self.error_widget = QMessageBox.critical(self, 'Ограничения API', str(e))

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        # срабатывание Enter для line_edit
        if a0.key() in [Qt.Key_Enter, Qt.Key_Return] and self.ln_search.hasFocus():
            self.search_listener()

    def search_listener(self):
        self.statusBar().clearMessage()
        # показываем результаты по запросу
        txt = self.ln_search.text()
        if txt:
            self.results_widget = SearchResultWidget(txt, self)

    def not_found(self):
        # предупреждение, что по запросу ничего не найдено
        self.statusBar().showMessage(f'По запросу "{self.ln_search.text()}" ничего не найдено.')

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # закрываем соединения
        self.db.on_close()
        self.api.on_close()

        super(MainWidget, self).closeEvent(a0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    ex.show()
    sys.exit(app.exec_())
