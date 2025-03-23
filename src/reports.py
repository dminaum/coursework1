import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
from pandas import DataFrame

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def save_report(file_name: Optional[str] = None) -> Any:
    """
    Декоратор для сохранения результата работы функции в JSON-файл.

    :param file_name: Опциональное имя файла для сохранения.
    :return: Декоратор, оборачивающий функцию.
    """

    def decorator(func: Any) -> Any:
        def wrapper(*args: tuple, **kwargs: dict) -> Any:
            logging.info(f"Выполнение функции {func.__name__}")
            result = func(*args, **kwargs)
            file_path = file_name or f"report_{func.__name__}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    result.to_dict(orient="records"), f, ensure_ascii=False, indent=4
                )
            logging.info(f"Отчет сохранен в файл {file_path}")
            return result

        return wrapper

    return decorator


@save_report()
def spending_by_category(
    transactions: List[Dict[str, Any]], category: str, date: Optional[str] = None
) -> DataFrame:
    """
    Фильтрует список транзакций по заданной категории за последние 90 дней.

    :param transactions: Список транзакций в виде словарей.
    :param category: Категория, по которой нужно отфильтровать транзакции.
    :param date: Опциональная дата, от которой отсчитываются 90 дней. Если не указана, берется текущая.
    :return: DataFrame с отфильтрованными транзакциями.
    """
    logging.info("Начало обработки транзакций по категории")

    if date is None:
        date_str = datetime.today().strftime("%Y-%m-%d")
    else:
        date_str = date

    date_dt = datetime.strptime(date_str, "%Y-%m-%d")  # Преобразование в datetime
    three_months_ago = date_dt - timedelta(days=90)

    df = pd.DataFrame(transactions)
    df["operation_date"] = pd.to_datetime(df["operation_date"], dayfirst=True)

    # Преобразуем datetime в строку для сериализации
    df["operation_date"] = df["operation_date"].dt.strftime("%Y-%m-%d")

    # Фильтруем по дате и категории
    df_filtered = df[
        (df["operation_date"] >= three_months_ago.strftime("%Y-%m-%d"))
        & (df["category"] == category.title())
    ]

    logging.info(f"Найдено {len(df_filtered)} транзакций по категории '{category}'")
    return df_filtered
