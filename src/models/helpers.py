from . import db
from collections import OrderedDict

"""
Serializer that serializes model data into JSON
"""


class Serializer(object):
    def serialize(self, **kwargs):
        import unicodedata
        result, ignore_keys = OrderedDict(), kwargs.get('ignore', set())
        keys = [k for k in self.__mapper__.c.keys() if k not in ignore_keys]
        for key in keys:
            result[key] = getattr(self, key)
            if isinstance(result[key], unicode):
                # convert unicode string to regular ascii string
                result[key] = unicodedata.normalize('NFKD', result[key]).encode('ascii', 'ignore')
            elif hasattr(result[key], 'isoformat'):
                # avoid datetime not serializable errors
                result[key] = result[key].isoformat()
        return result


"""
Custom CRUD Mixin to use with models
"""


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


class ModelMixins(CRUDMixin, Serializer):
    pass
