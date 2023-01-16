"""Like the other time I can tell 'flask_first_steps_3.0' is laconic literary name.
   This project grows not in width but in depth. Code became more neat and optimize
   because of Celery technology. What`s new in version 3.0:
   The currency exchange transaction completely moved to the Celery task:
   - edited SqlAlchemy connections, initialization, models, migrations;
   - connected Celery;
   - the transaction logic removed from the endpoint and transmitted to the task;
   - in the transaction endpoint described the start of the task.
   Besides that DB was changed to Postgresql. It was decided to abandon the idea of
   implementation of endpoints and logic related to deposits and it`s further realization
   because of it`s unnecessary functionality."""

import statistics
import uuid

from flask import Flask, request
import datetime
from statistics import mean
import database
import models
from models import Currency, Rating, User, Operation
from celery_worker import task1


app = Flask(__name__)

current_date = datetime.date.today().strftime("%Y-%m-%d")
# The line above exists for a few database queries where exact indication of today's date is necessary.


# Endpoints.
@app.get('/testing')
def testing():
    """This is only Celery testing function."""
    user_id = 1
    cur_1 = 'UAH'
    cur_2 = 'ZLT'
    amount = 100
    task_obj = task1.apply_async(args=[user_id, cur_1, cur_2, amount])
    return str(task_obj)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.get("/currency")
def currencies():
    """Getting all currencies from DB."""

    database.init_db()
    result = Currency.query.all()
    if not result:
        return "<p>Nothing found</p>"
    return [itm.to_dict() for itm in result]


@app.get("/currency/<currency_name>")
def currency(currency_name):
    """This function returns exact currency by it`s name."""

    database.init_db()
    result = Currency.query.filter_by(cur_name=currency_name).all()
    return [itm.to_dict() for itm in result]


@app.route("/currency/<currency_name>/rating", methods=["GET", "DELETE", "POST"])
def currency_review(currency_name):
    """Function let user see currency ratings, post ratings by oneself and delete it
    (administration simplification because session possabilities still absense here)."""
    database.init_db()
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
        database.db_session.delete(delete_obj)
        database.db_session.session.commit()
        return f"{currency_name} latest rating was removed."

    elif request.method == "POST":
        request_data = request.get_json()
        rating = request_data['rating']
        comment = request_data['comment']
        rating_obj = Rating(cur_name=currency_name, rating=rating, comment=comment)
        with database.db_session as session:
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
    """This function makes exchange from first specified currency in the URL to second one.
       Now the currency exchange transaction process itself completely moved to Celery worker."""

    request_data = request.get_json()
    user_id_1 = request_data['data']['id_user_1']
    user_id_2 = request_data['data']['id_user_2']
    amount1 = request_data['data']['amount_currency_1']

    transaction_id = uuid.uuid4()
    database.init_db()
    queue_record = models.TransactionQueue(transaction_id=str(transaction_id), status='In queue')
    database.db_session.add(queue_record)
    database.db_session.commit()

    task_obj = task1.apply_async(args=[user_id_1, user_id_2, currency_name_1, currency_name_2, amount1, transaction_id])
    return {'task_id': str(task_obj)}


@app.get("/user")
def all_user_info():
    """The function returns from DB all user and info about them."""

    database.init_db()
    user_info_dict = {}
    result = User.query.all()
    for items in result:
        user_info_dict[items.name] = items.login
    return f"Users: {user_info_dict}"


@app.get("/user/<user_id>")
def specific_user_info(user_id):
    """The function returns from DB info about one specific user by id."""

    database.init_db()
    result = User.query.filter_by(user_id=user_id).first()
    return f"User: {result.name}, login: {result.login}"


@app.get("/user/<user_id>/history")
def user_history(user_id):
    """The function returns from DB info and all done operations about one specific user by id."""

    database.init_db()
    data_dict = {}

    res1 = User.query.filter_by(user_id=user_id).first()
    res2 = Operation.query.filter_by(user=user_id).first()
    res3 = database.db_session.query(Operation, Currency).filter(Operation.user == user_id).filter(
        Operation.cur_from == Currency.cur_name).first()
    res4 = database.db_session.query(Operation, Currency).filter(Operation.user == user_id).filter(
        Operation.cur_to == Currency.cur_name).first()

    data_dict["User name"] = res1.name
    data_dict["Operation date"] = res2.datetime
    data_dict["Spent amount"] = res3.Operation.spent_amount
    data_dict["Spent currency"] = res3.Currency.cur_name
    data_dict["Gain amount"] = res4.Operation.gain_amount
    data_dict["Gain currency"] = res4.Currency.cur_name

    return data_dict


@app.teardown_appcontext
def shutdown_session(exception=None):
    database.db_session.remove()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
