# -*- coding: utf-8 -*-
"""
接口验证表单
"""
from app.api.validate import StrictForm, StringField, ListField, IntField, ImageField


class ServBind(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    serv_id = StringField(required=True, min_length=1, max_length=20)
    password = StringField(required=True, min_length=1, max_length=20)


class QuestionNew(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    title = StringField()
    # label = ListField(StringField(required=True))


class QuestionList(StrictForm):
    question_id = StringField(min_length=24, max_length=24)
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=20)
    identify = StringField()
    label = StringField()
    sort = IntField(default=-1)


class ServId(StrictForm):
    serv_id = StringField(required=True, min_length=1, max_length=20)


class QuestionId(StrictForm):
    question_id = StringField(min_length=24, max_length=24)


class GetTasks(StrictForm):
    question_id = StringField(min_length=24, max_length=24)
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=20)
    sort = IntField(default=-1)
    identify = StringField()


class GetMessages(StrictForm):
    message_id = StringField(min_length=24, max_length=24)
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=20)
    sort = IntField(default=-1)
    identify = StringField()


class TextMessage(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    sender = StringField(required=True, max_length=24)
    sender_type = IntField(required=True, enumerate=(1, 2))
    text = StringField(required=True)


class ImageMessage(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    sender = StringField(required=True, max_length=24)
    sender_type = IntField(required=True, enumerate=(1, 2))
    image = ImageField(required=True)


class GetItems(StrictForm):
    item_id = StringField(min_length=24, max_length=24)
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=20)
    sort = IntField(default=-1)
    identify = StringField()
