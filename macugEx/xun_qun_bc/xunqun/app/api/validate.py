# -*- coding: utf-8 -*-
from functools import partial
import binascii
import re

try:
    import ujson as json
except ImportError:
    import json

__all__ = ['Form', 'StrictForm', 'StringField', 'IntField', 'FloatField', 'EmailField', 'ImageField', 'ListField']


class ValidateError(Exception):
    pass


class Field(object):
    def __init__(self, **kwargs):
        self.condition = []
        if kwargs.get('required') and 'default' in kwargs:
            raise ValueError('default are conflict with required')
        if 'enumerate' in kwargs and not getattr(kwargs['enumerate'], '__iter__', None):
            raise ValueError('enumerate is not iterable')
        if 'max_length' in kwargs and 'min_length' in kwargs and kwargs['min_length'] > kwargs['max_length']:
            raise ValueError('max_length must large that min_length')
        if 'max_value' in kwargs and 'min_value' in kwargs and kwargs['min_value'] > kwargs['max_value']:
            raise ValueError('max_value must large that min_value')

        self.kwargs = kwargs

    def __repr__(self):
        return '%s(**%r)' % (self.__class__.__name__, self.kwargs)


class FormMeta(type):
    def __new__(mcs, name, bases, attrs):
        validator = {}
        attrs['_validator'] = validator
        for key, attr in attrs.items():
            if isinstance(attr, Field):
                validator[key] = attr
                del attrs[key]

        # make the Form.__class__ is FormMeta then
        # FormMeta can use to create Form's subclass,
        # so dont't use type(name, bases, attrs),
        # it will make Form.__class__ is type.
        return type.__new__(mcs, name, bases, attrs)


class Form(object):
    """
    Form.validate the returned dictionary's key is declare in the class level and retention origin form's key.
    """
    __metaclass__ = FormMeta

    def validate(self, form):
        mutable_form = form.copy()
        try:
            for field, handle in self._validator.items():
                mutable_form[field] = handle(form.get(field, None))
        except ValidateError as e:
            return False, (field, e.message)
        return True, mutable_form

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self._validator.keys())


class StrictForm(object):
    """
    StrictForm.validate the returned dictionary's key are declare in the class level.
    """
    __metaclass__ = FormMeta

    def validate(self, form):
        data = {}
        try:
            for field, handle in self._validator.items():
                data[field] = handle(form.get(field, None))
        except ValidateError as e:
            return False, (field, e.message)
        return True, data

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self._validator.keys())


def string_required(data):
    if not data:
        raise ValidateError('is required.')


def _string_length(max=0, min=0):
    if max and min:
        def v_max_min_length(data):
            if data and (min > len(data) or len(data) > max):
                raise ValidateError('must be between %d and %d characters long.' % (min, max))

        return v_max_min_length
    elif max:
        def v_max_length(data):
            if data and len(data) > max:
                raise ValidateError('cannot be longer than %d character.' % max)

        return v_max_length
    elif min:
        def v_min_length(data):
            if data and len(data) < min:
                raise ValidateError('cannot be least than %d character.' % min)

        return v_min_length
    else:
        raise RuntimeError('Validator.Field len verify not effect but min_length or max_length is null')


def string_enumerate(data, enum=None):
    if data:
        if data not in enum:
            raise ValidateError('value %s not in enumerate' % data)


class StringField(Field):
    def __init__(self, **kwargs):
        super(StringField, self).__init__(**kwargs)
        if kwargs.get('required'):
            self.condition.append(string_required)
        if ('max_length' in kwargs) and ('min_length' in kwargs):
            self.condition.append(_string_length(max=kwargs['max_length'], min=kwargs['min_length']))
        elif 'max_length' in kwargs:
            self.condition.append(_string_length(max=kwargs['max_length']))
        elif 'min_length' in kwargs:
            if kwargs['min_length'] <= 0:
                raise ValueError('string min length must large that 0')
            self.condition.append(_string_length(min=kwargs['min_length']))
        if 'enumerate' in kwargs:
            enumerate_string = {s.decode('utf-8') if isinstance(s, str) else s for s in kwargs['enumerate']}
            if '' in enumerate_string:
                raise ValueError('"" is empty string')
            self.condition.append(partial(string_enumerate, enum=enumerate_string))
        if 'default' in kwargs:
            if not isinstance(kwargs['default'], (str, unicode)):
                raise ValueError('default must is str or unicode type')
            default = kwargs['default']
            self.default = default.decode('utf-8') if isinstance(default, str) else default

    def __call__(self, data):
        [_(data) for _ in self.condition]
        if data is None:
            return getattr(self, 'default', None)
        if isinstance(data, unicode):
            return data
        else:
            return data.decode('utf-8')


# copy from https://gist.github.com/dideler/5219706
email_match = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                          "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                          "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"), re.IGNORECASE)


class EmailField(StringField):
    def __init__(self, **kwargs):
        super(EmailField, self).__init__(**kwargs)
        if 'default' in kwargs and email_match.match(kwargs['default']) is None:
            raise ValidateError('default is Invalid email address.')

    def __call__(self, data):
        [_(data) for _ in self.condition]

        if data is None or email_match.match(data) is None:
            if string_required in self.condition:
                raise ValidateError('Invalid email address.')
            return getattr(self, 'default', None)

        if isinstance(data, unicode):
            return data
        else:
            return data.decode('utf-8')


class ImageField(Field):
    def __init__(self, **kwargs):
        super(ImageField, self).__init__(**kwargs)
        if kwargs.get('required'):
            self.condition.append(string_required)
        if 'default' in kwargs:
            if not isinstance(kwargs['default'], str):
                raise ValueError('default must is str type')
            self.default = kwargs['default']

    def __call__(self, data):
        [_(data) for _ in self.condition]
        if data is None:
            return getattr(self, 'default', None)
        try:
            return data.decode('base64')
        except binascii.Error:
            raise ValidateError('must be base64 encode string')


def number_required(data, num_type):
    try:
        if not data or not num_type(data):
            raise ValidateError('is required.')
    except ValueError:
        raise ValidateError('must be number.')


def number_range(data, num_type, max=None, min=None):
    if data:
        number = num_type(data)
        if max is not None and min is not None and not (min <= number <= max):
            raise ValidateError('must be between %d and %d.' % (min, max))
        elif max is not None and number > max:
            raise ValidateError('must be at most %d.' % max)
        elif min is not None and number < min:
            raise ValidateError('must be at least %d.' % min)


def number_enumerate(data, num_type, enum=None):
    if data:
        if num_type(data) not in enum:
            raise ValidateError('value %s not in enumerate' % data)


class IntField(Field):
    def __init__(self, **kwargs):
        super(IntField, self).__init__(**kwargs)
        if kwargs.get('required'):
            self.condition.append(partial(number_required, num_type=int))
        if ('max_value' in kwargs) and ('min_value' in kwargs):
            self.condition.append(partial(number_range, num_type=int, max=kwargs['max_value'], min=kwargs['min_value']))
        elif 'max_value' in kwargs:
            self.condition.append(partial(number_range, num_type=int, max=kwargs['max_value']))
        elif 'min_value' in kwargs:
            self.condition.append(partial(number_range, num_type=int, min=kwargs['min_value']))
        if 'enumerate' in kwargs:
            for s in kwargs['enumerate']:
                if not isinstance(s, int):
                    raise ValueError('enumerate must is int type')
            if 0 in kwargs['enumerate']:
                raise ValueError('0 is empty number')
            self.condition.append(partial(number_enumerate, num_type=int, enum=set(kwargs['enumerate'])))
        if 'default' in kwargs:
            if not isinstance(kwargs['default'], int):
                raise ValueError('default must is int type')
            self.default = kwargs['default']

    def __call__(self, data):
        try:
            [_(data) for _ in self.condition]
            if data is None:
                return getattr(self, 'default', None)
            return int(data)
        except ValueError:
            raise ValidateError('not a regular int type')


class FloatField(Field):
    def __init__(self, **kwargs):
        super(FloatField, self).__init__(**kwargs)
        if kwargs.get('required'):
            self.condition.append(partial(number_required, num_type=float))
        if ('max_value' in kwargs) and ('min_value' in kwargs):
            self.condition.append(
                partial(number_range, num_type=float, max=kwargs['max_value'], min=kwargs['min_value']))
        elif 'max_value' in kwargs:
            self.condition.append(partial(number_range, num_type=float, max=kwargs['max_value']))
        elif 'min_value' in kwargs:
            self.condition.append(partial(number_range, num_type=float, min=kwargs['min_value']))
        if 'enumerate' in kwargs:
            for s in kwargs['enumerate']:
                if not isinstance(s, float):
                    raise ValueError('enumerate must is float type')
            if 0 in kwargs['enumerate']:
                raise ValueError('0 is empty number')
            self.condition.append(partial(number_enumerate, num_type=float, enum=set(kwargs['enumerate'])))
        if 'default' in kwargs:
            if not isinstance(kwargs['default'], float):
                raise ValueError('default must is float type')
            self.default = kwargs['default']

    def __call__(self, data):
        try:
            [_(data) for _ in self.condition]
            if data is None:
                return getattr(self, 'default', None)
            return float(data)
        except ValueError:
            raise ValidateError('not a regular float type')


class ListField(Field):
    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(**kwargs)
        if len(args) != 1:
            raise ValueError('ListField only can contain one type')
        self.field = args[0]
        if not issubclass(self.field.__class__, Field):
            raise ValueError('ListField only can contain Field class')
        if kwargs.get('required'):
            self.required = True
        else:
            self.required = False

    def __call__(self, data):
        try:
            if self.required and not data:
                raise ValidateError('is required.')
            elif data is None:
                return getattr(self, 'default', None)
            if not isinstance(data, (list, tuple)):
                data = json.loads(data)
                if not isinstance(data, (list, tuple)):
                    raise ValidateError('not a iterable type')
            return [self.field(d) for d in data]
        except binascii.Error:
            raise ValidateError('base64 decode failed')
        except ValueError:
            raise ValidateError('must be list type')
