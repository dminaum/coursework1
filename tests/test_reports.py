from datetime import datetime

import pytest

from src.reports import \
    spending_by_category  # Убедись, что импортируешь из правильного модуля


@pytest.fixture
def mock_transactions():
    # Пример транзакций для тестирования
    return [
        {"operation_date": "2025-01-15", "category": "Food", "amount": 50},
        {"operation_date": "2025-02-10", "category": "Transport", "amount": 20},
        {"operation_date": "2025-03-10", "category": "Food", "amount": 30},
        {"operation_date": "2025-03-20", "category": "Entertainment", "amount": 100},
    ]


# Тест: Проверка фильтрации по категории за последние 3 месяца
def test_spending_by_category(mock_transactions):
    result = spending_by_category(mock_transactions, "Food", "2025-03-20")

    # Проверяем, что в результатах только транзакции с категорией "Food"
    assert len(result) == 2
    assert all(row["category"] == "Food" for index, row in result.iterrows())

    # Проверяем корректность сумм
    assert result["amount"].sum() == 80  # 50 + 30


# Тест: Проверка фильтрации с использованием даты по умолчанию
def test_spending_by_category_default_date(mock_transactions):
    today = datetime.today().strftime("%Y-%m-%d")
    result = spending_by_category(mock_transactions, "Food", today)

    # Проверяем, что функция вернет все транзакции с категорией "Food"
    assert len(result) == 2


# Тест: Проверка с пустыми данными
def test_spending_by_category_empty(mock_transactions):
    result = spending_by_category(
        mock_transactions, "NonExistentCategory", "2025-03-20"
    )

    # Должно быть 0 транзакций с такой категорией
    assert len(result) == 0


# Тест: Проверка на дату, которая старше 3 месяцев
def test_spending_by_category_date_filter(mock_transactions):
    result = spending_by_category(mock_transactions, "Food", "2025-03-20")

    # Проверяем, что транзакции, старше 3 месяцев, не включаются
    assert (
        len(result) == 2
    )  # 2 транзакции с категорией "Food", которые в пределах 3 месяцев
