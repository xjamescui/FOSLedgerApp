from . import db
from helpers import ModelMixins
import datetime
import math
from flask_login import UserMixin as UserStatusMixin


class User(db.Model, ModelMixins, UserStatusMixin):
    """
    A user (e.g. Frontier) is a customer of LoyaltyPlus
    A user has many members
    A user remains even if all of its members are gone
    """
    __tablename__ = 'user'

    account_id = db.Column(db.String(255), unique=True, nullable=False)
    secret_key = db.Column(db.String(32))
    members = db.relationship('Member', backref='user', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        self.account_id = kwargs.get('account_id')
        self.secret_key = kwargs.get('secret_key')

    @property
    def points(self):
        return sum([m.points for m in self.members]) if self.members else 0


class Member(db.Model, ModelMixins):
    """
    A member is a customer of user
    A member belongs to a customer of LoyaltyPlus
    A member has many purchases
    A member is deleted along with the customer
    """
    __tablename__ = 'member'

    email = db.Column(db.String(255), unique=True, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('user.account_id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer, default=0)
    purchases = db.relationship('Purchase', backref='member', cascade='all, delete-orphan')

    _points_per_credit = 10  # 100 pts for $10 ==> 10 pts for $1

    def __init__(self, **kwargs):
        self.email = kwargs.get('email')
        self.account_id = kwargs.get('account_id')
        self.points = kwargs.get('points')
        self.credits = kwargs.get('credits')

    def is_reward_eligible(self):
        return self.points >= 100

    def max_reward_eligible(self):
        if self.is_reward_eligible():
            return self.credits_attainable_with(self.points)
        return 0

    def points_needed_for(self, credits_desired):
        return credits_desired * self._points_per_credit

    def credits_attainable_with(self, points):
        return points / self._points_per_credit

    def convert_points_for(self, credits_desired):
        if self.is_reward_eligible():
            pts = self.points_needed_for(credits_desired)
            if self.points >= pts:
                self.update(points=self.points - pts, credits=self.credits + credits_desired)
                return True
        return False

    @classmethod
    def price_to_points(cls, price):
        """
        Policy to decide price X converts into Y points
        Current policy: 1$ = 1 pt
        """
        return int(math.floor(price))


class Purchase(db.Model, ModelMixins):
    """
    A purchase belongs to a member
    A purchase is deleted when its member is deleted
    """
    __tablename__ = 'purchase'

    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    points = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    def __init__(self, **kwargs):
        self.title = kwargs.get('title')
        self.price = kwargs.get('price')
        self.points = Member.price_to_points(self.price)
        self.date = kwargs.get('date')
        self.member_id = kwargs.get('member_id')