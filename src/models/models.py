from . import db
from helpers import ModelMixins
import datetime
import math
from flask_login import UserMixin as UserStatusMixin


class User(db.Model, ModelMixins, UserStatusMixin):
    """
    A user owns a membership
    A user is created together with a membership
    A user remains even if his or her membership is deleted
    """
    __tablename__ = 'user'

    account_id = db.Column(db.String(255), unique=True, nullable=False)
    secret_key = db.Column(db.String(32))
    email = db.Column(db.String(255), unique=True, nullable=False)
    membership = db.relationship('Membership', uselist=False, backref='user', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        self.email = kwargs.get('email')
        self.account_id = kwargs.get('account_id')
        self.secret_key = kwargs.get('secret_key')
        self.membership = Membership(user_id=self.id)


class Membership(db.Model, ModelMixins):
    """
    A membership belongs to a user
    A membership is associated with many purchases
    A membership is deleted along with its owner(user)
    """
    __tablename__ = 'membership'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer, default=0)
    purchases = db.relationship('Purchase', backref='membership', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')
        self.points = kwargs.get('points')
        self.credits = kwargs.get('credits')

    @classmethod
    def price_to_points(cls, price):
        """
        Policy to decide price X converts into Y points
        Current policy: 1$ = 1 pt
        """
        return int(math.floor(price))


class Purchase(db.Model, ModelMixins):
    """
    A purchase is associated with a membership
    A purchase is deleted when its associated membership is deleted
    """
    __tablename__ = 'purchase'

    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    points = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'))

    def __init__(self, **kwargs):
        self.title = kwargs.get('title')
        self.price = kwargs.get('price')
        self.points = Membership.price_to_points(self.price)
        self.date = kwargs.get('date')
        self.membership_id = kwargs.get('membership_id')


