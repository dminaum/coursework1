import unittest
from unittest.mock import MagicMock, mock_open, patch

from src.utils import (count_stat_by_card, find_all_cards, find_exchange_rate,
                       find_stockmarket_rate, find_top_5_transactions,
                       good_something, read_json, read_xlsx)


class TestUtils(unittest.TestCase):

    def test_good_something(self):
        self.assertEqual(good_something("2025-03-19 06:30:00"), "Доброе утро!")
        self.assertEqual(good_something("2025-03-19 13:30:00"), "Добрый день!")
        self.assertEqual(good_something("2025-03-19 19:30:00"), "Добрый вечер!")
        self.assertEqual(good_something("2025-03-19 02:30:00"), "Доброй ночи!")

    def test_find_all_cards(self):
        transactions = [
            {"last_digits": "1234"},
            {"last_digits": "5678"},
            {"last_digits": "1234"},
        ]
        self.assertEqual(set(find_all_cards(transactions)), {"1234", "5678"})

    def test_count_stat_by_card(self):
        transactions = [
            {"last_digits": "1234", "cashback": 10, "amount_transaction_rub": 100},
            {"last_digits": "1234", "cashback": 5, "amount_transaction_rub": 50},
            {"last_digits": "5678", "cashback": 2, "amount_transaction_rub": 30},
        ]
        expected = [
            {"last_digits": "5678", "total_spent": 30, "cashback": 2},
            {"last_digits": "1234", "total_spent": 150, "cashback": 15},
        ]

        result = count_stat_by_card(transactions)

        self.assertEqual(
            sorted(result, key=lambda x: x["last_digits"]),
            sorted(expected, key=lambda x: x["last_digits"]),
        )

    def test_find_top_5_transactions(self):
        transactions = [
            {"amount_transaction_rub": "-200"},
            {"amount_transaction_rub": "-100"},
            {"amount_transaction_rub": "-300"},
            {"amount_transaction_rub": "-50"},
            {"amount_transaction_rub": "-500"},
            {"amount_transaction_rub": "-10"},
        ]
        top_5 = find_top_5_transactions(transactions)
        self.assertEqual(len(top_5), 5)
        self.assertEqual(top_5[0]["amount_transaction_rub"], "-10")

    @patch("src.utils.requests.get")
    def test_find_exchange_rate(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"result": 75.0}
        self.assertEqual(find_exchange_rate("USD"), 75.0)

    @patch("src.utils.requests.get")
    def test_find_stockmarket_rate(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "Global Quote": {"05. price": "150.5"}
        }
        self.assertEqual(find_stockmarket_rate("AAPL"), 150.5)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}',
    )
    def test_read_json(self, mock_file):
        data = read_json("./user_settings.json")
        self.assertEqual(data, {"user_currencies": ["USD"], "user_stocks": ["AAPL"]})


class TestReadXlsx(unittest.TestCase):

    @patch("os.path.exists")
    @patch("pandas.read_excel")
    @patch("src.utils.logger")
    def test_read_xlsx_success(self, mock_logger, mock_read_excel, mock_exists):
        # Настроим моки
        mock_exists.return_value = True
        mock_df = MagicMock()
        mock_df.to_dict.return_value = [
            {
                "Дата операции": "2025-03-19",
                "Дата платежа": "2025-03-19",
                "Статус": "Completed",
                "Номер карты": "1234",
                "Сумма операции": 1000,
                "Валюта операции": "USD",
                "Сумма платежа": 1000,
                "Валюта платежа": "USD",
                "Кэшбэк": 10,
                "Категория": "Food",
                "MCC": "1234",
                "Бонусы (включая кэшбэк)": 50,
                "Округление на инвесткопилку": 0,
                "Описание": "Purchase",
                "Сумма операции с округлением": 1000,
            }
        ]
        mock_read_excel.return_value = mock_df

        # Вызовем функцию
        result = read_xlsx("test.xlsx")

        # Проверим, что результат соответствует ожидаемому
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["operation_date"], "2025-03-19")
        self.assertEqual(result[0]["amount_transaction"], 1000)
        mock_logger.info.assert_called_with(
            "Файл test.xlsx успешно загружен. Найдено 1 записей."
        )

    @patch("os.path.exists")
    @patch("src.utils.logger")
    def test_file_not_found(self, mock_logger, mock_exists):
        # Настроим мок, что файл не существует
        mock_exists.return_value = False

        # Вызовем функцию
        result = read_xlsx("non_existent_file.xlsx")

        # Проверим, что результат пустой список
        self.assertEqual(result, [])
        mock_logger.warning.assert_called_with(
            "Файл non_existent_file.xlsx не найден. Возвращаем пустой список."
        )

    @patch("os.path.exists")
    @patch("pandas.read_excel")
    @patch("src.utils.logger")
    def test_invalid_data_structure(self, mock_logger, mock_read_excel, mock_exists):
        # Настроим моки
        mock_exists.return_value = True
        mock_df = MagicMock()
        mock_df.to_dict.return_value = {}  # Возвращаем некорректные данные (не список)
        mock_read_excel.return_value = mock_df

        # Вызовем функцию
        result = read_xlsx("test_invalid.xlsx")

        # Проверим, что результат пустой список
        self.assertEqual(result, [])
        mock_logger.warning.assert_called_with(
            "Файл test_invalid.xlsx не содержит списка транзакций."
        )

    @patch("os.path.exists")
    @patch("pandas.read_excel")
    @patch("src.utils.logger")
    def test_transaction_processing_error(
        self, mock_logger, mock_read_excel, mock_exists
    ):
        # Настроим моки
        mock_exists.return_value = True
        mock_df = MagicMock()
        mock_df.to_dict.return_value = [
            {
                "Дата операции": "2025-03-19",
                "Дата платежа": "2025-03-19",
                "Статус": "Completed",
                "Номер карты": "1234",
                "Сумма операции": "1000",
                "Валюта операции": "USD",
                "Сумма платежа": "1000",
                "Валюта платежа": "USD",
                "Кэшбэк": "10",
                "Категория": "Food",
                "MCC": "1234",
                "Бонусы (включая кэшбэк)": "invalid",  # Ошибка в данных
                "Округление на инвесткопилку": 0,
                "Описание": "Purchase",
                "Сумма операции с округлением": 1000,
            }
        ]
        mock_read_excel.return_value = mock_df

        # Вызовем функцию
        result = read_xlsx("test_error.xlsx")

        # Проверим, что результат пустой список
        self.assertEqual(result, [])
        mock_logger.error.assert_called_with(
            "Ошибка обработки транзакции: {'Дата операции': '2025-03-19', 'Дата платежа': '2025-03-19', 'Статус': "
            "'Completed', 'Номер карты': '1234', 'Сумма операции': '1000', 'Валюта операции': 'USD', 'Сумма платежа': "
            "'1000', 'Валюта платежа': 'USD', 'Кэшбэк': '10', 'Категория': 'Food', 'MCC': '1234', 'Бонусы (включая "
            "кэшбэк)': 'invalid', 'Округление на инвесткопилку': 0, 'Описание': 'Purchase', 'Сумма операции с "
            "округлением': 1000}. Ошибка: invalid literal for int() with base 10: 'invalid'"
        )

    @patch("os.path.exists")
    @patch("pandas.read_excel")
    @patch("src.utils.logger")
    def test_read_xlsx_exception(self, mock_logger, mock_read_excel, mock_exists):
        # Настроим моки
        mock_exists.return_value = True
        mock_read_excel.side_effect = Exception("Ошибка чтения файла")

        # Вызовем функцию
        result = read_xlsx("test_error_file.xlsx")

        # Проверим, что результат пустой список
        self.assertEqual(result, [])
        mock_logger.error.assert_called_with(
            "Ошибка чтения файла test_error_file.xlsx: Ошибка чтения файла"
        )


if __name__ == "__main__":
    unittest.main()
