# -*- coding: utf-8 -*-
import datetime
import time
import conf
import os
from flask import request
import lxml.html as lh
from lxml.html.clean import clean_html

from ..wrappers import api, Resource, wrap_object_id, wrap_page_num, reqparse
from comm.db import db
import uuid
import re

parser = reqparse.RequestParser()


def content_news(content):
    doc = lh.fromstring(content)
    doc = clean_html(doc)
    return doc.text_content()[:]


class NewResource(Resource):
    img_url = '%s/images/new' % conf.STATIC_URL
    img_path = '%s/images/new' % conf.STATIC_PATH
    default_img_url = '%s/images/avator.png' % conf.STATIC_URL

    def __init__(self, *args, **kwargs):
        super(NewResource, self).__init__(*args, **kwargs)

        if not os.path.exists(self.img_path):
            os.mkdir(self.img_path)

    text_field = ['title', 'content', 'source', 'timestamp', '_id']

    def fill_text_field(self, news, data):
        """
            src = {'name': 'mick'}
            dest = {}
            self.fill_text_field(src, dest)
            print dest  # {'name': 'testNews', 'content': 'default content', 'timestamp': None ..
        """
        for attr in self.text_field:
            data[attr] = news.get(attr)
        return data


class NewsList(NewResource):
    """
    资讯列表
    """

    @wrap_page_num()
    def get(self, page, num):
        news = []
        for new in db.news.find().skip(page * num).limit(num):
            try:
                content = content_news(new['content'])
            except KeyError:
                content = None
            news.append({
                '_id': str(new['_id']),
                'title': new.get('title'),
                'content': content,
                'timestamp': new.get('timestamp'),
                'source': new.get('source')
            })
        return {
            'code': 0,
            'news': news
        }

    def post(self):
        form = request.form
        new = {}
        if not form:
            return {
                'code': 1003,
                'msg': 'form data is empty'
            }
        for attr in self.text_field:
            if form.get(attr):
                new[attr] = form[attr]

        if 'image_file' in request.files:
            img_file = form.files['image_file']
            suffix = img_file.filename.split('.')[-1]
            filename = '%s.%s' % (uuid.uuid4(), suffix)
            img_file.save('%s/%s' % (self.img_path, filename))
            new['img'] = filename
        for attr in self.text_field:
            if form.get(attr):
                new[attr] = form[attr]
        if new:
            new['timestamp'] = datetime.datetime.now()
            _id = db.news.insert(new)
            return {
                'code': 0,
                '_id': _id,
                'msg': '添加成功'
            }
        else:
            return {
                'code': 101,
                'msg': '添加失败'
            }


class News(NewResource):
    """
    资讯
    """

    @wrap_object_id('newid')
    def get(self, newid):
        new = db.news.find_one({'_id': newid})

        if not new:
            return {
                'code': 1002,
                'msg': 'news not find',
            }
        try:
            timestamp = time.mktime(new['timestamp'].timetuple())
        except KeyError:
            timestamp = None
        return {
            'code': 0,
            '_id': new.get('_id'),
            'title': new.get('title'),
            'content': new.get('content'),
            'source': new.get('source'),
            'timestamp': timestamp,
        }

    @wrap_object_id('newid')
    def delete(self, newid):
        try:
            db.news.delete_one({'_id': newid})
            return {
                'code': 0,
                'msg': '删除成功！'
            }
        except Exception as e:
            return {
                'code': e,
                'msg': '删除失败'
            }

    @wrap_object_id('newid')
    def post(self, newid):
        form_data = request.form
        if not form_data:
            return {
                'code': 1003,
                'msg': 'form data is empty'
            }

        new = {}
        for attr in self.text_field:
            if form_data.get(attr):
                new[attr] = form_data[attr]
        db.news.update_one({'_id': newid}, {'$set': new})
        return {
            'code': 0,
            'msg': '更新成功'
        }


class NewsCount(Resource):
    """
    所有资讯总数
    """

    def get(self):
        return {
            'code': 0,
            'count': db.news.count(),
        }


class NewsSearch(NewResource):
    """
    资讯搜索
    @:param title
    """

    def get(self):
        title = request.args.get('title')
        titles = []
        titleSet = db.news.find({'title': re.compile(title)})
        if titleSet.count() == 0:
            return {
                'code': 1001,
                'msg': '没有您要搜索的标题，请换个关键字重新搜索'
                }
        for title in titleSet:
            titles.append({
                '_id': str(title['_id']),
                'title': title['title'],
                'timestamp': title['timestamp'],
                'source': title['source'],
                'content': title['content']
            })

        return {
            'code': 0,
            'titles': titles,
            'msg': '查询成功！'
        }


def __mount__():
    api.add_resource(NewsList, '/news')
    api.add_resource(News, '/news/<newid>')
    api.add_resource(NewsCount, '/news/count')
    api.add_resource(NewsSearch, '/news/search')

