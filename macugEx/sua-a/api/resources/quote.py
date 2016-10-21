# -*- coding: utf-8 -*-
import os
import time

from ..wrappers import api, Resource, wrap_page_num, wrap_object_id
from comm.db import db
import conf
from flask import request
import uuid
import re


def brief_quote(content):
    return content[:]


class QuoteResource(Resource):
    img_url = '%s/images/quote' % conf.STATIC_URL
    img_path = '%s/images/quote' % conf.STATIC_PATH

    def __init__(self, *args, **kwargs):
        super(QuoteResource, self).__init__(*args, **kwargs)

        if not os.path.exists(self.img_path):
            os.mkdir(self.img_path)

    text_field = ['title', 'brief', 'source', 'timestamp']


class QuoteList(QuoteResource):
    """
    语录列表
    """

    @wrap_page_num()
    def get(self, page, num):
        quotes = []
        for quote in db.quote.find().skip(page * num).limit(num):
            try:
                brief = brief_quote(quote['brief'])
            except KeyError:
                brief = None

            quotes.append({
                '_id': str(quote['_id']),
                'brief': brief,
                'source': quote.get('source'),
                'timestamp': quote.get('timestamp'),
                'image_url': '%s/%s' % (self.img_url, quote.get('img', '404.jpg')),
                'title': quote['title']
            })
        return {
            'code': 0,
            'quotes': quotes

        }

    def post(self):
        form = request.form
        quote = {}
        for attr in self.text_field:
            if form.get(attr):
                quote[attr] = form[attr]

        if 'image_file' in request.files:
            img_file = form.files['image_file']
            suffix = img_file.filename.split('.')[-1]
            filename = '%s.%s' % (uuid.uuid4(), suffix)
            img_file.save('%s/%s' % (self.img_path, filename))

        for attr in self.text_field:
            if form.get(attr):
                quote[attr] = form[attr]
        if quote:
            _id = db.quote.insert(quote)
            return {
                'code': 0,
                '_id': _id,
                'msg': '添加成功！'
               }
        else:
            return {
                'code': 1001,
                'msg': '添加失败'
            }


class Quote(QuoteResource):
    """
    语录
    """

    @wrap_object_id('qid')
    def get(self, qid):
        quote = db.quote.find_one({'_id': qid})
        if not quote:
            return {
                'code': 1002,
                'msg': 'quote not find',
            }
        try:
            timestamp = time.mktime(quote['maketime'].timetuple())
        except KeyError:
            timestamp = None
        return {
            'code': 0,
            'brief': quote.get('brief'),
            'source': quote.get('source'),
            'timestamp': quote.get('timestamp'),
        }

    @wrap_object_id('qid')
    def delete(self,qid):
        try:
            db.quote.delete_one({'_id': qid})
            return {
                'code': 0,
                'msg': '删除成功'
            }
        except Exception as e:
            return {
                'code': e,
                'msg': '删除失败'
            }

    @wrap_object_id('qid')
    def post(self, qid):
        form = request.form
        update = {}
        for attr in self.text_field:
            if form.get(attr):
                update[attr] = form[attr]
        if 'image_file' in request.files:
            img_file = form.files['image_file']
            suffix = img_file.filename.split('.')[-1]
            filename = '%s.%s' % (uuid.uuid4(), suffix)
            img_file.save('%s/%s' % (self.img_path, filename))
            update['img'] = filename

        if update:
            db.quote.update_one({'_id': qid}, {'$set': update})
            return {
                'code': 0,
                'msg': '修改成功！'
            }


class QuotesCount(QuoteResource):
    """
    所有语录总数
    """

    def get(self):
        return {
            'code': 0,
            'count': db.quote.count(),
        }


class QuoteTitles(QuoteResource):
    """
    按标题查询的所有语录
    """

    def get(self):
        title = request.args.get('title')
        titles = []
        regx = re.compile(title)
        titleSet = db.quote.find({'title': regx})
        if titleSet.count() == 0:
            return{
                'code': 1001,
                'msg': '没有找到您要搜索的相关基金会，请换个关键字重新搜索'
            }
        else:
            for title in titleSet:
                titles.append({
                    '_id': str(title['_id']),
                    'title': title['title'],
                    'timestamp': title['timestamp'],
                    'source': title['source'],
                    'brief': title['brief']
                })
            return {
                'code': 0,
                'titles': titles,
                'msg': '查询成功！'
            }


def __mount__():
    api.add_resource(QuoteList, '/quotes')
    api.add_resource(Quote, '/quote/<qid>')
    api.add_resource(QuotesCount, '/quote/count')
    api.add_resource(QuoteTitles, '/quote')
