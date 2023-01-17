import sqlite3
from typing import List, NamedTuple

MONTH_DICT = {'01': "Січень", '02': "Лютий", '03': "Березень", '04': "Квітень",
             '05': "Травень", '06': "Червень", '07': "Липень", '08': "Серпень",
             '09':"Вересень", '10': "Жовтень", '11':"Листопад", '12': "Грудень"}

conn = sqlite3.connect('finance.db')


class Category(NamedTuple):
    codename: str
    name: str
    nominations: List[str]
    base_expense: bool


def getting_categories():
    cursor = conn.cursor()
    categories = cursor.execute("SELECT codename_id, name,  nominations, base_expense FROM categories")
    categories_list = []
    for itm in categories:
        categories_list.append(Category(codename=itm[0], name=itm[1], nominations=itm[2], base_expense=itm[3]))
    return categories_list


def get_category_by_nominations(category_codename):
    categories = getting_categories()
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


print(get_category_by_nominations('їжа'))
print(get_category_by_nominations('кава'))
print(get_category_by_nominations('обід'))
print(get_category_by_nominations('бензин'))
print(get_category_by_nominations("зв'язок"))
print(get_category_by_nominations('журнали'))
print(get_category_by_nominations('інтернет'))
print(get_category_by_nominations('підписка'))
print(get_category_by_nominations('табак'))
print(get_category_by_nominations('зброя'))
print(get_category_by_nominations('підкови для коня'))


def every_month_stat(month_dict):
    """Ця функція """

    cursor = conn.cursor()
    month_stat_dict = {}
    for negative_count in range(0, 11):
        cursor.execute(f"SELECT sum(amount) AS Sum, strftime('%m %Y', created) "
                       f"FROM expense WHERE date(created) = date('now', '-{negative_count} month', '+0 year')")
        result = cursor.fetchone()
        if result[0]:
            splitted_result = result[1].split(' ')
            for key, value in month_dict.items():
                if splitted_result[0] == key:
                    month_and_year = ' '.join([value, splitted_result[1]])
                    month_stat_dict[month_and_year] = result[0]

    answer = "Ваші помісячні витрати наступні:\n\n"
    for key, value in month_stat_dict.items():
        answer = answer + f" > За {key} ви витратили {value} грн.\n"
    return answer


print(every_month_stat(MONTH_DICT))
