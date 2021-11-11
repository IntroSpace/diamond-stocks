from .api_key import FINN_API_KEY
from .extensions import APIError

import calendar
import datetime

from functools import wraps

import requests
import aiohttp
import asyncio

# "главная" ссылка, с помощью которой будем обращаться к Finnhub API
API_URL = 'https://finnhub.io/api/v1/'


# декоратор для предупреждения о лимите запросов к API
# используется только для методов, которым необходимо обращение к API
def API_call(func):
    # functools.wraps необходим для сохранения описания функции
    @wraps(func)
    def handler(self: object, *args: list, **kwargs: dict) -> dict:
        # если встречается неприятное сообщение от API об ограничении, возбуждаем свою ошибку
        response = None
        try:
            response = func(self, *args, **kwargs)
        except APIError as e:
            if 'limit' in str(e):
                raise APIError('Извините, обращаться к серверу можно только 60 раз в минуту')
            elif 'don\'t have access' in str(e):
                raise APIError('Извините, бесплатное API ограничено. Данную компанию выбрать нельзя')
        # в противном случае передаем данные
        return response

    return handler


class Connection:
    def __init__(self):
        """
        Класс для быстрой работы с Finnhub API
        """
        # использовать requests.Session вместо обычного requests.get рекомендуется
        # для оптимизации и уменьшения затрат на закрытие соединения
        self.client = requests.Session()

    @API_call
    def symbol_search(self, query):
        """
        Возвращает подходящие под запрос акции.

        :param query: Запрос для поиска
        :type query: str
        :return: Список акций, подходящих под запрос
        :rtype: dict
        """
        return self.client.get(f'{API_URL}search?q={query}&token={FINN_API_KEY}').json()

    @staticmethod
    async def get_info(url):
        # функция для асинхронной работы
        # другое название 'корутина'
        async with aiohttp.ClientSession() as session:
            # получаем результат
            async with session.get(url) as response:
                json = await response.json()
            # в случае встречи ключа 'error' в ответе, возбуждаем ошибку
            if error := json.get('error', ''):
                raise APIError(error)
            # если всё отлично, возвращаем ответ сервера
            return json

    @API_call
    def all_company_info(self, symbol):
        """
        Возвращает все данные, нужные для отображения информации в CompanyInfoWidget.

        :param symbol: тикер, по которому будет произведён поиск информации
        :type symbol: str
        :return: основная информация, информация для графиков и новейшая информация об акциях
        :rtype: tuple
        """
        loop = asyncio.get_event_loop()
        # переводим нужную нам дату(прошлый год) в unix форму
        d = datetime.datetime.utcnow()
        d1 = d - datetime.timedelta(days=365)
        unix_time = calendar.timegm(d.utctimetuple())
        # задаём параметры для запросов
        methods = {
            'stock/profile2': {
                'symbol': symbol
            },
            'stock/candle': {
                'symbol': symbol,
                'resolution': '60',
                'from': str(calendar.timegm(d1.utctimetuple())),
                'to': str(unix_time)
            },
            'quote': {
                'symbol': symbol
            }
        }
        # заполняем список сопрограмм(корутин)
        coroutines = []
        for method, params in methods.items():
            # перевод 'сырых' параметров в нормальную строку-URL
            url = f'{API_URL}{method}' \
                  f'?{"&".join([f"{name}={value}" for name, value in params.items()])}' \
                  f'&token={FINN_API_KEY}'
            coroutines.append(self.get_info(url))
        # запускаем наши сопрограммы
        results = loop.run_until_complete(asyncio.gather(*coroutines))
        return results

    def on_close(self):
        # по завершению работы программы необходимо закрыть соединение
        self.client.close()
