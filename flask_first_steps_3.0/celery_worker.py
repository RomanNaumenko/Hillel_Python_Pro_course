from celery import Celery
import datetime
import models
import database

app = Celery('celery_worker', broker='pyamqp://guest@localhost//')


@app.task
def task1(user_id_1, user_id_2, currency_name_1, currency_name_2, amount1, transaction_id):

    database.init_db()
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    transaction_record = models.TransactionQueue.query.filter_by(transaction_id=transaction_id).first()

    user1_balance = float(models.Account.query.filter_by(user_id=user_id_1, cur_name=currency_name_1).first().balance)
    user2_balance = float(models.Account.query.filter_by(user_id=user_id_2, cur_name=currency_name_2).first().balance)

    actual_currency1 = models.Currency.query.filter_by(cur_name=currency_name_1, cur_date=current_date).limit(1).first()
    actual_currency2 = models.Currency.query.filter_by(cur_name=currency_name_2, cur_date=current_date).limit(1).first()

    currency1_cost_to_one_usd = actual_currency1.relative_cost
    currency2_cost_to_one_usd = actual_currency2.relative_cost
    exist_currency_1 = float(actual_currency1.available_amount)
    exist_currency_2 = float(actual_currency2.available_amount)

    cur2_needed = amount1 * 1.0 * (float(currency1_cost_to_one_usd) / float(currency2_cost_to_one_usd))

    if (user1_balance >= float(amount1)) and (exist_currency_2 >= cur2_needed):

        models.Currency.query.filter_by(cur_name=currency_name_2, cur_date=current_date).update(
            dict(available_amount=exist_currency_2 - cur2_needed))
        database.db_session.commit()
        models.Currency.query.filter_by(cur_name=currency_name_1, cur_date=current_date).update(
            dict(available_amount=exist_currency_1 + amount1))
        database.db_session.commit()

        models.Account.query.filter_by(user_id=user_id_1, cur_name=currency_name_1).update(
            dict(balance=user1_balance - amount1))
        database.db_session.commit()
        models.Account.query.filter_by(user_id=user_id_2, cur_name=currency_name_2).update(
            dict(balance=user2_balance + cur2_needed))
        database.db_session.commit()

        insert_operation = models.Operation(spent_amount=amount1, datetime=current_date,
                                            gain_amount=user2_balance + cur2_needed, commission=0, account_from=1,
                                            account_to=2, cur_to=currency_name_2, cur_from=currency_name_1,
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
