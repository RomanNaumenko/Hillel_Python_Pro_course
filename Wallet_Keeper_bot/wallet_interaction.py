import sqlite3
import re
import exception
from typing import NamedTuple, Optional
import categories
import datetime
import pytz
from aiogram.dispatcher.filters.state import StatesGroup, State

conn = sqlite3.connect('finance.db')

MONTH_DICT = {'01': "січень", '02': "лютий", '03': "березень", '04': "квітень",
              '05': "травень", '06': "червень", '07': "липень", '08': "серпень",
              '09': "вересень", '10': "жовтень", '11': "листопад", '12': "грудень"}


class Message(NamedTuple):
    """Це структура распаршенного повідомлення про нову витрату."""

    amount: int
    category_text: str


class Expense(NamedTuple):
    """Структура нової витрати, що була додана до ДБ."""

    id: Optional[int]
    amount: int
    category_name: str


class BasicExp(StatesGroup):
    Q1 = State()


def add_expense(message_text: str) -> Expense:
    """Функція дадає до БД вказану витрату та повертає об'єкт Expense."""

    message = parsed_expense(message_text)
    category = categories.Categories().get_category_by_nominations(message.category_text)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expense (amount, created, category_codename, raw_text)"
                   f"VALUES('{message.amount}', '{get_today()}', '{category.codename}', '{message.category_text}')")
    conn.commit()
    return Expense(id=None, amount=message.amount, category_name=category.name)


def check_daily():

    cursor = conn.cursor()
    cursor.execute("SELECT daily_limit FROM budget WHERE is_set=1 AND codename='base'")
    daily_roof = cursor.fetchone()
    cursor.execute(f"SELECT sum(amount) FROM expense JOIN categories c on c.codename_id = expense.category_codename "
                   f"WHERE date(expense.created) = date('now') AND c.base_expense=1")
    daily_sum = cursor.fetchone()
    if daily_sum[0] > daily_roof[0]:
        return ("Увага! Ви перевищили максимальне значення щоденних витрат на базові потреби!\n"
                "Рекомендую підвищити значення базових витрат командою /set_base")


def parsed_expense(user_text: str) -> Message:
    """Парсить повідомлення, та повертає об'єкт Message, з чітко
    указанними сумою(amount) та категорією трати(category_text)."""

    re_result = re.match(r"([\d ]+) (.*)", user_text)
    if not re_result or not re_result.group(0) \
            or not re_result.group(1) or not re_result.group(2):
        raise exception.NotCorrectMessage(
            "Не можу розпізнати повідомлення. Напишіть повідомлення у наступному форматі: "
            "\n1500 кава")

    amount = int(re_result.group(1).replace(" ", ""))
    category_text = re_result.group(2).strip().lower()
    return Message(amount=amount, category_text=category_text)


def get_today() -> datetime.datetime:
    """Повертає сьогоденний datetime з урахуванням часової зони."""

    time_zone = pytz.timezone("Europe/Kiev")
    today = datetime.datetime.now(time_zone)
    return today


def today_stat() -> str:
    """Повертає строку з інформацією про сьогоденні витрати. Якщо значення базових
    витрат було встановлене, виводить і статистичне позначення відповідно до прозведенних витрат."""

    available_budget = is_base_budget_set()
    cursor = conn.cursor()

    cursor.execute(f"SELECT sum(amount) FROM expense "
                   f"WHERE date(created) = date('now')")
    singleday_result = cursor.fetchone()
    if not singleday_result[0]:
        today_sum_of_expenses = 0
    else:
        today_sum_of_expenses = singleday_result[0]

    cursor.execute(f"SELECT sum(amount), category_codename FROM expense "
                   f"WHERE date(created) = date('now') AND "
                   f"category_codename IN "
                   f"(SELECT codename_id FROM categories WHERE base_expense = '1')")
    base_result = cursor.fetchone()
    try:
        if not base_result[0]:
            today_sum_of_base = 0
        else:
            today_sum_of_base = base_result[0]

        if available_budget[0]:
            if available_budget[0] > today_sum_of_base:

                return ("З початку місяця ваші витрати дорівнюють наступним показникам:\n"
                        f"Загальні витрати: {today_sum_of_expenses} грн.\n"
                        f"Базові витрати: {today_sum_of_base} грн. із {available_budget[0]} грн., що доступні\n"
                        f"Нещодавні витрати: /last_expenses\n"
                        f"Загалом у цьому місяці: /month_stat\n"
                        f"Загалом у цьому році(по місяцям): /every_month_stat")

            elif available_budget[0] < today_sum_of_base:

                return ("З початку місяця ваші витрати дорівнюють наступним показникам:\n"
                        f"Загальні витрати: {today_sum_of_expenses} грн.\n"
                        f"Базові витрати: {today_sum_of_base} грн. із {available_budget[0]} грн., що доступні\n"
                        f"Ваш ліміт витрат був перевищений на {round(today_sum_of_base - available_budget[0], 2)} грн.\n"
                        f"Нещодавні витрати: /last_expenses\n"
                        f"Загалом у цьому місяці: /month_stat\n"
                        f"Загалом у цьому році(по місяцям): /every_month_stat")

        else:
            return ("За сьогодні ваші витрати наступні:\n"
                    f"Загальні витрати: {today_sum_of_expenses} грн.\n"
                    f"Базові витрати: {today_sum_of_base} грн.\n"
                    f"Нещодавні витрати: /last_expenses\n"
                    f"Загалом у цьому місяці: /month_stat\n"
                    f"Загалом у цьому році(по місяцям): /every_month_stat")

    except (exception.NotCorrectMessage, IndexError):
        print(f"У мене ще не має інформації стосовно ваших витрат.\n\n"
              "Перед тим, як продивлятися свої витрати, ви повинні їх сюди записати\n"
              "Наприклад: 50 кофеїн")


def month_stat() -> str:
    """Повертає строку з інформацією щодо витрат, починаючи з початку місяця."""

    cursor = conn.cursor()

    cursor.execute(f"SELECT sum(amount) FROM expense "
                   f"WHERE date(created) >= date('now','start of month')")
    month_result = cursor.fetchone()
    if not month_result[0]:
        month_sum_of_expenses = 0
    else:
        month_sum_of_expenses = month_result[0]

    cursor.execute(f"SELECT sum(amount), category_codename FROM expense "
                   f"WHERE date(created) >= date('now','start of month') AND "
                   f"category_codename IN "
                   f"(SELECT codename_id FROM categories WHERE base_expense = '1')")
    month_base_result = cursor.fetchone()
    if not month_base_result[0]:
        month_sum_of_base = 0
    else:
        month_sum_of_base = month_base_result[0]

    return ("З початку місяця ваші витрати дорівнюють наступним показникам:\n"
            f"Загальні витрати: {month_sum_of_expenses} грн.\n"
            f"Базові витрати: {month_sum_of_base} грн.\n"
            f"Нещодавні витрати: /last_expenses\n"
                f"Витрати за сьогодні: /today_stat\n"
            f"Загалом у цьому році(по місяцям): /every_month_stat")


# def every_month_stat(month_dict):
#     """pass"""
#
#     cursor = conn.cursor()
#     month_stat_dict = {}
#     for negative_count in range(0, 11):
#         cursor.execute(f"SELECT sum(amount) AS Sum, strftime('%m %Y', created) "
#                        f"FROM expense WHERE date(created) = date('now', '-{negative_count} month', '+0 year')")
#         month_and_sum = cursor.fetchone()
#
#         if month_and_sum[0]:
#             for key, value in month_dict.items():
#                 if month_and_sum[1] in key:
#                     month_stat_dict[value] = month_and_sum[0]
#
#     answer = "Ваші помісячні витрати наступні:\n\n"
#     for key, value in month_stat_dict.items():
#         answer = answer + f" > За {key} ви витратили {value} грн.\n"
#     return answer

def every_month_stat(month_dict) -> dict:
    """Повертає словник з інформацією щодо витрат, за кожен місяць(у якому вони були)."""

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

    return month_stat_dict


def last_exp() -> str:
    """Повертає останні декілька витрат(До 10)."""

    cursor = conn.cursor()
    cursor.execute(
        "select expense.id, expense.amount, categories.name "
        "from expense left join categories on categories.codename_id=expense.category_codename "
        "order by created desc limit 10")
    rows = cursor.fetchall()
    try:
        if not rows[0]:
            return ("У вас ще не має витрат.")
        else:
            last_expenses = [Expense(id=row[0], amount=row[1], category_name=row[2]) for row in rows]
            raw_answer = [f"{last.amount} грн. на {last.category_name} — натисни /delete{last.id} з метою видалення"
                          for last in last_expenses]
            answer = "Останні витрати, зроблені вами:\n\n> " + "\n\n> " \
                .join(raw_answer)
            return answer
    except (exception.InvalidExecuteDB, IndexError) as err:
        return (f"У мене ще не має інформації стосовно ваших витрат.\n\n"
                "Перед тим, як продивлятися свої витрати, ви повинні їх сюди записати\n"
                "Наприклад: 50 кофеїн")


def delete_by_id(row_id: int) -> None:
    """Звертається до БД з метою видалення витрати за її id."""

    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM expense WHERE id={row_id}")
    conn.commit()


def is_base_budget_set():
    """Перевіряє, чи встановлене у БД значення базових витрат та повертає це значення."""

    cursor = conn.cursor()
    cursor.execute(f"SELECT daily_limit FROM budget WHERE is_set=TRUE AND codename='base'")
    budget = cursor.fetchone()
    return budget


def set_basic_expenses(value) -> str:
    """Встановлює у БД значення базових витрат та повертає строку з інформацією щодо цього."""

    cursor = conn.cursor()
    cursor.execute(f"UPDATE budget SET daily_limit = {value} WHERE codename='base' AND is_set=TRUE ")
    conn.commit()
    return value
