import json
import unittest
from unittest.mock import patch

from src.services import search_transactions_by_keyword


class TestSortTransactionsKey(unittest.TestCase):

    def setUp(self):
        self.transactions = [
            {"description": "Оплата в кафе", "amount": 100},
            {"description": "Перевод другу", "amount": 200},
            {"description": "Кафе на берегу", "amount": 150},
            {"description": "Покупка в магазине", "amount": 300},
        ]

    def test_found_transactions(self):
        """Проверяем, что находятся нужные транзакции"""
        result_json = search_transactions_by_keyword(self.transactions, "кафе")
        result = json.loads(result_json)
        expected = [
            {"description": "Оплата в кафе", "amount": 100},
            {"description": "Кафе на берегу", "amount": 150},
        ]
        self.assertEqual(result, expected)

    def test_no_matching_transactions(self):
        """Проверяем случай, когда ничего не найдено"""
        result_json = search_transactions_by_keyword(self.transactions, "бензин")
        result = json.loads(result_json)
        self.assertEqual(result, [])

    def test_empty_transactions_list(self):
        """Проверяем, что функция корректно работает с пустым списком"""
        result_json = search_transactions_by_keyword([], "кафе")
        result = json.loads(result_json)
        self.assertEqual(result, [])

    def test_invalid_data_type(self):
        """Проверяем, что передача некорректных данных приводит к возврату пустого списка"""
        result_json = search_transactions_by_keyword("invalid_data", "кафе")
        result = json.loads(result_json)
        self.assertEqual(result, [])

    def test_empty_keyword(self):
        """Проверяем, что пустое ключевое слово не приводит к ошибкам"""
        result_json = search_transactions_by_keyword(self.transactions, "")
        result = json.loads(result_json)
        self.assertEqual(result, [])

    def test_transactions_with_missing_description(self):
        """Проверяем, что функция пропускает транзакции без 'description'"""
        transactions = [
            {"description": "Оплата в кафе", "amount": 100},
            {"amount": 200},  # Нет описания
            {"description": "Кафе на берегу", "amount": 150},
        ]
        result_json = search_transactions_by_keyword(transactions, "кафе")
        result = json.loads(result_json)
        expected = [
            {"description": "Оплата в кафе", "amount": 100},
            {"description": "Кафе на берегу", "amount": 150},
        ]
        self.assertEqual(result, expected)

    @patch("src.services.logger")
    def test_logging(self, mock_logger):
        """Проверяем, что вызываются нужные сообщения логирования"""
        search_transactions_by_keyword(self.transactions, "кафе")
        mock_logger.info.assert_any_call(
            "Начат поиск транзакций по ключевому слову: 'кафе'"
        )
        mock_logger.info.assert_any_call(
            "Найдено 2 транзакций по ключевому слову 'кафе'"
        )

    @patch("src.services.logger")
    def test_logging_for_invalid_data(self, mock_logger):
        """Проверяем логирование ошибок и предупреждений"""
        search_transactions_by_keyword("invalid_data", "кафе")
        mock_logger.error.assert_called_with("Переданные данные не являются списком.")

        search_transactions_by_keyword(self.transactions, "")
        mock_logger.warning.assert_called_with(
            "Ключевое слово отсутствует или не является строкой."
        )

        search_transactions_by_keyword([{"amount": 200}], "кафе")
        mock_logger.warning.assert_called_with(
            "Пропущена транзакция без описания: {'amount': 200}"
        )


if __name__ == "__main__":
    unittest.main()
