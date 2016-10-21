# -*- coding: utf-8 -*-
import urllib
import time
import logging

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

try:
    import ujson as json
except ImportError:
    import json

from core.buffer import CacheBuffer
from core.db import db

logger = logging.getLogger('LocateProxy.handle')

LbsKey = 'ae3ce8544885129868da3027867791ac'
GeoKey = '386cdf42d85e68f8e9a197d0b9f58a92'
GeoUrl = 'http://restapi.amap.com/v3/geocode/regeo?key=%s&location=%%s,%%s' % GeoKey
ConvertKey = '70e7644f3386ad7962853d8ebe6c084e'
ConverUrl = 'http://restapi.amap.com/v3/assistant/coordinate/convert?key=%s&coordsys=gps&locations=%%s,%%s' % ConvertKey

# 腕表原始gps点转换缓存
GeoCache = CacheBuffer(expire=86400 * 2)
# 腕表基站定位数据缓存
LbsCache = CacheBuffer(expire=86400)
# 腕表最后lbs轨迹点
LastLbsLocusCache = CacheBuffer(expire=86400)
# 腕表最后一次gps轨迹点
LastGpsLocusCache = CacheBuffer(expire=86400)

NullAddress = {'province': '', 'city': '', 'road': '', 'citycode': '', 'adcode': ''}


def raw_gps_convert(raw_lon, raw_lat):
    """
    usage:
        status, result = raw_gps_convert(raw_lon, raw_lat)
        if status:
            lon, lat, address, province, city, citycode, adcode = result
    """
    geo_cache_key = '%s:%s' % (raw_lon, raw_lat)
    cache = GeoCache.get(geo_cache_key)
    if not cache:
        resolve = urllib2.urlopen(ConverUrl % (raw_lon, raw_lat)).read()
        result = json.loads(resolve)
        if result['status'] == '1':
            lon, lat = result['locations'].split(',')
            lon = float(lon)
            lat = float(lat)
        else:
            logger.error('Assistant Amap Bad Result %s (%s,%s)' % (resolve, raw_lon, raw_lat))
            return 0, 0
        GeoCache[geo_cache_key] = {
            'lon': lon,
            'lat': lat,
            'address': '',
            'province': '',
            'city': '',
            'citycode': '',
            'adcode': '',
        }
        address = ''
        province = ''
        city = ''
        citycode = ''
        adcode = ''
    else:
        lon = cache['lon']
        lat = cache['lat']
        address = cache['address']
        province = cache['province']
        city = cache['city']
        citycode = cache['citycode']
        adcode = cache['adcode']
    return 1, (lon, lat, address, province, city, citycode, adcode)


def geo_request(lon, lat, raw_lon, raw_lat):
    """
    usage:
        status, result = geo_request(lon, lat, raw_lon, raw_lat)
        if status:
            address, province, city, citycode, adcode = result
    """
    # NOTE 获得定位地址
    geo_cache_key = '%s:%s' % (raw_lon, raw_lat)
    resolve = urllib2.urlopen(GeoUrl % (lon, lat)).read()
    result = json.loads(resolve)
    if result['status'] != '1':
        logger.error('Geocode Amap Bad Result %s %s %s' % (resolve, lon, lat))
        return 0, 0
    regocode = result['regeocode']
    address = regocode['formatted_address'] if regocode.get('formatted_address') else ''
    address_component = result['regeocode'].get('addressComponent', NullAddress)
    province = address_component.get('province', '')
    city = address_component.get('city', '')
    # road = regocode.get('streetNumber', {'street': ''}).get('street', '')
    citycode = address_component.get('citycode', '')
    adcode = address_component.get('adcode', '')
    GeoCache[geo_cache_key] = {
        'lon': lon,
        'lat': lat,
        'address': address,
        'province': province,
        'city': city,
        'citycode': citycode,
        'adcode': adcode,
        # 'road': road,
    }
    return 1, (address, province, city, citycode, adcode)


def lbs_request(imei, lbs):
    """
    usage:
        status, result = lbs_request(imei, lbs)
        if status:
            lon, lat, radius, address, province, city, citycode, adcode = result
    """
    # 只取前6组lbs信息,腕表多组信息后会乱码
    lbs = lbs[:6] if len(lbs) > 6 else lbs
    lbs_cache_key = repr(lbs)
    cache = LbsCache.get(lbs_cache_key)
    if not cache:
        request = {
            'key': LbsKey,
            'accesstype': 0,
            'cdma': 0,
            'imei': imei,
            'network': 'GPRS',
        }
        nearbts = []
        for i, data in enumerate(lbs):
            mcc, mnc, lac, cid, rlex = data
            # mcc, mnc, 小区编号,基站编号,信号强度
            if i != 0:
                nearbts.append('%s,%s,%s,%s,%s' % (mcc, mnc, lac, cid, rlex - 110))
            else:
                request['bts'] = '%s,%s,%s,%s,%s' % (mcc, mnc, lac, cid, rlex - 110)
        request['nearbts'] = '|'.join(nearbts)
        resolve = urllib2.urlopen('http://apilocate.amap.com/position?' + urllib.urlencode(request)).read()
        result = json.loads(resolve)
        if result['status'] != '1' or result['result']['type'] == '0':
            logger.error('Locate Amap Bad Result %s %s' % (resolve, repr(request)))
            return 0, 0
        result = result['result']
        lon, lat = result.get('location', '0,0').split(',')
        lon, lat = float(lon), float(lat)
        radius = result.get('radius', 1000)
        address = result.get('desc', '').replace(' ', '')
        province = result.get('province', '')
        city = result.get('city', '')
        citycode = result.get('citycode', '')
        adcode = result.get('adcode', '')
        # road = result.get('road', '')
        # poi = result.get('poi', '')
    else:
        lon = cache['lon']
        lat = cache['lat']
        radius = cache['radius']
        address = cache['address']
        province = cache['province']
        city = cache['city']
        citycode = cache['citycode']
        adcode = cache['adcode']
    return 1, (lon, lat, radius, address, province, city, citycode, adcode)


def get_last_lbs_locus(imei):
    """
    usage:
        last_lbs_locus = get_last_lbs_locus(imei)
        if last_lbs_locus:
            Get It...
        else:
            Not Get It...
    last_lbs_locus:
        {
            'lon': lon,
            'lat': lat,
            'struct_time': struct_time,
            'radius': radius,
            'timestamp': timestamp,
        }
    """
    last_lbs_locus = LastLbsLocusCache.get(imei)
    if not last_lbs_locus:
        last_lbs_locus = db.watch_locus.find_one({'imei': imei, 'type': 2}, sort=[('timestamp', -1)])
        if last_lbs_locus:
            last_lbs_locus['struct_time'] = time.gmtime(last_lbs_locus['timestamp'])
            LastLbsLocusCache[imei] = last_lbs_locus
    return last_lbs_locus


def new_last_lbs_locus(imei, lon, lat, struct_time, timestamp, radius, lbs_radius):
    LastLbsLocusCache[imei] = {
        'lon': lon,
        'lat': lat,
        'struct_time': struct_time,
        'radius': radius,
        'lbs_radius': lbs_radius,
        'timestamp': timestamp,
    }


def get_last_gps_locus(imei):
    """
    usage:
        last_gps_locus = get_last_gps_locus(imei)
        if last_gps_locus:
            Get It...
        else:
            Not Get It...
    last_gps_locus:
        {
            'lon': lon,
            'lat': lat,
            'struct_time': struct_time,
            'timestamp': timestamp,
        }
    """
    last_gps_locus = LastGpsLocusCache.get(imei)
    if not last_gps_locus:
        last_gps_locus = db.watch_locus.find_one({'imei': imei, 'type': 1}, sort=[('timestamp', -1)])
        if last_gps_locus:
            last_gps_locus['struct_time'] = time.gmtime(last_gps_locus['timestamp'])
            LastGpsLocusCache[imei] = last_gps_locus
    return last_gps_locus


def new_last_gps_locus(imei, lon, lat, struct_time, timestamp):
    LastGpsLocusCache[imei] = {
        'lon': lon,
        'lat': lat,
        'struct_time': struct_time,
        'timestamp': timestamp,
    }


def get_request_user(redis_data):
    if 'request_gps_users' in redis_data and 'request_lbs_users' in redis_data:
        return redis_data['request_gps_users'].split(',') + redis_data['request_lbs_users'].split(',')
    elif 'request_gps_users' in redis_data:
        return redis_data['request_gps_users'].split(',')
    elif 'request_lbs_users' in redis_data:
        return redis_data['request_lbs_users'].split(',')
    else:
        return tuple()
