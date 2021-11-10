import sqlite3
from datetime import datetime


class DBConnection:
    def __init__(self, name):
        """
        Создаёт соединение с БД

        :param name: название файла
        :type name: str
        """
        # создаёт соединение с базой данных
        self.con = sqlite3.connect(name)

    def get_chosen_list(self):
        """
        Возвращает список избранных компаний (их тикеры и названия).

        :return: список избранных компаний
        :rtype: list
        """
        # собираем информацию об избранных из БД
        cur = self.con.cursor()
        chosen_list = cur.execute('SELECT ticker, name FROM chosen').fetchall()
        return chosen_list

    def get_chosen_status(self, ticker) -> bool:
        """
        Возвращает состояние(bool), есть ли данный ticker в списке избранных

        :param ticker: Тикер компании
        :type ticker: str
        :return: Статус
        :rtype: bool
        """
        # проверяем количество строк в таблице избранных компаний с нужным нам тикером
        cur = self.con.cursor()
        status = cur.execute('SELECT COUNT(*) FROM chosen\n'
                             'WHERE ticker = ?', (ticker, )).fetchone()[0]
        # bool(0) - это False, bool(1) - это True
        return bool(status)

    def remove_from_chosen(self, ticker):
        """
        Удаляет компанию из избранных

        :param ticker: Тикер компании
        :type ticker: str
        """
        # выполняем запрос удаления строки с нужным нам тикером
        cur = self.con.cursor()
        cur.execute('DELETE FROM chosen WHERE ticker = ?', (ticker, ))
        # обновляем таблицы БД
        self.con.commit()

    def add_to_chosen(self, ticker, name, text):
        """
        Добавляет компанию в избранные

        :param ticker: Тикер компании
        :type ticker: str
        :param name: Название компании
        :type name: str
        :param text: Текст заметки
        :type text: str
        """
        # получаем id заметки с данным текстом
        # если такой заметки нет, будет создана новая заметка
        note_id = self.create_note(text)
        # добавляем новую компанию в таблицу chosen
        cur = self.con.cursor()
        cur.execute('INSERT INTO chosen VALUES(?, ?, ?)', (ticker, name, note_id))
        # обновляем таблицы БД
        self.con.commit()

    def create_note(self, text):
        """
        Создаёт новую заметку и возвращает её id, либо возвращает id уже существующей

        :param text: Текст заметки
        :type text: str
        :return: noteId
        :rtype: int
        """
        cur = self.con.cursor()
        # проверяем, есть ли заметка с таким текстом
        # если есть, будет возвращен id существующей заметки
        if not (note_id := cur.execute('SELECT id FROM notes\n'
                                       'WHERE text = ?', (text, )).fetchone()):
            # если не найдено заметки с таким текстом, создаётся новая
            cur.execute('INSERT INTO notes(text) VALUES(?)', (text, ))
            # обновляем таблицы БД
            self.con.commit()
            # получаем новый id
            note_id = cur.execute('SELECT id FROM notes\n'
                                  'WHERE text = ?', (text, )).fetchone()
        return note_id[0]

    def get_note_text(self, ticker):
        """
        Возвращает текст заметки по тикеру

        :param ticker: Тикер компании
        :type ticker: str
        :return: Текст заметки
        :rtype: str
        """
        cur = self.con.cursor()
        # ищем заметку с данным noteId и берём у неё текст
        text = cur.execute('SELECT text FROM notes\n'
                           'WHERE id = (SELECT noteId FROM chosen\n'
                           'WHERE ticker = ?)', (ticker, )).fetchone()[0]
        return text

    def edit_note_text(self, ticker, prev, curr):
        """
        Редактирует текст заметки у избранной компании

        :param ticker: Тикер компании
        :type ticker: str
        :param prev: Прошлый текст заметки
        :type prev: str
        :param curr: Новый текст заметки
        :type curr: str
        """
        cur = self.con.cursor()
        # ищем заметки с данными текстами (с прошлым и новым текстами)
        note_id = cur.execute('SELECT id FROM notes\n'
                              'WHERE text = ?', (prev, )).fetchone()[0]
        new_note_id = cur.execute('SELECT id FROM notes\n'
                                  'WHERE text = ?', (curr, )).fetchone()

        # если уже существует заметка с новым текстом, то заменяем noteId компании на id заметки
        # если прошлая заметка используется и для других компаний
        #   то создаём новую заметку и присваиваем её компании
        # в остальных случаях, меняем текст первоначальной заметки
        if new_note_id:
            cur.execute('UPDATE chosen SET noteId = ?\n'
                        'WHERE ticker = ?', (new_note_id[0], ticker))
        elif cur.execute('SELECT COUNT(*) FROM chosen\n'
                         'WHERE noteId = ?', (note_id, )).fetchone()[0] > 1:
            new_note_id = self.create_note(curr)
            cur.execute('UPDATE chosen SET noteId = ?\n'
                        'WHERE ticker = ?', (new_note_id, ticker))
        else:
            cur.execute('UPDATE notes SET text = ? WHERE id = ?', (curr, note_id))
        # обновляем таблицы БД
        self.con.commit()

    def edit_checked(self, ticker, cl, o, h, low):
        """
        Обновляет информацию о просмотре компании

        :param ticker: Тикер компании
        :type ticker: str
        :param cl: close цена
        :type cl: float
        :param o: open
        :type o: float
        :param h: high
        :type h: float
        :param low: low
        :type low: float
        """
        # получаем предыдущую дату просмотра
        cur = self.con.cursor()
        prev_date = cur.execute('SELECT date FROM checked WHERE ticker = ?',
                                (ticker, )).fetchone()
        # сегодняшняя дата
        curr_date = datetime.now().date()
        # кортеж параметров для SQL-запроса
        db_data = (curr_date, cl, o, h, low, ticker)
        # если просмотр до этого уже был и дата прошлого просмотра не сегодняшняя
        #   обновляем информацию
        # в ином случае создаём новую строку в таблице
        if prev_date:
            if prev_date[0] != curr_date:
                cur.execute('UPDATE checked SET date = ?, close = ?, open = ?, '
                            'high = ?, low = ? WHERE ticker = ?', db_data)
        else:
            cur.execute('INSERT INTO checked(date, close, open, high, low, ticker) '
                        'VALUES(?, ?, ?, ?, ?, ?)', db_data)
        # обновляем таблицы БД
        self.con.commit()

    def get_checked(self, ticker):
        """
        Возвращает информацию о прошлом просмотре

        :param ticker: Тикер компании
        :type ticker: str
        :return: Информацию о прошлом просмотре, если такой есть
        :rtype: tuple
        """
        # получаем дату прошлого просмотра
        cur = self.con.cursor()
        prev_date = (cur.execute('SELECT date FROM checked WHERE ticker = ?',
                                 (ticker, )).fetchone() or [''])[0]
        # если просмотр до этого уже был и дата прошлого просмотра не сегодняшняя
        #   возвращаем прошлую дату и цены акций (close, open, high, low)
        # в ином случае сообщаем, что просмотра не было (возвращаем кортеж из None)
        if prev_date:
            prev_date = datetime.fromisoformat(prev_date).date()
            curr_date = datetime.now().date()
            if prev_date != curr_date:
                cl, o, h, low = cur.execute('SELECT close, open, high, low FROM checked\n'
                                            'WHERE ticker = ?', (ticker, )).fetchone()
                return prev_date, cl, o, h, low
        return None,

    def get_filename(self, ticker):
        """
        Возвращает имя файла для импорта

        :param ticker: Тикер компании
        :type ticker: str
        :return: Название файла
        :rtype: str
        """
        # ищем в БД название файла по данному тикеру
        cur = self.con.cursor()
        filename = cur.execute('SELECT filename FROM filenames\n'
                               'WHERE ticker = ?', (ticker, )).fetchone()
        # если название найдено, возвращаем его
        if filename:
            return filename[0]
        # иначе возвращаем название, сгенерированное по шаблону
        return f'{ticker}_import'

    def update_set_filename(self, ticker, new_filename):
        """
        Обновляем название файла в БД

        :param ticker: Тикер компании
        :type ticker: str
        :param new_filename: Новое название файла
        :type new_filename: str
        """
        # проверяем, есть ли в БД строчка с таким тикером
        cur = self.con.cursor()
        filename_status = cur.execute('SELECT COUNT(*) FROM filenames\n'
                                      'WHERE ticker = ?', (ticker, )).fetchone()[0]
        if filename_status:
            # если есть, обновляем её название файла
            cur.execute('UPDATE filenames SET filename = ?\n'
                        'WHERE ticker = ?', (new_filename, ticker))
        else:
            # иначе создаём новую строчку с таким названием
            cur.execute('INSERT INTO filenames VALUES(?, ?)', (ticker, new_filename))
        # обновляем таблицы БД
        self.con.commit()

    def on_close(self):
        """
        Закрывает соединение
        """
        # закрываем соединение с БД
        self.con.close()
