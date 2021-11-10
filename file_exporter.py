import csv

import xlsxwriter as xw
from datetime import datetime


class FileWriter:
    @staticmethod
    def import_excel(filename, ticker, name, data):
        """
        Сохраняет информацию в Excel-файле

        :param filename: Название файла без расширения
        :type filename: str
        :param ticker: Тикер компании
        :type ticker: str
        :param name: Название компании
        :type name: str
        :param data: Даты и цены
        :type data: dict
        """
        # создаём workbook для работы с excel-файлом
        workbook = xw.Workbook(f'{filename}.xlsx')
        worksheet = workbook.add_worksheet()
        row = 0

        # записываем тикер и название
        names = [('Тикер', ticker), ('Название', name)]
        for row, (item, value) in enumerate(names):
            worksheet.write(row, 0, item)
            worksheet.write(row, 1, value)

        # записываем заголовки
        row += 2
        names = ['Дата', 'close', 'open', 'high', 'low']
        for col, name in enumerate(names):
            worksheet.write(row, col, name)

        # записываем сами данные
        row += 1
        for new_row, date in enumerate(data.get('t', [])):
            worksheet.write(row + new_row, 0, str(datetime.utcfromtimestamp(float(date)).date()))
        for col, price_list in enumerate([data.get('c', []), data.get('o', []),
                                          data.get('h', []), data.get('l', [])]):
            for new_row, price in enumerate(price_list):
                worksheet.write(row + new_row, col + 1, price)

        # создаём график для close цены
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({
            'categories': f'=Sheet1!A5:A{5 + len(data.get("t", []))}',
            'values': f'=Sheet1!B5:B{5 + len(data.get("c", []))}',
            'marker': {'type': 'diamond', 'size': 3},
            'name': 'Close prices'
        })
        chart.set_x_axis({'name': 'дата'})
        chart.set_y_axis({'name': 'close price'})
        worksheet.insert_chart('F5', chart)

        # закрываем workbook
        workbook.close()

    @staticmethod
    def import_csv(filename, ticker, name, data):
        """
        Сохраняет информацию в CSV-файле

        :param filename:
        :type filename:
        :param ticker:
        :type ticker:
        :param name:
        :type name:
        :param data:
        :type data:
        :return:
        :rtype:
        """
        # создаём список словарей с данными для записи
        data_to_write = [{
            'ticker': ticker,
            'name': name,
            'date': datetime.utcfromtimestamp(float(date)).date()
        } for date in data.get('t', [])]
        # пополняем словари в списке ценами
        names = ['close', 'open', 'high', 'low']
        for name, price_list in zip(names, [data.get('c', []), data.get('o', []),
                                            data.get('h', []), data.get('l', [])]):
            for row, price in enumerate(price_list):
                data_to_write[row].update({name: price})
        # запись в CSV-файл
        with open(f'{filename}.csv', mode='w', encoding='utf8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(data_to_write[0].keys()),
                                    delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for row in data_to_write:
                writer.writerow(row)
