import json
import unittest
from unittest.mock import patch

from src.views import web_page


class TestWebPage(unittest.TestCase):

    @patch("src.views.read_json")
    @patch("src.views.find_exchange_rate")
    @patch("src.views.find_stockmarket_rate")
    @patch("src.views.count_stat_by_card")
    @patch("src.views.find_top_5_transactions")
    @patch("src.views.good_something")
    def test_web_page(
        self,
        mock_good_something,
        mock_find_top_5_transactions,
        mock_count_stat_by_card,
        mock_find_stockmarket_rate,
        mock_find_exchange_rate,
        mock_read_json,
    ):
        # Подготовка мока
        mock_read_json.return_value = {
            "user_currencies": ["USD", "EUR"],
            "user_stocks": ["AAPL", "GOOGL"],
        }
        mock_find_exchange_rate.side_effect = lambda currency: (
            1.1 if currency == "USD" else 0.9
        )
        mock_find_stockmarket_rate.side_effect = lambda stock: (
            150 if stock == "AAPL" else 200
        )
        mock_count_stat_by_card.return_value = {"Visa": 100, "MasterCard": 200}
        mock_find_top_5_transactions.return_value = [
            {"transaction_id": 1, "amount": 500},
            {"transaction_id": 2, "amount": 300},
        ]
        mock_good_something.return_value = "Доброе утро!"

        # Используем правильный формат времени
        current_time = "2025-03-19 09:00:00"
        data = [
            {"transaction_id": 1, "amount": 500},
            {"transaction_id": 2, "amount": 300},
        ]

        # Вызов функции
        result = web_page(current_time, data)

        # Преобразуем строку в словарь
        result_dict = json.loads(result)

        # Проверка, что ключи присутствуют в ответе
        self.assertIn("greeting", result_dict)
        self.assertIn("cards", result_dict)
        self.assertIn("currency_rates", result_dict)
        self.assertIn("stocks_prices", result_dict)
        self.assertIn("top_transactions", result_dict)

        # Проверка, что в currency_rates содержатся корректные данные для валют
        currency_rates = result_dict.get("currency_rates", [])
        self.assertTrue(
            any(
                rate["currency"] == "USD" and rate["rate"] == 1.1
                for rate in currency_rates
            )
        )
        self.assertTrue(
            any(
                rate["currency"] == "EUR" and rate["rate"] == 0.9
                for rate in currency_rates
            )
        )

        # Выводим результат для диагностики ошибки
        print(result)

    @patch("src.views.read_json")
    def test_web_page_with_empty_data(self, mock_read_json):
        # Тест с пустым набором данных
        mock_read_json.return_value = {"user_currencies": ["USD"], "user_stocks": []}

        current_time = "2025-03-19 19:00:00"  # Используем правильный формат времени
        data = []

        result = web_page(current_time, data)

        # Преобразуем строку в словарь
        result_dict = json.loads(result)

        # Проверка, что результат содержит строку с ожидаемыми данными
        self.assertIn("greeting", result_dict)
        self.assertIn("cards", result_dict)
        self.assertIn("currency_rates", result_dict)
        self.assertIn("stocks_prices", result_dict)


# Запуск тестов
if __name__ == "__main__":
    unittest.main()
