import pyqtgraph as pg
import requests
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QInputDialog, QMessageBox

import fn_api
from UserInterfaces import filesave_widget, note_editor, updates_in_prices
from DBConnection import DBConnection
from UserInterfaces.company_info_widget_ui import Ui_Form
from file_exporter import FileWriter

# цвета для вывода прироста или убытка в акциях на экране
# первым элементом является красный цвет для убытка
# вторым элементом - зелёный цвет для прироста
DIFF_COLORS = ['#FF0000', '#32CD32']

# иконки для обычных и избранных компаний
STAR = ['unstar', 'yellow_star']


class NoteEditorWidget(QWidget, note_editor.Ui_Form):
    def __init__(self, parent):
        """
        Окно(виджет) для редактирования заметок у избранных компаний.

        :param parent: Класс, вызывающего виджета, для работы с его элементами, функциями и переменными.
        :type parent: QWidget
        """
        super(NoteEditorWidget, self).__init__()
        self.setupUi(self)
        # сохраняем класс родителя и текущий тикер(англ. ticker, symbol)
        # тикер - это специальный идентификатор компаний на бирже. Для каждой биржи он уникален.
        self.parent_widget = parent
        self.symbol = self.parent_widget.symbol.text()
        # получаем текущую заметку из базы данных и выводим её на экран
        self.initial = self.parent_widget.db.get_note_text(self.symbol)
        # создаём пустую переменную message_exit
        # в неё позже будем записывать ответ пользователя на подтверждение выхода
        self.message_exit = None
        self.initUi()

    def initUi(self):
        self.note_text.setText(self.initial)
        # соединяем сигналы кнопок с соответствующими слотами
        self.button_cancel.clicked.connect(self.close)
        self.button_save.clicked.connect(self.save_note)

    def save_note(self):
        # если измененная заметка такая же, как исходная заметка, то не имеет смысла её заменять в БД
        # в ином случае данные БД обновляются на новые, а окно закрывается
        if self.note_text.text() != self.initial:
            self.parent_widget.db.edit_note_text(self.parent_widget.symbol.text(),
                                                 self.initial, self.note_text.text())
            self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # если closeEvent вызвала кнопка закрытия окна, то self.sender вернёт None
        # т.к. объект None не имеет метода .text(), будет возвращена ошибка
        # чтобы этого избежать, использован оператор or
        # если self.sender вернёт None, то будет выбран self.button_cancel
        if (self.sender() or self.button_cancel).text() == 'Сохранить'\
                or self.note_text.text() == self.initial:
            # если условия выполняются, пропускаем окно подтверждения
            self.message_exit = QMessageBox.Yes
        else:
            # в ином случае просим у пользователя подтверждения
            self.message_exit = QMessageBox.question(self, 'Подтверждение выхода',
                                                     'Вы точно хотите выйти без сохранения?',
                                                     QMessageBox.Yes | QMessageBox.No)
        # если выход подтверждён(выбран вариант 'Yes'), закрываем данный виджет
        # иначе игнорируем closeEvent
        if QMessageBox.Yes == self.message_exit:
            super(NoteEditorWidget, self).closeEvent(a0)
        else:
            a0.ignore()


class UpdatesInPricesWidget(QWidget, updates_in_prices.Ui_Form):
    def __init__(self, parent_w, date, diff_c, diff_o, diff_h, diff_l):
        """
        Окно(виджет) для вывода изменений в цене.

        :param parent_w: Класс родителя
        :type parent_w: QWidget
        :param date: Дата прошлого обновления цен
        :type date: datetime.date
        :param diff_c: Изменения в close цене
        :type diff_c: float
        :param diff_o: Изменения в open цене
        :type diff_o: float
        :param diff_h: Изменения в high цене
        :type diff_h: float
        :param diff_l: Изменения в low цене
        :type diff_l: float
        """
        super(UpdatesInPricesWidget, self).__init__()
        self.setupUi(self)
        # сохраняем всю новую информацию
        self.parent_w = parent_w    # класс родителя
        self.date = date            # дата обновления данных, с которыми сравниваем обновленные данные
        self.diff_c = diff_c        # разница в close цене
        self.diff_o = diff_o        # разница в open цене
        self.diff_h = diff_h        # разница в high цене
        self.diff_l = diff_l        # разница в low цене
        self.initUi()

    def initUi(self):
        # выводим всю информацию на экран(передаём информацию в каждый label)
        self.ticker.setText(self.parent_w.symbol.text())
        self.name.setText(self.parent_w.name.text())
        self.lb_date.setText(str(self.date))
        self.lb_close.setText(str(self.diff_c))
        self.lb_open.setText(str(self.diff_o))
        self.lb_high.setText(str(self.diff_h))
        self.lb_low.setText(str(self.diff_l))

        # разукрашиваем эти label в зависимости от того, как изменилась цена 🧚
        for i in range(4):
            # получаем label, в котором указана цена, и форматируем информацию
            item = self.gridLayout.itemAtPosition(i + 1, 1).widget()
            item.setText('%.2f' % float(item.text()))

            # проверяем, как изменилась цена:
            #   если значение изменения цены больше 0, то ставим зелёный цвет текста
            #   если значение изменения цены меньше 0, то ставим красный цвет текста
            #   если цена не изменилась, то цвет текста остаётся чёрным
            diff = float(item.text())
            item.setText(('+' if diff > 0 else '') + str(diff))
            if diff == 0:
                item.setStyleSheet('color: #000')
            else:
                item.setStyleSheet('color: ' + DIFF_COLORS[diff > 0])


class FileSaveWidget(QWidget, filesave_widget.Ui_Form):
    def __init__(self, ticker, name, data, db):
        """
        Окно(виджет) для сохранения информации о данной компании.

        :param ticker: Тикер компании, информацию которой надо сохранить
        :type ticker: str
        :param name: Название этой компании
        :type name: str
        :param data: Данные о ценах из графика
        :type data: dict
        :param db: DBConnection
        :type db: DBConnection
        """
        super(FileSaveWidget, self).__init__()
        self.setupUi(self)
        # сохраняем переменные
        self.ticker = ticker
        self.name = name
        self.data = data
        self.db = db
        # создаём пустую переменную message_exit
        # в неё позже будем записывать ответ пользователя на подтверждение выхода
        self.message_exit = None
        # соединяем сигналы с соответствующими им слотами
        self.cancel.clicked.connect(self.close)
        self.save_excel.clicked.connect(self.import_excel)
        self.save_csv.clicked.connect(self.import_csv)
        # показываем либо предыдущее, либо дефолтное название файла
        self.filename.setText(db.get_filename(ticker))

    def import_excel(self):
        # если поле ввода пустое, предупреждаем пользователя
        # в ином случае сохраняем информацию в файл с данным названием и расширением .xlsx
        # и закрываем данное окно
        if not (filename := self.filename.text()):
            QMessageBox.critical(self, 'Неверное название файла', 'Название файла пустое.')
        else:
            FileWriter.import_excel(filename, self.ticker, self.name, self.data)
            self.close()

    def import_csv(self):
        # если поле ввода пустое, предупреждаем пользователя
        # в ином случае сохраняем информацию в файл с данным названием и расширением .csv
        # и закрываем данное окно
        if not (filename := self.filename.text()):
            QMessageBox.critical(self, 'Неверное название файла', 'Название файла пустое.')
        else:
            FileWriter.import_csv(filename, self.ticker, self.name, self.data)
            self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # если поле ввода не пустое, то записываем новое название файла в БД
        if filename := self.filename.text():
            self.db.update_set_filename(self.ticker, filename)
        if 'Сохранить' in (self.sender() or self.cancel).text()\
                or not filename:
            # если была нажата любая из кнопок для сохранения
            # или была нажата кнопка отмены, но поле ввода пустое
            # то пропускаем запрос подтверждения выхода
            self.message_exit = QMessageBox.Yes
        else:
            # в ином случае спрашиваем у пользователя подтверждение
            self.message_exit = QMessageBox.question(self, 'Подтверждение выхода',
                                                     'Вы точно хотите выйти без сохранения?',
                                                     QMessageBox.Yes | QMessageBox.No)
        # если пользователь подтвердил выход без сохранения, закрываем окно
        # в ином случае closeEvent игнорируется
        if QMessageBox.Yes == self.message_exit:
            super(FileSaveWidget, self).closeEvent(a0)
        else:
            a0.ignore()


class LogoThread(QThread):
    # сигнал для уведомления об окончании загрузки и передачи изображения
    logo = pyqtSignal(bytes)

    def __init__(self, symbol, url):
        """
        Отдельный поток для загрузки логотипа данной компании

        :param symbol: Тикер компании
        :type symbol: str
        :param url: Ссылка на логотип
        :type url: str
        """
        super(LogoThread, self).__init__()
        # сохраняем переменные
        self.symbol = symbol
        self.url = url

    def run(self) -> None:
        # загружаем логотип и передаём его с помощью сигнала
        self.logo.emit(requests.get(self.url).content)


class CompanyInfoWidget(QWidget, Ui_Form):
    def __init__(self, api, symbol, db):
        """
        Виджет, показывающий всю информацию о выбранной компании

        :param api: fn_api.Connection для обращения к API
        :type api: fn_api.Connection
        :param symbol: Тикер компании
        :type symbol: str
        :param db: DBConnection дял работы с БД
        :type db: DBConnection
        """
        super().__init__()
        self.setupUi(self)
        # сохраняем переменные
        self.api = api
        self.db = db
        # пустые переменные, в которые позже запишем значения
        self.thread = None
        self.status = False
        self.resp = None
        self.update_widget = None
        self.file_save_widget = None
        self.message_delete = None
        self.editor_widget = None
        # расставляем кнопкам иконки и подсказки, а также соединяем сигналы и слоты
        self.download.setIcon(QIcon('src/icons/download.png'))
        self.download.clicked.connect(self.download_info)
        self.download.setToolTip('Импорт данных')
        self.open_note.setIcon(QIcon('src/icons/note.png'))
        self.open_note.clicked.connect(self.show_note)
        self.open_note.setToolTip('Показать заметку')
        self.set_chosen.clicked.connect(self.add_remove_chosen)
        # создаём и готовим виджет для работы с графиком
        self.view = pg.PlotWidget()
        self.curve = self.view.plot(name="Stocks")
        # обновляем всю информацию с помощью self.replaceInfo
        self.replaceInfo(symbol)
        self.widget_graph.layout().addWidget(self.view)

    def replaceInfo(self, symbol: str):
        # если в списке выбрана та же компания, которая уже обработана, то ничего не обновляем
        if symbol == self.symbol.text():
            return
        # если было возбуждено исключение APIError, выставляем везде значения null и скрываем кнопки
        if symbol == 'null':
            self.symbol.setText('NULL')
            self.name.setText('NULL')
            self.p_close.setText('NULL')
            self.difference.setText('NULL')
            self.difference.hide()
            self.p_open.setText('NULL')
            self.p_high.setText('NULL')
            self.p_low.setText('NULL')
            self.ipo_date.setText('NULL')
            self.website.setText('NULL')
            self.webView.load(QUrl('about:blank'))
            self.curve.setData([0])
            self.logo.clear()
            if not self.download.isHidden():
                self.open_note.hide()
                self.set_chosen.hide()
                self.download.hide()
            return
        # если кнопки скрыты, а исключение APIError не было возбуждено, показываем кнопки
        if self.download.isHidden():
            self.set_chosen.show()
            self.download.show()

        # получаем всю нужную нам информацию
        profile, self.resp, latest_info = self.api.all_company_info(symbol)
        # получаем из базы данных информацию о последнем просмотре о данной компании
        prev_info = self.db.get_checked(symbol)
        # выводим тикер и название данной компании
        self.symbol.setText(symbol)
        self.name.setText(profile.get('name'))
        # очищаем прошлый логотип и загружаем логотип другой компании, если он есть
        self.logo.clear()
        if logo_url := profile.get('logo'):
            self.thread = LogoThread(symbol, logo_url)
            self.thread.logo.connect(self.set_logo)
            self.thread.start()

        # проверяем, находится ли данная компания в списке избранных
        self.status = self.db.get_chosen_status(symbol)
        # если да, то показываем кнопку для редактирования заметки
        # если нет, то скрываем кнопку для редактирования заметки
        # в обоих случаях меняем подсказку для кнопки
        if self.status:
            self.open_note.show()
            self.set_chosen.setToolTip('Убрать из избранного')
        else:
            self.open_note.hide()
            self.set_chosen.setToolTip('Добавить в избранное')
        # меняем иконку для кнопки в зависимости от self.status
        self.set_chosen.setIcon(QIcon(self.chosen_icon_path()))

        # если данные отсутствуют, выставляем нулевые значения
        # если всё нормально, вносим полученные данные
        if 'no_data' in self.resp.get('s', 'none'):
            self.curve.setData([0])
            diff = 0
        else:
            self.curve.setData(self.resp.get('c'))
            diff = latest_info.get('d', 0)
        # приводим данные в вид '±diff', где diff - изменения в цене
        self.difference.setText(('+' if diff > 0 else '') + '%.2f' % diff)

        # разукрашиваем текст в зависимости от значений diff
        # diff > 0 - зелёный, diff < 0 - красный
        # если diff = 0, то разница не выводится на экран
        if diff == 0:
            self.difference.setText('')
        else:
            if self.difference.isHidden():
                self.difference.show()
            self.difference.setStyleSheet('color: ' + DIFF_COLORS[diff > 0])

        # получаем новейшие цены акций
        p_close = latest_info.get('c', 0)
        p_open = latest_info.get('o', 0)
        p_high = latest_info.get('h', 0)
        p_low = latest_info.get('l', 0)
        # заполняем имеющимися данными все label и форматируем их, если надо
        self.ipo_date.setText(profile.get('ipo', 'not found'))
        self.website.setText(profile.get('weburl', 'not found'))
        self.p_close.setText('%.2f' % p_close)
        self.p_open.setText('%.2f' % p_open)
        self.p_high.setText('%.2f' % p_high)
        self.p_low.setText('%.2f' % p_low)

        # если данную компанию пользователь уже смотрел
        # и дата просмотра не равна сегодняшней дате
        # то показываем пользователю разницу в ценах по сравнению с прошлыми данными
        if prev_info[0]:
            date, close, op, high, low = prev_info
            diff_c = p_close - close
            diff_o = p_open - op
            diff_h = p_high - high
            diff_l = p_low - low
            self.update_widget = UpdatesInPricesWidget(self, date, diff_c, diff_o, diff_h, diff_l)
            self.update_widget.show()
        # загружаем сайт компании, если он есть
        # если его нет, то будет загружена пустая страница
        self.webView.load(QUrl(profile.get('weburl', 'about:blank')))
        # обновляем данные о просмотре данной компании
        self.update_db_checked(latest_info)

    @pyqtSlot(bytes)
    def set_logo(self, data):
        # если логотип загружен для другой компании, ничего не обновляется
        if self.sender().symbol != self.symbol.text():
            return
        # если всё нормально, заносим логотип в pixmap
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        # масштабируем иконку
        w, h = pixmap.size().width(), pixmap.size().height()
        coefficient = min(w, h) / 32
        try:
            self.logo.setPixmap(pixmap.scaled(w // coefficient, h // coefficient))
        except ZeroDivisionError:
            self.logo.clear()
        # удаляем этот поток
        self.thread.deleteLater()
        self.thread = None

    def chosen_icon_path(self):
        # возвращаем путь к подходящей иконке
        return f'src/icons/{STAR[self.status]}.png'

    def download_info(self):
        # показываем окно для сохранения данных в файл
        self.file_save_widget = FileSaveWidget(self.symbol.text(), self.name.text(),
                                               self.resp, self.db)
        self.file_save_widget.show()

    def update_db_checked(self, info: dict):
        # сохраняем информацию о последнем просмотре в БД
        self.db.edit_checked(self.symbol.text(), info.get('c', 0),
                             info.get('o', 0), info.get('h', 0), info.get('l', 0))

    def add_remove_chosen(self):
        if self.status:
            # если данная компания уже в списке избранных
            # то просим подтвердить удаление и удаляем, если ответ положительный
            self.message_delete = QMessageBox.question(self, 'Подтверждение удаления',
                                                       f'Удалить {self.symbol.text()} из избранных?',
                                                       QMessageBox.Yes | QMessageBox.No)
            if QMessageBox.Yes == self.message_delete:
                self.db.remove_from_chosen(self.symbol.text())
                # меняем иконку на противоположную
                self.status = not self.status
                self.set_chosen.setIcon(QIcon(self.chosen_icon_path()))
                self.open_note.hide()
        else:
            # если компании нет в списке избранных
            # то спрашиваем, какую заметку добавить, и добавляем компанию в избранные
            text, ok_pressed = QInputDialog.getText(self, 'Введите заметку',
                                                    'Введите заметку к данным акциям')
            if ok_pressed:
                self.db.add_to_chosen(self.symbol.text(), self.name.text(), text)
                self.open_note.show()
                # меняем иконку на противоположную
                self.status = not self.status
                self.set_chosen.setIcon(QIcon(self.chosen_icon_path()))
        # обновляем список компаний в родительском окне
        self.nativeParentWidget().update_info()

    def show_note(self):
        # показываем редактор заметки компании
        self.editor_widget = NoteEditorWidget(self)
        self.editor_widget.show()
