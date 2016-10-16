# -*- coding: utf-8 -*-
"""orm实现 version 1"""
import datetime
from pymysql.cursors import DictCursor
from pool import ConnectionPool


class Field:
    def __init__(self, name=None, pk=False, nullable=True, index=False, unique=False):
        self.column = name
        self.pk = pk
        self.nullable = nullable
        self.index = index
        self.unique = unique
        self.name = None

    def to_sql(self, value):
        raise NotImplementedError()

    def validate(self, value):
        return True, ''

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        ok, msg = self.validate(value)
        if not ok:
            raise TypeError(msg)
        instance.__dict__[self.name] = value


class IntField(Field):
    def __init__(self, name=None, pk=False, nullable=True, index=False, unique=False, auto_inc=False):
        super().__init__(name, pk, nullable, index, unique)
        self.auto_inc = auto_inc

    def to_sql(self, value):
        return str(value)

    def validate(self, value):
        if value is not None and not isinstance(value, int):
            return False, 'require type int, but {}'.format(type(value))
        return True, ''


class StringField(Field):
    def __init__(self, name=None, pk=False, nullable=True, index=False, unique=False, length=45):
        super().__init__(name, pk, nullable, index, unique)
        self.length = length

    def to_sql(self, value):
        return '"{}"'.format(value)

    def validate(self, value):
        if value is not None:
            if isinstance(value, str):
                if len(value) <= self.length:
                    return True, ''
                return False, 'max length is {}, but {}'.format(self.lenght, len(value))
            return False, 'require str, but {}'.format(type(value))
        return True, ''


class Meta(type):
    def __new__(cls, name, bases, attrs):
        mapping = []
        pk = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                v.name = k
                if v.column is None:
                    v.column = k
                if v.pk:
                    pk.append(v)
                mapping.append(v)
        attrs['__mapping__'] = mapping
        attrs['__pk__'] = pk
        if attrs.get('__table__') is None:
            attrs['__table__'] = name
        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=Meta):
    def __init__(self, **kwargs):
        for field in self.__mapping__:
            setattr(self, field.name, kwargs.get(field.name))


class DB:
    def __init__(self, **kwargs):
        kwargs['cursorclass'] = DictCursor
        self.pool = ConnectionPool(**kwargs)

    def get(self, cls, pk):
        if len(cls.__pk__) != 1:
            raise RuntimeError('pk is not 1')
        fields = ['`{}` AS `{}`'.format(field.column, field.name) for field in cls.__mapping__]
        sql = 'select {} from `{}` where {}={}'.format(', '.join(fields), cls.__table__, cls.__pk__[0].column, cls.__pk__[0].to_sql(pk))
        print(sql)
        with self.pool() as cur:
            cur.execute(sql)
            result = cur.fetchone()
            return cls(**result)

    def query(self, cls):
        return Query(cls, self)

    def update(self, instance):
        if not isinstance(instance, Model):
            raise Exception('{} is not instance of Model'.format(instance.__class__))
        where = []
        for pk in instance.__pk__:
            v = getattr(instance, pk.name)
            if v is None:
                raise RuntimeError('pk is not null')
            where.append('`{}`={}'.format(pk.column, pk.to_sql(v)))
        kv = {}
        for field in instance.__mapping__:
            if isinstance(field, Field):
                v = getattr(instance, field.name)
                if v is None:
                    if not field.nullable:
                        raise ValueError('{} not nullable or auto inc'.format(field.name))
                    kv[field.column] = 'null'
                else:
                    kv[field.column] = field.to_sql(v)
        sql = 'update `{}` set {} where {}'.format(instance.__table__,
                                                   ', '.join('`{}`={}'.format(k, v) for k, v in kv.items()),
                                                   ' and '.join(where))
        print(sql)
        with self.pool() as cur:
            return cur.execute(sql)

    def insert(self, instance):
        if not isinstance(instance, Model):
            raise Exception('{} is not instance of Model'.format(instance.__class__))
        fields = []
        values = []
        for field in instance.__mapping__:
            if isinstance(field, Field):
                v = getattr(instance, field.name)
                if v is None:
                    if not field.nullable and not getattr(field, 'auto_inc', False):
                        raise ValueError('{} not nullable or auto inc'.format(field.name))
                else:
                    fields.append('`{}`'.format(field.column))
                    values.append(field.to_sql(v))
        sql = '''insert into `{}`({}) value({})'''.format(instance.__table__, ', '.join(fields), ', '.join(values))
        print(sql)
        with self.pool() as cur:
            cur.execute(sql)


class Query:
    def __init__(self, model, session):
        self.where_expression = None
        self.session = session
        self.model = model
        self._offset = 0
        self._limit = 0

    def offset(self, offset):
        self._offset = offset
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    def where(self):
        return Condition(Expression(self))

    def _to_select(self):
        fields = ['`{}` AS `{}`'.format(field.column, field.name) for field in self.model.__mapping__]
        sql = 'select {} from `{}`'.format(', '.join(fields), self.model.__table__)
        return sql

    def _to_delete(self):
        return 'delete from `{}`'.format(self.model.__table__)

    def _add_where_expression(self, sql):
        if self.where_expression:
            sql = '{} where {}'.format(sql, self.where_expression)
        return sql

    def _add_limit(self, sql):
        limit = ''
        if self._offset > 0 and self._limit > 0:
            limit = '{},{}'.format(self._offset, self._limit)
        elif self._limit > 0:
            limit = str(self._limit)
        if limit:
            sql = '{} limit {}'.format(sql, limit)
        return sql

    def all(self):
        sql = self._to_select()
        sql = self._add_where_expression(sql)
        sql = self._add_limit(sql)
        with self.session.pool() as cur:
            cur.execute(sql)
            return [self.model(**result) for result in cur.fetchall()]

    def one(self):
        sql = self._to_select()
        sql = self._add_where_expression(sql)
        sql = '{} limit 1'.format(sql)
        with self.session.pool() as cur:
            cur.execute(sql)
            return self.model(**cur.fetchone())

    def delete(self):
        sql = self._to_delete()
        sql = self._add_where_expression(sql)
        with self.session.pool() as cur:
            return cur.execute(sql)


class Condition:
    def __init__(self, expression):
        self.expression = expression

    def eq(self, field, value):
        sql = '`{}`={}'.format(field.column, field.to_sql(value))
        self.expression.add(sql)
        return self.expression

    def le(self, field, value):
        sql = '`{}`<={}'.format(field.column, field.to_sql(value))
        self.expression.add(sql)
        return self.expression


class Expression:
    def __init__(self, query):
        self.tokens = []
        self.query = query

    def add(self, token):
        self.tokens.append(token)

    def and_(self):
        self.add('and')
        return Condition(self)

    def or_(self):
        self.add('or')
        return Condition(self)

    def not_(self):
        self.add('not')
        return Condition(self)

    def end(self):
        self.query.where_expression = ' '.join(self.tokens)
        return self.query


class Author(Model):
    __table__ = 'author'

    id = IntField(pk=True, auto_inc=True)
    name = StringField(length=45)
    country = StringField(length=45)

    def __repr__(self):
        return 'Author<id={}, name={}, country={}>'.format(self.id, self.name, self.country)


if __name__ == '__main__':
    db = DB(host='127.0.0.1',
            port=3306,
            user='root',
            password='123456',
            database='demo',
            cursorclass=DictCursor)

    # author = db.get(Author, 16)
    #
    # print(author)

    results = db.query(Author).where().eq(Author.name, 'comyn').and_().le(Author.id, 18).end().offset(2).limit(1).all()
    # select * from `author` where name="comyn" and id < 18;
    for r in results:
        print(r)