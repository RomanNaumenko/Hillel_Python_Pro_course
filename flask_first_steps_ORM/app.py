"""This newest version of previous web currency exchanger with ORM integrated.
   Used sqlalchemy. Also created 'models.py' where all models for DB interaction are located.
   Project structure are the same."""

import statistics
from flask import Flask, request
import sqlite3
import datetime
from statistics import mean
from models import db
from models import Currency, Rating, User, Operation, Account

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_lite.db'
db.init_app(app)  # DB initialization

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
    """Getting all currencies from DB and returning in JSON format."""

    result = Currency.query.all()
    return [itm.to_dict() for itm in result]


@app.get("/currency/<currency_name>")
def currency(currency_name):
    """This function returns exact currency by it`s name."""

    result = Currency.query.filter_by(cur_name=currency_name).all()
    return [itm.to_dict() for itm in result]


@app.route("/currency/<currency_name>/rating", methods=["GET", "DELETE", "POST"])
def currency_review(currency_name):
    """Every user(in theory) can leave a rating for every currency and it`s price on this platform.
           By indicating currency name you can see it`s rating, post your rating and opinion or delete it
           (Deleting option of course should be only managed by admin)."""

    if request.method == "GET":
        result = Rating.query.filter_by(cur_name=currency_name).all()
        try:
            avg_rating = round(mean([itm.rating for itm in result]), 2)
        except statistics.StatisticsError:
            avg_rating = "No data"

        return {'Currency name': currency_name, 'Average rating': avg_rating}

    elif request.method == "DELETE":
        max_id = Rating.query.filter_by(cur_name=currency_name).order_by(Rating.id).limit(1).first().id
        delete_obj = Rating(cur_name=currency_name, id=max_id)
        db.session.delete(delete_obj)
        db.session.commit()
        return f"{currency_name} latest rating was removed."

    elif request.method == "POST":
        request_data = request.get_json()
        rating = request_data['rating']
        comment = request_data['comment']
        rating_obj = Rating(cur_name=currency_name, rating=rating, comment=comment)
        with db.session as session:
            session.add(rating_obj)
            session.commit()
        return f"<p>New rating was added and successfully committed!</p>"


@app.get("/currency/trade/<currency_name_1>/<currency_name_2>")
def course_ups1_to_ups2(currency_name_1, currency_name_2):
    """This function returns relative cost of one currency to other one. From the first specified to the second one."""

    res1 = Currency.query.filter_by(cur_name=currency_name_1, cur_date=current_date).first()
    res2 = Currency.query.filter_by(cur_name=currency_name_2, cur_date=current_date).first()
    return {'value': round(res1.relative_cost / res2.relative_cost, 2)}


@app.post("/currency/trade/<currency_name_1>/<currency_name_2>")
def exchange(currency_name_1, currency_name_2):
    """This function makes exchange from first specified currency in the URL to second one."""
    user_id = 1
    amount1 = request.get_json()['amount']

    user1_balance = Account.query.filter_by(user_id=user_id, cur_name=currency_name_1).first().balance
    user2_balance = Account.query.filter_by(user_id=user_id, cur_name=currency_name_2).first().balance

    actual_currency1 = Currency.query.filter_by(cur_name=currency_name_1, cur_date=current_date).limit(1).first()
    actual_currency2 = Currency.query.filter_by(cur_name=currency_name_2, cur_date=current_date).limit(1).first()

    currency1_cost_to_one_usd = actual_currency1.relative_cost
    currency2_cost_to_one_usd = actual_currency2.relative_cost
    exist_currency_1 = actual_currency1.available_amount
    exist_currency_2 = actual_currency2.available_amount

    cur2_needed = amount1 * 1.0 * (currency1_cost_to_one_usd / currency2_cost_to_one_usd)

    if (user1_balance >= amount1) and (exist_currency_2 >= cur2_needed):

        Currency.query.filter_by(cur_name=currency_name_2, cur_date=current_date).update(
            dict(available_amount=exist_currency_2 - cur2_needed))
        db.session.commit()
        Currency.query.filter_by(cur_name=currency_name_1, cur_date=current_date).update(
            dict(available_amount=exist_currency_1 + amount1))
        db.session.commit()

        Account.query.filter_by(user_id=user_id, cur_name=currency_name_1).update(dict(balance=user1_balance - amount1))
        db.session.commit()
        Account.query.filter_by(user_id=user_id, cur_name=currency_name_2).update(
            dict(balance=user2_balance + cur2_needed))
        db.session.commit()

        insert_operation = Operation(user=user_id, spent_amount=amount1, datetime=current_date,
                                     gain_amount=user2_balance + cur2_needed, commission=0, account_from=1,
                                     account_to=6, cur_to=currency_name_2, cur_from=currency_name_1,
                                     operation_type="Exchange")

        db.session.add(insert_operation)
        db.session.commit()
        db.session.close()

        return f"<p>Exchange was successful!</p>"
    else:
        return "<p>Not enough money</p>"


@app.get("/user")
def all_user_info():
    """The function returns from DB all user and info about them."""
    user_info_dict = {}
    result = User.query.all()
    for items in result:
        user_info_dict[items.name] = items.login
    return f"Users: {user_info_dict}"


@app.get("/user/<user_id>")
def specific_user_info(user_id):
    """The function returns from DB info about one specific user by id."""
    result = User.query.filter_by(user_id=user_id).first()
    return f"User: {result.name}, login: {result.login}"


@app.get("/user/<user_id>/history")
def user_history(user_id):
    data_dict = {}

    res1 = User.query.filter_by(user_id=user_id).first()
    res2 = Operation.query.filter_by(user=user_id).first()
    res3 = db.session.query(Operation, Currency).filter(Operation.user == user_id).filter(
        Operation.cur_from == Currency.cur_name).first()
    res4 = db.session.query(Operation, Currency).filter(Operation.user == user_id).filter(
        Operation.cur_to == Currency.cur_name).first()

    data_dict["User name"] = res1.name
    data_dict["Operation date"] = res2.datetime
    data_dict["Spent amount"] = res3.Operation.spent_amount
    data_dict["Spent currency"] = res3.Currency.cur_name
    data_dict["Gain amount"] = res4.Operation.gain_amount
    data_dict["Gain currency"] = res4.Currency.cur_name

    return data_dict

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
