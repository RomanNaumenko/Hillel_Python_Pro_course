from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # SQLAlchemy object


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)  # , db.ForeignKey('user.id')
    balance = db.Column(db.REAL, nullable=False)
    cur_name = db.Column(db.String(3), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user id': self.user_id,
            'balance': self.balance,
            'currency name': self.cur_name,
        }


class Currency(db.Model):
    cur_id = db.Column(db.Integer, primary_key=True, nullable=False)
    cur_name = db.Column(db.String(3), nullable=False)
    relative_cost = db.Column(db.REAL, nullable=False)
    available_amount = db.Column(db.REAL, nullable=False)
    cur_date = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            'currency id': self.cur_id,
            'currency name': self.cur_name,
            'relative cost': self.relative_cost,
            'available amount': self.available_amount,
            'currency date': self.cur_date
        }


class Deposite(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    opening_date = db.Column(db.String(10), nullable=False)
    closing_date = db.Column(db.String(10), nullable=False)
    balance = db.Column(db.REAL, nullable=False)
    interest_rate = db.Column(db.Integer, nullable=False)
    storage_conditions = db.Column(db.Integer, nullable=False)
    storage_cur = db.Column(db.String(3), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'date of opening': self.opening_date,
            'date of closing': self.closing_date,
            'balance': self.balance,
            'interest rate': self.interest_rate,
            'storage conditions': self.storage_conditions,
            'storage currency': self.storage_cur
        }


class Operation(db.Model):
    user = db.Column(db.Integer, primary_key=True, nullable=False)
    spent_amount = db.Column(db.REAL, nullable=False)
    datetime = db.Column(db.String(10), nullable=False)
    gain_amount = db.Column(db.REAL, nullable=False)
    commission = db.Column(db.REAL, nullable=False)
    account_from = db.Column(db.Integer, nullable=False)
    account_to = db.Column(db.Integer, nullable=False)
    cur_to = db.Column(db.Integer, nullable=False)
    cur_from = db.Column(db.Integer, nullable=False)
    operation_type = db.Column(db.String(30), nullable=False)

    def to_dict(self):
        return {
            'user': self.user,
            'spent amount': self.spent_amount,
            'datetime': self.datetime,
            'gain amount': self.gain_amount,
            'commission': self.commission,
            'account from': self.account_from,
            'account to': self.account_to,
            'currency to': self.cur_to,
            'currency from': self.cur_from,
            'operation type': self.operation_type
        }


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    cur_name = db.Column(db.String(3), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'currency name': self.cur_name,
            'rating': self.rating,
            'comment': self.comment
        }


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    login = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'user id': self.user_id,
            'name': self.name,
            'login': self.login,
            'password': self.password
        }