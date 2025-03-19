import heapq
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd
import requests
from dotenv import load_dotenv

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("utils.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
load_dotenv()
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
STOCKMARKET_API_KEY = os.getenv("STOCKMARKET_API_KEY")


def good_something(datetime_str: str) -> str:
    """
    :param datetime_str: строка с указанием времени
    :return: строка с приветствием, в зависимости от текущего времени
    """
    try:
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        current_hour = datetime_obj.hour

        if 5 <= current_hour < 12:
            greeting = "Доброе утро!"
        elif 12 <= current_hour < 18:
            greeting = "Добрый день!"
        elif 18 <= current_hour < 23:
            greeting = "Добрый вечер!"
        else:
            greeting = "Доброй ночи!"

        logger.info(f"Приветствие: {greeting} (на основе времени {datetime_str})")
        return greeting
    except ValueError as e:
        logger.error(f"Ошибка обработки времени: {datetime_str} - {e}")
        return "Ошибка в формате даты"


def find_all_cards(data: List[Dict[str, str | float]]) -> List[str | float]:
    """Дает список уникальных карт, использованных за определенный период"""
    if not data:
        logger.warning("Передан пустой список транзакций.")
        return []

    cards = [transaction.get("last_digits", "") for transaction in data]
    unique_cards = list(set(cards))

    logger.info(f"Найдено {len(unique_cards)} уникальных карт.")
    return unique_cards


def count_stat_by_card(
    data: List[Dict[str, Union[str, float]]],
) -> List[Dict[str, Union[str, float]]]:
    """
    Считает количество трат и кэшбэка по каждой карте.
    """
    if not data:
        logger.warning("Передан пустой список транзакций.")
        return []

    all_cards = find_all_cards(data)
    results = []

    for card in all_cards:
        cashback = sum(
            float(transaction.get("cashback", 0) or 0)
            for transaction in data
            if transaction["last_digits"] == card
        )
        total_spent = sum(
            float(transaction.get("amount_transaction_rub", 0) or 0)
            for transaction in data
            if transaction["last_digits"] == card
        )

        results.append(
            {
                "last_digits": card if card else "Другие карты",
                "total_spent": round(total_spent, 2),
                "cashback": round(cashback, 2),
            }
        )

    logger.info(f"Рассчитана статистика по {len(results)} картам.")
    return results


def find_top_5_transactions(data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Ищет 5 самых крупных транзакций
    """
    if not data:
        logger.warning("Передан пустой список транзакций.")
        return []

    try:
        result = heapq.nlargest(
            5, data, key=lambda x: float(x.get("amount_transaction_rub", 0))
        )
        logger.info("Топ-5 транзакций успешно найден.")
        return result
    except (ValueError, KeyError) as e:
        logger.error(f"Ошибка при поиске топ-5 транзакций: {e}")
        return []


def read_xlsx(file_path: str | Path) -> List[Dict]:
    """
    Читает Excel-файл и возвращает список транзакций.

    :param file_path: путь до файла xlsx
    :return: список со словарями транзакций
    """
    if not os.path.exists(file_path):
        logger.warning(f"Файл {file_path} не найден. Возвращаем пустой список.")
        return []

    try:
        df = pd.read_excel(file_path)
        df.fillna(0, inplace=True)
        data = df.to_dict(orient="records")

        if not isinstance(data, list):
            logger.warning(f"Файл {file_path} не содержит списка транзакций.")
            return []

        logger.info(f"Файл {file_path} успешно загружен. Найдено {len(data)} записей.")

        normalized_data = []
        for transaction in data:
            try:
                normalized_transaction = {
                    "operation_date": transaction.get("Дата операции", ""),
                    "payment_date": transaction.get("Дата платежа", ""),
                    "state": transaction.get("Статус", ""),
                    "last_digits": transaction.get("Номер карты", ""),
                    "amount_transaction": transaction.get("Сумма операции", 0),
                    "currency": transaction.get("Валюта операции", ""),
                    "amount_transaction_rub": transaction.get("Сумма платежа", 0),
                    "account_currency": transaction.get("Валюта платежа", ""),
                    "cashback": transaction.get("Кэшбэк", 0),
                    "category": transaction.get("Категория", ""),
                    "transaction_code": transaction.get("MCC", ""),
                    "benefit": int(
                        transaction.get("Бонусы (включая кэшбэк)", 0)
                    ),  # Приводим к int
                    "amount_to_piggy": transaction.get(
                        "Округление на инвесткопилку", 0
                    ),
                    "description": transaction.get("Описание", ""),
                    "amount_rounded": transaction.get(
                        "Сумма операции с округлением", 0
                    ),
                }
                normalized_data.append(normalized_transaction)
            except (ValueError, TypeError) as e:
                logger.error(f"Ошибка обработки транзакции: {transaction}. Ошибка: {e}")
                continue  # Пропускаем некорректные транзакции

        return normalized_data
    except Exception as e:
        logger.error(f"Ошибка чтения файла {file_path}: {e}")
        return []


def read_json(file_path: Path) -> Dict:
    """Читает JSON-файл настроек клиента."""
    if not os.path.exists(file_path):
        logger.warning(f"Файл {file_path} не найден. Возвращаем пустой словарь.")
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if not isinstance(data, dict):
                logger.warning(f"Файл {file_path} содержит некорректные данные.")
                return {}
            logger.info(f"Файл {file_path} успешно загружен.")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON в файле {file_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Ошибка чтения файла {file_path}: {e}")
        return {}


def find_exchange_rate(
    currency_from: str, amount: float = 1, currency_to: str = "RUB"
) -> float | None:
    """Конвертирует сумму из одной валюты в рубли через API."""
    if currency_from == currency_to:
        return amount
    url = f"https://api.apilayer.com/exchangerates_data/convert?to={currency_to}&from={currency_from}&amount={amount}"
    url = f"https://api.apilayer.com/exchangerates_data/convert?to={currency_to}&from={currency_from}&amount={amount}"
    headers = {"apikey": CURRENCY_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        result = data.get("result")
        if result is not None:
            return float(result)
        else:
            logger.warning("Ошибка API: отсутствует ключ 'result'")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе API: {e}")
        return None


def find_stockmarket_rate(stock_from: str) -> float | None:
    """Получает курс акции."""
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_from}&apikey={STOCKMARKET_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        price_str = data.get("Global Quote", {}).get("05. price")
        if price_str:
            return float(price_str)
        else:
            logger.warning(f"Ошибка API: не найден ключ '05. price' для {stock_from}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе API: {e}")
        return None
