import os
from celery import Celery
import datetime
import models
import database

# app = Celery('celery_worker', broker='pyamqp://guest@localhost//')
app = Celery('celery_worker', broker=os.environ.get('RABBIT_CONNECTION_STR'))


@app.task
def task1(user_id_1, user_id_2, currency_name_1, currency_name_2, amount1, transaction_id):
    database.init_db()
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    transaction_record = models.TransactionQueue.query.filter_by(transaction_id=transaction_id).first()

    try:
        user1_balance = float(
            models.Account.query.filter_by(user_id=user_id_1, cur_name=currency_name_1).first().balance)
        user2_balance = float(
            models.Account.query.filter_by(user_id=user_id_2, cur_name=currency_name_2).first().balance)
    except AttributeError as e:
        transaction_record.status = 'failed'
        database.db_session.commit()
        return 'failed'

    actual_currency1 = models.Currency.query.filter_by(cur_name=currency_name_1, cur_date=current_date).limit(1).first()
    actual_currency2 = models.Currency.query.filter_by(cur_name=currency_name_2, cur_date=current_date).limit(1).first()

    currency1_cost_to_one_usd = float(actual_currency1.relative_cost)
    currency2_cost_to_one_usd = float(actual_currency2.relative_cost)
    exist_currency_1 = float(actual_currency1.available_amount)
    exist_currency_2 = float(actual_currency2.available_amount)

    cur1_needed = float(amount1) * 1.0 * currency1_cost_to_one_usd / currency2_cost_to_one_usd

    if (user1_balance >= cur1_needed) and (exist_currency_1 >= cur1_needed):

        currency_1_available_amount = round((exist_currency_1 - cur1_needed), 2)
        currency_2_available_amount = round((exist_currency_2 + amount1), 2)

        models.Currency.query.filter_by(cur_name=currency_name_2, cur_date=current_date).update(
            dict(available_amount=currency_2_available_amount))
        models.Currency.query.filter_by(cur_name=currency_name_1, cur_date=current_date).update(
            dict(available_amount=currency_1_available_amount))
        database.db_session.commit()

        account_1_balance = round((user1_balance - cur1_needed), 2)
        account_2_balance = round((user2_balance + amount1), 2)

        models.Account.query.filter_by(user_id=user_id_1, cur_name=currency_name_1).update(
            dict(balance=account_1_balance))
        models.Account.query.filter_by(user_id=user_id_2, cur_name=currency_name_2).update(
            dict(balance=account_2_balance))
        database.db_session.commit()

        insert_operation = models.Operation(spent_amount=amount1, datetime=current_date,
                                            gain_amount=str(round(cur1_needed, 2)), commission=0,
                                            account_from=user_id_1,
                                            account_to=user_id_2, cur_from=currency_name_1, cur_to=currency_name_2,
                                            operation_type="Exchange")
        try:
            database.db_session.add(insert_operation)
            transaction_record.status = "Success"
            database.db_session.add(transaction_record)
            database.db_session.commit()
            database.db_session.close()
        except Exception as e:
            return "Error: " + str(e)
        return f"<p>Exchange was successful!</p>"
    else:
        transaction_record.status = "Failed"
        database.db_session.add(transaction_record)
        database.db_session.commit()
        return "<p>Not enough money</p>"
