import sqlite3
from typing import List, NamedTuple

conn = sqlite3.connect('finance.db')


class Category(NamedTuple):
    """Це структура, що подібна запису у БД у таблиці categories."""

    codename: str
    name: str
    nominations: List[str]
    base_expense: bool


class Categories:

    def __init__(self):
        self.categories = self._categories_showcase()

    @staticmethod
    def _categories_showcase() -> List[Category]:
        """Функція повертає усі елементи з таблиці category, та
        повертає їх у вигляді списку з об'єктами класу Category."""

        cursor = conn.cursor()
        categories = cursor.execute("SELECT codename_id, name,  nominations, base_expense FROM categories")
        categories_list = []
        for itm in categories:
            categories_list.append(Category(codename=itm[0], name=itm[1], nominations=itm[2], base_expense=itm[3]))
        return categories_list

    def get_all_categories(self):
        return self.categories

    def get_category_by_nominations(self, category_codename: str) -> Category:
        """Функція за іменуванням, що описав користувач обирає категорію,
        до якої це наіменування відноситься. Повертає об'єкт Category."""

        categories = self.get_all_categories()
        answer = None
        for category in categories:
            nominations = category.nominations.split(', ')
            if category_codename in nominations:
                answer = category
                break
        if answer:
            return answer
        else:
            return categories[-1]
