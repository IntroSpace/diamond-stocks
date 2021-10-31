import csv

import requests
from .api_key import API_KEY
from .extensions import APILimitError

from functools import wraps

# "главная" ссылка, с помощью которой будем обращаться к AlphaVantage API
API_URL = 'https://www.alphavantage.co/query'


# декоратор для предупреждения о лимите запросов к API
# используется только для методов, которым необходимо обращение к API
def API_call(func):
    @wraps(func)
    def handler(self: object, *args: list, **kwargs: dict) -> dict:
        # если встречается неприятное сообщение от API об ограничении, возбуждаем свою ошибку
        if 'Thank' in (response := func(self, *args, **kwargs)).get('Note', ''):
            raise APILimitError('Извините, обращаться к серверу можно только '
                                '5 раз в минуту\nи максимум 500 раз в день')
        # в противном случае передаем данные
        return response
    return handler


class Connection:
    @API_call
    def time_series_intraday(self, symbol: str, interval: str, time_slice: str = None) -> dict:
        """
        Возвращает внутридневные временные ряды указанного капитала с определенным интервалом.
        """
        # Задаём параметры для запроса
        data = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'apikey': API_KEY
        }
        if time_slice:
            data.update({
                'function': 'TIME_SERIES_INTRADAY_EXTENDED',
                'slice': time_slice
            })
        # Получаем json-данные
        resp = requests.get(API_URL, params=data)
        # При ненулевом time_slice необходимо парсить csv
        if time_slice:
            return {
                'Symbol': symbol,
                f'Time Series ({interval})': list(csv.DictReader(
                    resp.content.decode('utf-8').splitlines(), delimiter=','))
            }
        return resp.json()

    @API_call
    def time_series_monthly(self, symbol: str) -> dict:
        """
        Возвращает данные об акциях компании помесячно.
        """
        # Задаём параметры для запроса
        data = {
            'function': 'TIME_SERIES_MONTHLY',
            'symbol': symbol,
            'apikey': API_KEY
        }
        # Получаем json-данные
        resp = requests.get(API_URL, params=data)
        return resp.json()

    @API_call
    def company_overview(self, symbol: str):
        """
        Возвращает все данные о компании по его тикеру.
        """
        # Задаём параметры для запроса
        data = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': API_KEY
        }
        # Получаем json-данные
        resp = requests.get(API_URL, params=data)
        return resp.json()

    @API_call
    def symbol_search(self, keywords: str):
        # Задаём параметры для запроса
        data = {
            'function': 'SYMBOL_SEARCH',
            'keywords': keywords,
            'apikey': API_KEY
        }
        # Получаем json-данные
        resp = requests.get(API_URL, params=data)
        return resp.json()
