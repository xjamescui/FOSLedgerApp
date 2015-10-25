from . import db
from helpers import ModelMixins
import datetime
import math
from flask_login import UserMixin as UserStatusMixin


class User(db.Model, ModelMixins, UserStatusMixin):
    """
    A user (e.g. Frontier) is a customer of LoyaltyPlus
    A user is associated with one account (assuming this for now)
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

    @property
    def credits(self):
        return sum([m.credits for m in self.members]) if self.members else 0

    @property
    def purchases(self):
        return [p for m in self.members for p in m.purchases]


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

    def credits_attainable_with(self, points):
        return points / self._points_per_credit

    def add_points(self, pts):
        return pts > 0 and self.update(points=self.points + pts)

    def subtract_points(self, pts):
        return 0 < pts <= self.points and self.update(points=self.points - pts)

    def add_credits(self, c):
        return c > 0 and self.update(credits=self.credits + c)

    def subtract_credits(self, c):
        return 0 < c <= self.credits and self.update(credits=self.credits - c)

    def convert_points_to_these_credits(self, credits_desired):
        pts = self.points_needed_for(credits_desired)
        return self.is_reward_eligible() and self.subtract_points(pts) and self.add_credits(credits_desired)

    @classmethod
    def price_to_points(cls, price):
        """
        Policy to decide price X converts into Y points
        Current policy: 1$ = 1 pt
        """
        return int(math.floor(price))

    @classmethod
    def points_needed_for(cls, credits_desired):
        return credits_desired * cls._points_per_credit


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
