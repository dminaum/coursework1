from pathlib import Path

from src.reports import spending_by_category
from src.services import search_transactions_by_keyword
from src.utils import read_xlsx
from src.views import web_page

MAIN_DIR = Path(__file__).resolve().parent
PATH_XLSX = MAIN_DIR / "data" / "operations.xlsx"


def main():
    """
    Основная функция программы. Предлагает пользователю выбрать один из сервисов:

    1. Веб-страница — генерация JSON-словаря с отчетом по транзакциям, курсам валют и акций.
    2. Поиск по транзакциям — фильтрация списка транзакций по ключевому слову.
    3. Траты по категориям — расчет трат по указанной категории за последние 90 дней.

    Функция загружает данные из файла operations.xlsx и передает их в выбранный сервис.

    :return: Результат работы выбранного сервиса (JSON-словарь/Pandas Dataframe).
    """
    data = read_xlsx(PATH_XLSX)
    print('Здравствуйте!')
    feature = input(
        """
Каким сервисом хотите воспользоваться?
Веб-страница // Поиск по транзакциям // Траты по категориям
""")

    if feature.lower() == 'веб-страница':
        current_time = input('Введите текущие дату и время в формате ГГГГ-ММ-ДД ЧЧ:ММ:СС ')
        result = web_page(current_time, data)
        print(result)
        return result

    elif feature.lower() == 'поиск по транзакциям':
        key_word = input('По какому слову в описании искать транзакции? ')
        result = search_transactions_by_keyword(data, key_word)
        print(result)
        return result

    elif feature.lower() == 'траты по категориям':
        category = input('Введите название категории ')
        date = input('По какую дату создать 3-х месячный отчет? Введите в формате ГГГГ-ММ-ДД ')
        result = spending_by_category(data, category, date)
        print(result)
        return result


if __name__ == '__main__':
    main()
