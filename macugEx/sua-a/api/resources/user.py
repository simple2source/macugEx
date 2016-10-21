# -*- coding: utf-8 -*-
import os
import uuid
import time
import datetime
import re

from flask import request

from ..wrappers import api, Resource, wrap_object_id, wrap_page_num, reqparse
from comm.db import db
from comm.misc import distance
import conf

parser = reqparse.RequestParser()


class UserResource(Resource):
    img_url = '%s/images/user' % conf.STATIC_URL
    img_path = '%s/images/user' % conf.STATIC_PATH
    default_img_url = '%s/images/avator.png' % conf.STATIC_URL

    def __init__(self, *args, **kwargs):
        super(UserResource, self).__init__(*args, **kwargs)

        if not os.path.exists(self.img_path):
            os.mkdir(self.img_path)

    text_field = ['name', 'grade', 'specialty', 'phone', 'career', 'profession', 'gender', 'OpenId']

    def fill_text_field(self, src, dest):
        """
            src = {'name': 'mick'}
            dest = {}
            self.fill_text_field(src, dest)
            print dest  # {'name': 'mick', 'grade': None, 'phone': None ..
        """
        for attr in self.text_field:
            dest[attr] = src.get(attr)
        return dest


class UserInfo(UserResource):
    """
    用户校友信息
    """

    @wrap_object_id('userid')
    def post(self, userid):
        form = request.form
        user = {}
        for attr in self.text_field:
            if attr in form:
                user[attr] = form[attr]
        if 'image_file' in request.files:
            img_file = form.files['image_file']
            suffix = img_file.filename.split('.')[-1]
            filename = '%s.%s' % (uuid.uuid4(), suffix)
            img_file.save('%s/%s' % (self.img_path, filename))
            user['img'] = filename
        try:
            user['loc'] = [float(form['lon']), float(form['lat'])]
            user['lasttime'] = datetime.datetime.now()
        except (KeyError, ValueError):
            pass
        if user:
            db.user.update_one({'_id': userid}, {'$set': user}, upsert=True)
        return {
            'code': 0,
            'msg': '修改成功'
        }

    @wrap_object_id('userid')
    def get(self, userid):
        user = db.user.find_one({'_id': userid})
        if not user:
            return {'code': 1002, 'msg': 'user not find'}
        try:
            image_url = '%s/%s' % (self.img_url, user['img'])
        except KeyError:
            image_url = self.default_img_url
        data = {
            'code': 0,
            'image_url': image_url
        }
        self.fill_text_field(user, data)
        return data

    @wrap_object_id('userid')
    def delete(self, userid):
        try:
            db.user.delete_one({'_id': userid})
            return {
                'code': 0,
                'msg': '删除成功'
            }
        except Exception as e:
            return {
                'code': e,
                'msg': '删除失败'
            }


class UsersCount(Resource):
    """
    所有用户总数
    """

    def get(self):
        return {
            'code': 0,
            'count': db.user.count(),
        }


class UsersList(Resource):
    """
    所有用户信息
    """

    @wrap_page_num()
    def get(self, page, num):
        return {
            'code': 0,
            'users': list(db.user.find().skip(page * num).limit(num)),
        }


class Alumnus(UserResource):
    """
    附近校友信息
    """

    def get(self):
        try:
            lon = float(request.args['lon'])
            lat = float(request.args['lat'])
        except KeyError:
            return {'code': 1001, 'msg': 'miss params'}
        except ValueError:
            return {'code': 1001, 'msg': 'bad params'}

        users = db.user.find({
            'loc': {
                '$near': {
                    '$geometry': {
                        'type': "Point",
                        'coordinates': [lon, lat]
                    },
                    '$maxDistance': 1000
                }
            }
        })
        user_list = []
        for user in users:
            try:
                timestamp = time.mktime(user['lasttime'].timetuple())
            except KeyError:
                timestamp = None
            try:
                image_url = '%s/%s' % (self.img_url, user['img'])
            except KeyError:
                image_url = self.default_img_url
            user_list.append(self.fill_text_field(user, {
                'userid': str(user['_id']),
                'image_url': image_url,
                'distance': distance(lon, lat, *user['loc']),
                'last_timestamp': timestamp,
            }))
        return {
            'code': 0,
            'alumnus': user_list,
        }


class CareerInfo(UserResource):
    """
    同行信息
    """

    @wrap_page_num()
    def get(self, careerid, page, num):
        users = []
        for user in db.user.find({'career': careerid}).skip(page * num).limit(num):
            users.append(self.fill_text_field(user, {
                'userid': user['_id'],
            }))
        return {
            'code': 0,
            'peers': users,
        }


class UserSearch(Resource):
    """
    用户搜索
    @:param name,wechatID,career
    """
    def get(self):
        searchKey = request.args.get('searchKey')
        regx = re.compile(searchKey)
        userSet = []
        users = db.user.find({'$or': [{'name': regx}, {'career': regx},
                                      {'OpenId': regx}]})
        if users.count() == 0:
            return {
                'code': 1001,
                'msg': '找不到您输入的关键信息，请换关键字重新搜索'
            }
        for attr in users:
            userSet.append({
                '_id': str(attr.get('_id')),
                'OpenId': attr.get('OpenId'),
                'career': attr.get('career'),
                'grade': attr.get('grade'),
                'gender': attr.get('gender'),
                'phone': attr.get('phone'),
                'profession': attr.get('profession'),
                'specialty': attr.get('specialty'),
                'name': attr.get('name')
            })
        return {
            'code': 0,
            'msg': '搜索成功',
            'userSet': userSet
        }


def __mount__():
    api.add_resource(UserInfo, '/user/<userid>')
    api.add_resource(UsersCount, '/users/count')
    api.add_resource(UsersList, '/users')
    api.add_resource(CareerInfo, '/career/<careerid>/peers')
    api.add_resource(Alumnus, '/alumnus/near')
    api.add_resource(UserSearch, '/users/search')
