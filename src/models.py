from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(255), unique=True)
    secret_key = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    membership = db.relationship('Membership', uselist=False, backref='user')
    purchases = db.relationship('Purchase', backref='user')

    def __init__(self):
        pass


class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    points = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer, default=0)

    _points_per_dollar = 10
    _redeemable_threshold = 100  # redeem at least 100 pts

    def __init__(self):
        pass


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self):
        pass
