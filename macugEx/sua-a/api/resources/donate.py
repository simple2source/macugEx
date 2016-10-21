# -*- coding: utf-8 -*-
import os

from ..wrappers import api, Resource, wrap_object_id, wrap_page_num
from .user import UserResource
from comm.db import db
import conf
from flask import request
import re


class DonateCount(Resource):
    """
    捐赠记录总计
    """

    def get(self):
        return {
            'code': 0,
            'count': db.donate.count(),
        }


class FoundationResource(Resource):
    img_url = '%s/images/foundation' % conf.STATIC_URL
    img_path = '%s/images/foundation' % conf.STATIC_PATH

    def __init__(self, *args, **kwargs):
        super(FoundationResource, self).__init__(*args, **kwargs)

        if not os.path.exists(self.img_path):
            os.mkdir(self.img_path)

    text_field = ['content', 'acount', 'amount', 'need_money', 'name', 'create_time','image_url']


class FoundationList(FoundationResource):
    """
    基金会列表
    """

    @wrap_page_num()
    def get(self, page, num):
        founds = []
        for found in db.donate.find().skip(page * num).limit(num):
            founds.append({
                '_id': str(found['_id']),
                'name': found.get('name'),
                'content': found.get('content'),
                'acount': found.get('acount'),
                'amount': found.get('amount'),
                'create_time': found.get('create_time'),
                'image_url': '%s/%s' % (self.img_url, found.get('img', '404.jpg')),
            })
        return {
            'code': 0,
            'foundations': founds,
        }

    def post(self):
        """
        添加捐款项目
        :return:
        """
        form = request.form
        donate = {}
        for attr in self.text_field:
            if form.get(attr):
                donate[attr] = form[attr]
        if donate:
            _id = db.donate.insert(donate)
        return {
            'code': 0,
            '_id': _id,
            'msg': '添加成功！'
        }


class Foundation(FoundationResource):
    """
    基金会
    """

    @wrap_object_id('foundid')
    def get(self, foundid):
        found = db.donate.find_one({'_id': foundid})
        if not found:
            return {
                'code': 1002,
                'msg': 'foundation not find',
            }
        return {
            'code': 0,
            '_id': found.get('_id'),
            'name': found.get('name'),
            'content': found.get('content'),
            'acount': found.get('acount'),
            'amount': found.get('amount'),
            'image_url': '%s/%s' % (self.img_url, found.get('img', '404.jpg')),
        }

    @wrap_object_id('foundid')
    def delete(self,foundid):
        try:
            db.donate.delete_one({'_id': foundid})
            return {
                'code': 0,
                'msg': '删除成功'
            }
        except Exception as e:
            return {
                'code': e,
                'msg': '删除失败'
            }

    @wrap_object_id('foundid')
    def post(self, foundid):
        form = request.form
        found = {}
        for attr in self.text_field:
            if form.get(attr):
                found[attr] = form[attr]
        if found:
            db.donate.update({'_id': foundid}, {'$set': found}, upsert=True)
        return {
            'code': 0,
            'msg': '修改成功！'
        }


class FoundationDonate(Resource):
    """
    基金会捐赠情况
    """

    @wrap_object_id('foundid')
    @wrap_page_num()
    def get(self, founid, page, num):
        donates = []
        users = {}
        for donate in db.donate.find({'found_id': founid}).skip(page * num).limit(num):
            try:
                userid = donate['user_id']
                users[userid] = UserResource.default_img_url
            except KeyError:
                userid = None
            donates.append({
                'donateid': str(donate['_id']),
                'userid': userid,
                'brief': donate.get('brief'),
                'named': donate.get('named'),
                'wishe': donate.get('wishe'),
                'amount': donate.get('num'),
                'timestamp': donate.get('timestamp'),
            })
        for user in db.user.find({'_id': {'$in': users.keys()}}, {'img': 1}):
            users[user['_id']] = '%s/%s' % (UserResource.img_url, user['img'])
        for donate in donates:
            try:
                donate['image_url'] = users[donate['user_id']]
            except KeyError:
                donate['image_url'] = UserResource.default_img_url
        return {
            'code': 0,
            'donates': donates,
        }


class UserDonateRank(Resource):
    """
    用户捐赠榜
    """

    @wrap_page_num()
    def get(self, page, num):
        users = []
        for user in db.user.find().sort('donateNum', -1).skip(page * num).limit(num):
            try:
                image_url = '%s/%s' % (UserResource.img_url, user['img'])
            except KeyError:
                image_url = UserResource.default_img_url
            users.append({
                'userid': str(user['_id']),
                'image_url': image_url,
                'name': user.get('name'),
                'grade': user.get('grade'),
                'specialty': user.get('specialty'),
                'amount': user.get('donateNum'),
            })
        return {
            'code': 0,
            'users': users,
        }


class UserDonate(Resource):
    """
    用户捐赠
    """

    @wrap_object_id('userid')
    @wrap_page_num()
    def get(self, userid, page, num):
        donates = {}
        foundids = set()
        for donate in db.donate.find({'user_id': userid}).skip(page * num).limit(num):
            try:
                foundid = donate['found_id']
            except KeyError:
                foundid = ''
            try:
                foundDonates = donates[foundid]
            except KeyError:
                foundDonates = {
                    'name': None,
                    'image_url': None,
                    'amount': 0,
                    'acount': 0,
                }
                donates[foundid] = foundDonates
                if foundid:
                    foundids.add(foundid)
            foundDonates['amount'] += donate.get('num')
            foundDonates['acount'] += 1
        founds = {}
        for found in db.foundation.find({'_id': {'$in': list(foundids)}}, {'name': 1, 'img': 1}):
            founds[found['_id']] = {
                'name': found.get('name'),
                'image_url': '%s/%s' % (FoundationResource.img_url, found.get('img', '404.jpg')),
            }
        for foundid, found in donates.items():
            try:
                found['name'] = founds[foundid]['name']
                found['image_url'] = founds[foundid]['image_url']
            except KeyError:
                pass
        return {
            'code': 0,
            'donates': donates,
        }

    @wrap_object_id('userid')
    def post(self, userid):
        # FIXME
        pass


class DonateAction(Resource):
    """
    发起捐赠
    """

    @wrap_object_id('foundationid', 'userid')
    def get(self, foundationid, userid):
        # FIXME
        pass


class FoundationSearch(Resource):
    """
    关键字查询
    :param name
    """
    def get(self):
        searchName = request.args.get('queryName')
        nameSet = []
        regx = re.compile(searchName)
        donateSet = db.donate.find({'$or': [{'name': regx}, {'amount': regx}]})
        if donateSet.count() == 0:
            return {
                'code': 1001,
                'msg': '没有找到您要搜索的相关基金会，请换个关键字重新搜索'
            }
        for attr in donateSet:
            nameSet.append({
                '_id': str(attr.get('_id')),
                'name': attr.get('name'),
                'acount': attr.get('acount'),
                'amount': attr.get('amount'),
                'create_time': attr.get('create_time'),
                'need_money': attr.get('need_money'),
                'content': attr.get('content')
            })
        return {
            'code': 0,
            'msg': '查询成功',
            'nameSet': nameSet
        }


def __mount__():
    api.add_resource(FoundationList, '/foundations')
    api.add_resource(DonateCount, '/donate/count')
    api.add_resource(Foundation, '/foundation/<foundid>')
    api.add_resource(FoundationDonate, '/foundation/<foundid>/donates')
    api.add_resource(UserDonateRank, '/users/donateRanks')
    api.add_resource(UserDonate, '/user/<userid>/donates')
    api.add_resource(DonateAction, '/donate/action')
    api.add_resource(FoundationSearch, '/foundations/search')
