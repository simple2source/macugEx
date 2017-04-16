# -*- coding:utf-8 -*-

"""base orm field, archive object"""

import pymysql

class Field(object):
    def __init__(self, name, column=None, primary_key=False, unique=False, index=False,
                 nullable=None, default=None):
        self.name = name
        self.column = column
        self.primary_key = primary_key
        self.unique = unique
        self.index = index
        self.nullable = nullable
        self.default = default

    def validate(self, value):
        raise NotImplemented

    def __get__(self, instance, cls):
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        self.validate(value)
        instance.__dict__[self.name] = value


class IntField(Field):

    def __init__(self, name, column=None, primary_key=False, unique=False, index=False,
                 nullable=None, default=None, auto_increment=False):

        super(IntField).__init__(name, column, primary_key, unique, index, nullable, default)
        self.auto_increment = auto_increment

    def validate(self, value):
        if not self.nullable and value is None:
            raise TypeError('{}<{}> required'.format(self.name, self.column))
        if value is None:
            return

        if not isinstance(value, int):
            raise TypeError('{}<{}> must be int but {}'.format(self.name, self.column, type(value)))


class StringField(Field):
    def __init__(self, name, column=None, primary_key=False, unique=False, index=False,
                 nullable=False, default=None, length=45):
        super(StringField).__init__(name, column, primary_key, unique, index,
                                    nullable, default)
        self.length = length

    def validate(self, value):
        # this can use db to validate
        if not self.nullable and value is None:
            raise TypeError('{}<{}> required'.format(self.name, self.column))
        if value is None:
            return

        if not isinstance(value, str):
            raise TypeError('{}<{}> must be str but'.format(self.name, self.column, type(value)))

        if len(value) > self.length:
            raise ValueError('{}<{}> too long'.format(self.name, self.column))


class User(object):
    id = IntField('id', column='id', primary_key=True, auto_increment=True)
    name = StringField(name='name', column='name', nullable=True, unique=True, length=45)
    age = IntField(name='age', column='age')

    def __init__(self, name, id, age):
        self.id = id
        self.name = name
        self.age = age


# ---------v1 use model to save --------->

class Model(object):

    def save(self):
        fields = {}
        for name, field in self.__class__.__dict__.items():
            if isinstance(field, Field):
                fields[name] = field
        keys = []
        values = []
        for name, value in self.__dict__.items():
            if name in fields.keys():
                keys.append('{}'.format(name))
                values.append(value)
        query = '''INSERT INTO `{}` ({}) VALUE ({})'''.format(self.__class__.__table__,
                                                              ','.join(keys), ','.join('%s'))
        print(query)
        # cur.execute(query, values)


class UserV1(Model):
    __table__ = 'user'

    id = IntField('id', column='id', primary_key=True, auto_increment=True)
    name = StringField(name='name', column='name', nullable=True, unique=True, length=45)
    age = IntField(name='age', column='age')

    def __init__(self, name, id, age):
        self.id = id
        self.name = name
        self.age = age

user = UserV1(12, 'jack', 13)
user.save()


# ------------v2 ------->
"""use metaclass archive save"""


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        if '__table__' not in attrs.items():
            attrs['__table__'] = name
        mapping = {}
        primary_key = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                v.name = k
                if v.column is None:
                    v.column = k
                mapping[k] = v
                if v.primary_key:
                    primary_key.append(v)
        attrs['__mapping__'] = mapping
        attrs['__primary_key__'] = primary_key
        return super(ModelMeta).__new__(cls, name, bases, attrs)


class Model(ModelMeta):
    pass


class Engine(object):
    def __init__(self, *args, **kwarg):
        """create connect to db"""
        self.conn = pymysql.connect(*args, **kwarg)

    def _get_mapping(self, instance):
        mapping = {}


    def save(self, instance):  # save instance to db
        fields = {'`{}`'.format(k): v for k, v in instance.__dict__.items()
                  if k in instance.__dict__.mapping.keys()}
        query = 'INSERT INTO `{}` ({}) VALUES ({})'.format(instance.__class__.__table, ','.join(fields.keys()),
                                                           ','.join(['%s'] * len(fields)))
        with self.conn as cur:
            with cur:
                cur.execute(query, fields.values())

    def get(self, cls, key):  # select by primary key model have unique primary key
        pass

    def update(self, instance):  # update to primary key
        pass

    def select(self, cls):
        pass

    def delete(self, instance):
        pass
