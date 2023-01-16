from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, nullable=False)  # , ForeignKey('user.id')
    balance = Column(String(50), nullable=False)
    cur_name = Column(String(3), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user id': self.user_id,
            'balance': self.balance,
            'currency name': self.cur_name,
        }


class Currency(Base):
    __tablename__ = 'currencies'
    cur_id = Column(Integer, primary_key=True, nullable=False)
    cur_name = Column(String(3), nullable=False)
    relative_cost = Column(String(10), nullable=False)
    available_amount = Column(String(10), nullable=False)
    cur_date = Column(String(10), nullable=False)

    def to_dict(self):
        return {
            'currency id': self.cur_id,
            'currency name': self.cur_name,
            'relative cost': self.relative_cost,
            'available amount': self.available_amount,
            'currency date': self.cur_date
        }


class Deposite(Base):
    __tablename__ = 'deposits'
    id = Column(Integer, primary_key=True, nullable=False)
    opening_date = Column(String(10), nullable=False)
    closing_date = Column(String(10), nullable=False)
    balance = Column(String(10), nullable=False)
    interest_rate = Column(Integer, nullable=False)
    storage_conditions = Column(Integer, nullable=False)
    storage_cur = Column(String(3), nullable=False)

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


class Operation(Base):
    __tablename__ = 'operations'
    operation_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    spent_amount = Column(String(10), nullable=False)
    datetime = Column(String(10), nullable=False)
    gain_amount = Column(String(10), nullable=False)
    commission = Column(Integer, nullable=False)
    account_from = Column(Integer, nullable=False)
    account_to = Column(Integer, nullable=False)
    cur_to = Column(String(3), nullable=False)
    cur_from = Column(String(3), nullable=False)
    operation_type = Column(String(30), nullable=False)

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


class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True, nullable=False)
    cur_name = Column(String(3), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'currency name': self.cur_name,
            'rating': self.rating,
            'comment': self.comment
        }


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(20), nullable=False)
    login = Column(String(20), nullable=False)
    password = Column(String(20), nullable=False)

    def to_dict(self):
        return {
            'user id': self.user_id,
            'name': self.name,
            'login': self.login,
            'password': self.password
        }


class TransactionQueue(Base):
    __tablename__ = 'transaction_queue'
    id = Column(Integer, primary_key=True, nullable=False)
    transaction_id = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'transaction id': self.transaction_id,
            'status': self.status
        }
