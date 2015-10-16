from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

'''
Custom CRUD Mixin to use with models
'''


class CRUDMixin(object):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    @classmethod
    def get_by_id(cls, id):
        if any(
                (isinstance(id, basestring) and id.isdigit(),
                 isinstance(id, (int, float))),
        ):
            return cls.query.get(int(id))
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()


'''
Models
'''


class User(db.Model, CRUDMixin):
    """
    A user owns a membership
    A user is created together with a membership
    A user remains even if his or her membership is deleted
    """
    __tablename__ = 'user'

    account_id = db.Column(db.String(255), unique=True, nullable=False)
    secret_key = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    membership = db.relationship('Membership', uselist=False, backref='user', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        self.email = kwargs.get('email')
        self.account_id = kwargs.get('account_id')
        self.secret_key = kwargs.get('secret_key')

    def add_membership(self):
        self.membership = Membership(user_id=self.id).save()
        return self.membership


class Membership(db.Model, CRUDMixin):
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


    _points_per_dollar = 10
    _redeemable_threshold = 100  # redeem at least 100 pts

    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')
        self.points = kwargs.get('points')
        self.credits = kwargs.get('credits')


class Purchase(db.Model, CRUDMixin):
    """
    A purchase is associated with a membership
    A purchase is deleted when its associated membership is deleted
    """
    __tablename__ = 'purchase'

    price = db.Column(db.Float)
    date = db.Column(db.DateTime)
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'))

    def __init__(self, **kwargs):
        self.price = kwargs.get('price')
        self.date = kwargs.get('date', None)
        self.membership_id = kwargs.get('membership_id')
