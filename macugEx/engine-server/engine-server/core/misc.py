# -*- coding: utf-8 -*-
import math


def distance(lon1, lat1, lon2, lat2):
    """
    获取两地GPS间距离,两地距离不能相同
    params: lon1 lat1, lon2 lat2
        < float float float float >
    """
    if lon1 == lon2 and lat1 == lat2:
        return 0.0
    lon1 = lon1 * math.pi / 180.0
    lat1 = lat1 * math.pi / 180.0
    lon2 = lon2 * math.pi / 180.0
    lat2 = lat2 * math.pi / 180.0
    con = math.sin(lat1) * math.sin(lat2)
    con += math.cos(lat1) * math.cos(lat2) * math.cos(lon1 - lon2)
    return round(math.acos(con) * 6378137.0 / 1000, 9) * 1000
