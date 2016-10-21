# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()

try:
    import ujson as json
except ImportError:
    import json

import urllib2
import sys

sys.path.append('..')
from core.db import db


def resolve_loc(lon, lat):
    """
    usage:
        result = resolve_location(data['lon'], data['lat'])
        if not result:
            return failed(XXX)
        else:
            address, province, city, citycode, adcode = result
    """
    resolve = urllib2.urlopen(
        'http://restapi.amap.com/v3/geocode/regeo?key=386cdf42d85e68f8e9a197d0b9f58a92&location=%s,%s' % (
            lon, lat)).read()
    result = json.loads(resolve)
    if result['status'] != '1':
        print(result)
        return None
    regocode = result['regeocode']
    address = regocode.get('formatted_address', '')
    if not address:
        print(result)
        return None
    address_component = regocode.get('addressComponent')
    if not address_component:
        return address, '', '', '', ''
    province = address_component.get('province', '')
    city = address_component.get('city', '')
    citycode = address_component.get('citycode', '')
    adcode = address_component.get('adcode', '')
    return address, province, city, citycode, adcode


for data in db.user_locate.aggregate([
    {'$group': {
        '_id': {'user_id': '$user_id'},
        'loc': {'$last': '$loc'},
        'oid': {'$last': '$_id'},
        'address': {'$last': '$address'},
    }}
]):
    if data['address']:
        continue
    user_id = data['_id']['user_id']
    loc = data['loc']
    if not 180 >= data['loc'][0] >= -180 or not 90 >= data['loc'][1] >= -90:
        print('bad user loc %s, %s' % (user_id, repr(loc)))
        continue
    result = resolve_loc(*data['loc'])
    if not result:
        print('can not get loc result %s, %s' % (user_id, repr(loc)))
        continue
    address, province, city, citycode, adcode = result
    db.user_locate.update_one({'_id': data['oid']}, {'$set': {
        'address': address,
        'province': province,
        'city': city,
        'citycode': citycode,
        'adcode': adcode,
    }})
