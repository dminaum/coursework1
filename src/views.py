import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from src.utils import (count_stat_by_card, find_exchange_rate,
                       find_stockmarket_rate, find_top_5_transactions,
                       good_something, read_json)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SCRIPT_DIR = Path(__file__).resolve().parent
MAIN_DIR = SCRIPT_DIR.parent
SETTINGS_PATH = MAIN_DIR / "user_settings.json"


def web_page(current_time: str, data: List[Dict[str, Any]]) -> str:
    """
    Формирует JSON-ответ для фронтенда, содержащий информацию о картах, курсах валют, акциях и транзакциях.

    :param current_time: Текущее время в строковом формате.
    :param data: Список транзакций, представленный в виде списка словарей.
    :return: JSON-строка с данными для отображения на веб-странице.
    """
    logging.info("Вызвана функция web_page с текущим временем: %s", current_time)

    try:
        user_settings = read_json(SETTINGS_PATH)
        logging.info("Загружены настройки пользователя.")
    except Exception as e:
        logging.error("Ошибка при загрузке настроек пользователя: %s", e)
        raise

    user_currencies = user_settings.get("user_currencies", [])
    logging.info("Получены валюты пользователя: %s", user_currencies)

    currency_rates = []
    for currency in user_currencies:
        try:
            rate = find_exchange_rate(currency)
            currency_rates.append({"currency": currency, "rate": rate})
            logging.info("Получен курс валюты %s: %s", currency, rate)
        except Exception as e:
            logging.error("Ошибка при получении курса для валюты %s: %s", currency, e)

    user_stocks = user_settings.get("user_stocks", [])
    logging.info("Получены акции пользователя: %s", user_stocks)

    stocks_prices = []
    for stock in user_stocks:
        try:
            price = find_stockmarket_rate(stock)
            stocks_prices.append({"stock": stock, "price": price})
            logging.info("Получена цена акции %s: %s", stock, price)
        except Exception as e:
            logging.error("Ошибка при получении цены для акции %s: %s", stock, e)

    try:
        response = {
            "greeting": good_something(current_time),
            "cards": count_stat_by_card(data),
            "top_transactions": find_top_5_transactions(data),
            "currency_rates": currency_rates,
            "stocks_prices": stocks_prices,
        }
        response_json = json.dumps(response, indent=4, ensure_ascii=False)
        logging.info("Сформирован ответ для фронтенда.")
        return response_json
    except Exception as e:
        logging.error("Ошибка при формировании ответа: %s", e)
        raise
