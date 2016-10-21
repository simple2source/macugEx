# -*- coding: utf-8 -*-
import os

from flask import request

from ..wrappers import api, Resource, wrap_object_id, wrap_page_num
from comm.db import db
import conf
import uuid
import re


class CompanyResource(Resource):
    img_url = '%s/images/company' % conf.STATIC_URL
    img_path = '%s/images/company' % conf.STATIC_PATH

    def __init__(self, *args, **kwargs):
        super(CompanyResource, self).__init__(*args, **kwargs)

        if not os.path.exists(self.img_path):
            os.mkdir(self.img_path)

    text_field = ['name', 'type', 'province', 'city', 'citycode', 'district', 'adcode', 'address', 'title', 'content']

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


class Company(CompanyResource):
    """
    校企详情
    """

    @wrap_object_id('companyid')
    def get(self, companyid):
        company = db.company.find_one({'_id': companyid})
        if not company:
            return {'code': 1002, 'msg': 'company not find'}
        return {
            'code': 0,
            'companyid': str(company['_id']),
            'name': company.get('name'),
            'province': company.get('province'),
            'city': company.get('city'),
            'area': company.get('district'),
            'loc': company.get('loc'),
            'type': company.get('type'),
            'address': company.get('address'),
            'title': company.get('title'),
            'content': company.get('content'),
        }

    @wrap_object_id('companyid')
    def post(self, companyid):
        company = db.company.find_one({'_id': companyid}, {'img': 1})
        if not company:
            return {
                'code': 1002,
                'msg': 'company not find',
            }

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
        try:
            update['loc'] = [float(form['lon']), float(form['lat'])]
        except (KeyError, ValueError):
            pass

        if update:
            db.company.update_one({'_id': companyid}, {'$set': update})

            if company.get('img'):
                try:
                    os.remove('%s/%s' % (self.img_path, company['img']))
                except OSError:
                    pass
        return {
            'code': 0
        }

    @wrap_object_id('companyid')
    def delete(self, companyid):
        try:
            db.company.delete_one({'_id': companyid})
            return {
                'code': 0,
                'msg': '删除成功'
            }
        except Exception as e:
            return {
                'code': e,
                'msg': '删除失败'
            }


class CompanyCount(Resource):
    """
    所有企业总数
    """

    def get(self):
        return {
            'code': 0,
            'count': db.company.count(),
        }


class CompanyList(CompanyResource):
    """
    所有企业信息
    """

    @wrap_page_num()
    def get(self, page, num):
        return {
            'code': 0,
            'companys': list(db.company.find().skip(page * num).limit(num)),
        }

    def post(self):
        form = request.form
        company = {}
        if not form:
            return {
                'code': 1003,
                'msg': 'form data is empty'
            }
        for attr in self.text_field:
            if form.get(attr):
                company[attr] = form[attr]

        if 'image_file' in request.files:
            img_file = form.files['image_file']
            suffix = img_file.filename.split('.')[-1]
            filename = '%s.%s' % (uuid.uuid4(), suffix)
            img_file.save('%s/%s' % (self.img_path, filename))
            company['img'] = filename
        try:
            company['loc'] = [float(form['lon']), float(form['lat'])]
        except (KeyError, ValueError):
            pass
        _id = db.company.insert(company)
        return {
            'code': 0,
            '_id': _id
        }


class CompanyNearList(CompanyResource):
    """
    附近校企
    """

    def get(self):
        try:
            lon = float(request.args['lon'])
            lat = float(request.args['lat'])
        except KeyError:
            return {'code': 1001, 'msg': 'miss params'}
        except ValueError:
            return {'code': 1001, 'msg': 'bad params'}
        # companys = db.company.find({
        #     'loc': {
        #         '$near': {
        #             '$geometry': {
        #                 'type': "Point",
        #                 'coordinates': [lon, lat]
        #             },
        #             '$maxDistance': 2500
        #         }
        #     }
        # })
        # FIXME for debug
        companys = db.company.find()
        company_list = []
        for company in companys:
            company_list.append({
                'companyid': str(company['_id']),
                'name': company.get('name'),
                'area': company.get('district'),
                'type': company.get('type'),
                'address': company.get('address'),
                'image_url': '%s/%s' % (self.img_url, company.get('img', '404.jpg')),
            })
        return {
            'code': 0,
            'companys': company_list,
        }


class CompanySearch(CompanyResource):
    """
    搜索校企
    @:param name, type ,address
    """
    def get(self):
        searchKey = request.args.get('searchKey')
        companySet = []
        regx = re.compile(searchKey)
        companys = db.company.find({'$or': [{'name': regx}, {'address': regx},
                                    {'type': regx}]})
        if companys.count() == 0:
            return {
                'code': 1001,
                'msg': '找不到您输入的关键信息，请换关键字重新搜索'

            }
        for company in companys:
            companySet.append({
                '_id': str(company.get('_id')),
                'name': company.get('name'),
                'address': company.get('address'),
                'content': company.get('content')
            })

        return {
            'code': 0,
            'msg': '搜索成功',
            'companySet': companySet
        }


def __mount__():
    api.add_resource(Company, '/company/<companyid>')
    api.add_resource(CompanyNearList, '/company/near')
    api.add_resource(CompanyList, '/companys')
    api.add_resource(CompanyCount, '/companys/count')
    api.add_resource(CompanySearch, '/companys/search')
