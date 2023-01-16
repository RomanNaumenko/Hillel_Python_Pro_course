"""This web-application was my first steps as web-development beginner.
   This app is sort of online currency exchanger with local database(DB). There is
   a few endpoints and functions that match them with a minimal for understanding
   documentation and comments and also tools for testing as HTTP-request files.
   Besides that you can see base web-application structure in png-file 'app_structure'.
   Some functions or lines can be committed or unused but decided not to delete them."""

from flask import Flask, request
import json
import sqlite3
import datetime

app = Flask(__name__)

current_date = datetime.date.today().strftime("%Y-%m-%d")


# The line above exists for a few database queries where exact indication of today's date is necessary.


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# Below you can see some functions for connection to database, sending queries and getting the result back.
def get_db_fetchall(query: str):
    conn = sqlite3.connect('database_lite.db')
    conn.row_factory = dict_factory
    cursor = conn.execute(query)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result


def get_db_fetchone(query: str):
    conn = sqlite3.connect('database_lite.db')
    cursor = conn.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result


# Endpoints.
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.get("/currency")
def currencies():
    # Getting all currencies from DB and returning in JSON format.
    res = get_db_fetchall(f"SELECT cur_name, available_amount FROM Currency GROUP BY cur_name")
    return f"<p>Available currencies: {json.dumps(res)}</p>"


@app.get("/currency/<currency_name>")
def currency(currency_name):
    """This function returns exact currency by it`s name.
    Next commented out 7 lines is just an alternative and pretty(if I can say so) way to represent data."""
    # data_dict = {"Currency name": get_db_fetchone(f"SELECT cur_name FROM Currency WHERE cur_name = '{currency_name}'"),
    #              "Currency cost related to USD": get_db_fetchone(
    #                  f"SELECT relative_cost FROM Currency WHERE cur_name = '{currency_name}'"),
    #              "Amount of currency": get_db_fetchone(
    #                  f"SELECT available_amount FROM Currency WHERE cur_name = '{currency_name}'"),
    #              "Last price update": get_db_fetchone(
    #                  f"SELECT cur_date FROM Currency WHERE cur_name = '{currency_name}'")}
    res = get_db_fetchall(f"SELECT * FROM Currency WHERE cur_name = '{currency_name}'")
    return {"data": res, "status": "ok"}


@app.route("/currency/<currency_name>/rating", methods=["GET", "DELETE", "POST"])
def currency_review(currency_name):
    """Every user(in theory) can leave a rating for every currency and it`s price on this platform.
       By indicating currency name you can see it`s rating, post your rating and opinion or delete it
       (Deleting option of course should be only managed by admin)."""
    if request.method == "GET":
        res = get_db_fetchall(
            f"SELECT cur_name AS 'Currency Name', round(avg(rating), 2) AS 'Rating' FROM Rating WHERE cur_name = '{currency_name}' GROUP BY cur_name")
        return f"Currency name and it`s rating: {json.dumps(res)}"
    elif request.method == "DELETE":
        get_db_fetchall(
            "DELETE FROM Rating WHERE cur_name = '{currency_name}' and id = (SELECT MAX(id) FROM Rating WHERE cur_name = '{currency_name}')")
        return f"<p>The latest {currency_name} rating was deleted</p>"
    elif request.method == "POST":
        request_data = request.get_json()
        rating = request_data['rating']
        comment = request_data['comment']
        get_db_fetchall(
            f"INSERT into Rating(cur_name, rating, comment) VALUES('{currency_name}', '{rating}','{comment}')")
        return f"<p>Ok!</p>"


@app.get("/currency/trade/<currency_name_1>/<currency_name_2>")
def course_ups1_to_ups2(currency_name_1, currency_name_2):
    """This function returns relative cost of one currency to other one. From the first specified to the second one."""
    res = get_db_fetchall(f"""SELECT round(    
    (SELECT relative_cost FROM Currency WHERE cur_name='{currency_name_1}' and cur_date='{current_date}' ORDER BY cur_date DESC limit 1) /
    (SELECT relative_cost FROM Currency WHERE cur_name='{currency_name_2}' and cur_date='{current_date}' ORDER BY cur_date DESC limit 1), 2) as 'Latest exchange price'""")
    return f"<p>Trade price of the {currency_name_1} against the {currency_name_2}: \n{res}</p>"


@app.post("/currency/trade/<currency_name_1>/<currency_name_2>")
def exchange(currency_name_1, currency_name_2):
    """This function makes exchange from first specified currency in the URL to second one."""
    user_id = 1
    amount1 = request.get_json()['amount']
    user_balance = get_db_fetchall(
        f"""SELECT balance FROM Account WHERE user_id = {user_id} and cur_name = '{currency_name_1}'""")
    user_balance2 = get_db_fetchall(
        f"""SELECT balance FROM Account WHERE user_id = {user_id} and cur_name = '{currency_name_2}'""")

    actual_currency1 = get_db_fetchall(
        f"""SELECT * FROM Currency WHERE cur_name = '{currency_name_1}' ORDER BY cur_date DESC limit 1""")

    actual_currency2 = get_db_fetchall(
        f"""SELECT * FROM Currency WHERE cur_name = '{currency_name_2}' ORDER BY cur_date DESC limit 1""")

    currency1_cost_to_one_usd = actual_currency1[0]['relative_cost']
    currency2_cost_to_one_usd = actual_currency2[0]['relative_cost']
    exist_currency_1 = actual_currency1[0]['available_amount']
    exist_currency_2 = actual_currency2[0]['available_amount']

    cur2_needed = amount1 * 1.0 * (currency1_cost_to_one_usd / currency2_cost_to_one_usd)

    if (user_balance[0]['balance'] >= amount1) and (exist_currency_2 >= cur2_needed):

        get_db_fetchall(
            f"UPDATE Currency SET available_amount = {exist_currency_2 - cur2_needed} WHERE cur_date = '{current_date}' and cur_name = '{currency_name_2}'")
        get_db_fetchall(
            f"UPDATE Currency SET available_amount = {exist_currency_1 + amount1} WHERE cur_date = '{current_date}' and cur_name = '{currency_name_2}'")

        get_db_fetchall(
            f"UPDATE Account SET balance = {user_balance[0]['balance'] - amount1} WHERE user_id = {user_id} and cur_name = '{currency_name_1}'")
        get_db_fetchall(
            f"UPDATE Account SET balance = {user_balance2[0]['balance'] + cur2_needed} WHERE user_id = {user_id} and cur_name = '{currency_name_2}'")

        get_db_fetchall(f"""INSERT INTO Operation
        (user, spent_amount, datetime, gain_amount, commission, account_from, account_to, cur_to, cur_from, operation_type) VALUES
        ('{user_id}', '{amount1}', '{current_date}', '{user_balance2[0]['balance'] + cur2_needed}', '0', '1', '6', '{currency_name_2}', '{currency_name_1}', 'Exchange')""")
        return f"<p> Transaction competed successfully!</p>"
    else:
        return "<p>Not enough money</p>"


@app.get("/user")
def all_user_info():
    """The function returns from DB all user and info about them."""
    res = get_db_fetchall(f"SELECT user_id, name, login FROM User")
    return f"<p>Users: {res}</p>"


@app.get("/user/<user_id>")
def specific_user_info(user_id):
    """The function returns from DB info about one specific user by id."""
    res = get_db_fetchall(f"SELECT name as 'Username', login as 'User login' FROM User WHERE user_id = '{user_id}'"),
    return f"<p>User info: {res}</p>"


@app.get("/user/<user_id>/history")
def user_history(user_id):
    """The function returns from DB info and all done operations about one specific user by id."""
    data_dict = {"User name": get_db_fetchone(f"SELECT name FROM User WHERE user_id = '{user_id}'"),
                 "Operation number and date": get_db_fetchone(
                     f"SELECT  operation_id, datetime FROM Operation WHERE user='{user_id}'"),
                 "Amount of spent currency": get_db_fetchone(
                     f"SELECT  Operation.spent_amount, Currency.cur_name  FROM Operation join Currency WHERE "
                     f"Operation.user='{user_id}' and Operation.cur_from = Currency.cur_id"),
                 "Amount of gain currency": get_db_fetchone(f"SELECT Operation.gain_amount, Currency.cur_name "
                                                            f"FROM Operation join Currency WHERE Operation.user='{user_id}'"
                                                            f"and Operation.cur_to = Currency.cur_id")}
    return f"<p>{data_dict}</p>"


# All the endpoints below was thought out and took place in whole application structure
# but haven`t yet realized and non-functional.
@app.post("/user/transfer")
def transfer():
    return "<p>Info about user transfer</p>"


@app.route("/user/deposit", methods=["GET", "POST"])
def user_deposit():
    if request.method == "GET":
        return "<p>Info about user deposit</p>"
    elif request.method == "POST":
        return "<p>Put info about new deposit</p>"


@app.route("/user/deposit/<deposit_id>", methods=["GET", "POST"])
def user_deposit_id(deposit_id):
    if request.method == "GET":
        return f"<p>Info about user deposit: {deposit_id}</p>"
    elif request.method == "POST":
        return f"<p>Put some changes about {deposit_id}</p>"


@app.get("/user/deposit/<currency_name>")
def user_deposit_currency(currency_name):
    return f"<p>Info about {currency_name} deposit rates </p>"


if __name__ == "__main__":
    app.run(debug=True)
