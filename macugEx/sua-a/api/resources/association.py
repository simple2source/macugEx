# -*- coding: utf-8 -*-
from flask import request
from ..wrappers import api, Resource, wrap_object_id, wrap_page_num
from comm.db import db
import re


class Association(Resource):
    """
    校友会
    """

    @wrap_object_id('aid')
    def get(self, aid):
        association = db.association.find_one({'_id': aid})
        if not association:
            return {
                'code': 1002,
                'msg': 'association not find',
            }
        return {
            'code': 0,
            'name': association.get('name'),
            'content': association.get('content'),
            'type': association.get('type'),
        }

    @wrap_object_id('aid')
    def post(self, aid):
        form_data = request.form.to_dict()
        association = db.association.find_one({'_id': aid})
        if not form_data and not association:
            return {
                'code': 1003,
                'msg': 'form data is None or id not find'
            }
        _id = db.association.update_one({'_id': aid}, {'$set': form_data}, upsert=True)
        if not _id:
            raise Exception('update fail {}'.format(_id))
        return {
            'code': 0
        }

    @wrap_object_id('aid')
    def delete(self, aid):
        try:
            db.association.delete_one({'_id': aid})
            return {
                'code': 0,
                'msg': '删除成功'
            }
        except Exception as e:
            return {
                'code': e,
                'msg': '删除失败'
            }


class AssociationCount(Resource):
    """
    所有校友会总数
    """
    def get(self):
        return {
            'code': 0,
            'count': db.association.count()
        }


class Associations(Resource):
    """
    所有校友会信息
    """
    @wrap_page_num()
    def get(self, page, num):
        return {
            'code': 0,
            'associations': list(db.association.find().skip(page * num).limit(num))
        }

    def post(self):
        form_data = request.form.to_dict()
        if form_data is None:
            return {
                'code': 1003,
                'msg': 'form data is None'
            }
        _id = db.association.insert(form_data)
        if not _id:
            raise Exception('insert form data error')
        return {
            'code': 0,
        }


class AssociationList(Resource):
    """
    校友会列表总览
    """

    def get(self):
        associations = db.association.find()
        asss = {}
        for AS in associations:
            try:
                asss[AS['type']].append({
                    'associationid': str(AS['_id']),
                    'name': AS.get('name'),
                })
            except KeyError:
                asss[AS['type']] = [{
                    'associationid': str(AS['_id']),
                    'name': AS.get('name'),
                }]

        return {
            'code': 0,
            'associations': asss
        }


class AssociationSearch(Resource):
    """
    搜索校友会
    """
    def get(self):
        searchKey = request.args.get('searchKey')
        associationSet = []
        regx = re.compile(searchKey)
        associations = db.association.find({'$or': [{'name': regx}, {'type': regx}]})
        if associations.count() == 0:
            return{
                'code': 1001,
                'msg': '找不到您输入的关键信息，请换关键字重新搜索'
            }
        for attr in associations:
            associationSet.append({
                '_id': str(attr.get('_id')),
                'name': attr.get('name'),
                'type': attr.get('type')
            })
        return {
            'code': 0,
            'msg': '搜索成功',
            'associationSet': associationSet
        }


def __mount__():
    api.add_resource(Association, '/association/<aid>')
    api.add_resource(AssociationList, '/association/overview')
    api.add_resource(AssociationCount, '/associations/count')
    api.add_resource(Associations, '/associations')
    api.add_resource(AssociationSearch, '/associations/search')
