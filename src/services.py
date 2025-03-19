import json
import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def search_transactions_by_keyword(data: List[Dict[str, Any]], key_word: str) -> str:
    """
    Выполняет поиск транзакций по заданному ключевому слову в их описании.

    :param data: Список транзакций, где каждая транзакция представлена словарем.
    :param key_word: Ключевое слово для поиска в описании транзакций.
    :return: JSON-строка с найденными транзакциями.
    """
    if not isinstance(data, list):
        logger.error("Переданные данные не являются списком.")
        return json.dumps([])

    if not isinstance(key_word, str) or not key_word:
        logger.warning("Ключевое слово отсутствует или не является строкой.")
        return json.dumps([])

    logger.info(f"Начат поиск транзакций по ключевому слову: '{key_word}'")

    result_list = []
    pattern = re.compile(rf"{key_word}", re.IGNORECASE)

    for transaction in data:
        if not isinstance(transaction, dict):
            logger.warning(f"Пропущена некорректная транзакция: {transaction}")
            continue

        if "description" not in transaction:
            logger.warning(f"Пропущена транзакция без описания: {transaction}")
            continue

        if pattern.search(transaction["description"]) is not None:
            result_list.append(transaction)

    logger.info(
        f"Найдено {len(result_list)} транзакций по ключевому слову '{key_word}'"
    )

    return json.dumps(result_list, indent=4, ensure_ascii=False)
