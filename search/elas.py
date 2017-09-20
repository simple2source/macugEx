# -*- coding: utf-8 -*-

"""
goods cache server

add delete search ...

"""

import json
from datetime import datetime
from flask import Blueprint, request
from cacheandsearch.extensions import es, logger
from elasticsearch.exceptions import NotFoundError
from aladin.services import ResponseJson
from cacheandsearch.service_code import PUBLISHED_CODE

goods = Blueprint('goodsCache', __name__)
res_json = ResponseJson()
res_json.module_code = 20


@goods.route('/add', methods=["POST"])
def add_goods():
    """
    商品库同步 新增，修改
    :return:
    """
    res_json.action_code = 35
    doc = request.json
    gid = doc.get('goods_id')
    if not gid:
        return res_json.print_json(23, 'params goods_id not exist')
    doc['timestamp'] = datetime.now()
    ret = es.index(index="test-goodslib", doc_type='goods', id=gid, body=doc)
    logger.info(ret)
    return res_json.print_json(0, 'ok', ret)


@goods.route('/<int:goods_id>/delete', methods=['POST'])
def delete_goods(goods_id):
    """
    商品库删除商品
    :param goods_id:
    :return:
    """
    res_json.action_code = 36
    try:
        es.delete(index='test-goodslib', doc_type='goods', id=goods_id)
    except NotFoundError:
        logger.error('goods_id {} not found in es'.format(goods_id))
        return res_json.print_json(404, 'goods_id not found in es')

    return res_json.print_json(0, 'ok')


@goods.route('/sn/search')
def search_sn():
    """
    use two field query [goods_status] [goods_sn] must, use prefix search
    :param #  goods_sn goods_status must query
    :return:
    """
    res_json.action_code = 37
    goods_sn = request.args.get('q')
    goods_status = request.args.get('goods_status', PUBLISHED_CODE)
    if not goods_sn:
        return res_json.print_json(37, u'查询商品编码为空')
    result = es.search(index='test-goodslib', doc_type='goods', body={
        'query': {
            'bool': {
                'must': [
                    {'match_phrase_prefix': {'goods_sn': {'query': goods_sn, 'slop': 10, 'max_expansions': 20}}},
                    {'match': {'status': goods_status}}
                ]
            }

        }
    })
    logger.info('search get ret : {}'.format(result))
    return res_json.print_json(0, 'ok', data=result['hist']['hits'])


@goods.route('/search')
def get_goods():
    """
    use goods name to match
    :return:
    """
    res_json.action_code = 39
    goods_name = request.args.get('q')
    ret = es.get('test-goodslib', doc_type='goods', id=10)
    ret = es.search('test-index', size=1)
    print(ret)
    ret_phrase = es.search(index='test-index', doc_type='goods', body={
        "query": {
            "match": {
                "goods_name": {
                    "query": "战争与和平",
                    "type": "phrase"
                }
            }
        }
    })
    return res_json.print_json(data=ret)


@goods.route('/tes')
def tes():
    res_json.action_code = 24
    ret = es.get('test-goodslib', doc_type='goods', id=50)
    print(ret)
    return res_json.print_json(data=ret['_source'])


#!/usr/bin/env python
# coding=utf-8

from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import DocType, Date, Integer, Keyword, Text
import sys

es = Elasticsearch([{'host': '192.168.1.12', 'port': 9200}])
doc = {
    'author': 'stangda',
    'book': '战争与和平',
    'year': 'age20',
    'k3code': 'GB1231',
    'book_num': 2343,
    'tag': 'GB1322',
    'goods_sn': 'GBS',
    'name': 'rose43430',
    'status': 1,
    'text': 'Elasticsearch: cool. bonsai cool.',
    'timestamp': datetime.now(),
    'long': '360page',
    'attribute': [
        {
            'a1': 'woj'
        },
        {
            'a1': 'tatum'
        }

    ]
}
# res = es.index(index="test-index", doc_type='t00eet', id=37, body=doc)
# res = es.get(index='test-index', id=37)
# res = es.search(index="test-index", body={"query": {"match_all": {}}})
# res = es.delete(index='test-index', doc_type='tweet', id=1)
# res = es.search(index='test-index', body={'query': {'term': {'author': 'tolr'}}})
# res = es.search(index='test-index', doc_type='tweet', q='＋status:1')

# fox = es.index(index='email', doc_type='address', body={
#     "author": "blue",
#     "postcode": "GI-102",
#     "name": "horse z",
#     "habbit": "登山，看电影，网球",
#     "status": 1,
#     "sn": "GX12220"
# })
# print('fox ------:', fox)
# sys.exit(400)

res = es.search(index='test-index', doc_type='t00eet', body={"query": {'match': {"a1": 'woj'}}})
riiiii_doc = {
    'book': '风之影',
    'name': 'safeng',
    'great': '一本书',
    'tag': "most important",
    'page': 500
}
# riiiii = es.index(index='face-index', id=62, doc_type='face', body=riiiii_doc)
# rii_ret = es.search(index='face-index', doc_type='face', body={"query": {"match": {"book": "百"}}})
rws = es.search(index='test-index', body={
    'query': {
        "constant_score": {
            "filter": {
                'bool': {
                    'must': [
                        {'match': {'book_num': 2343}},
                        {'match': {'status': 0}}
                    ]
                }
            }
        }

    }
})

rqs = es.search(index='test-index', body={
    'query': {
        'bool': {
            'must': [
                {'match': {'book_num': 2343}},
                {'match': {'status': 0}}
            ]
        }
    }
})

rfq = ret_phrase = es.search(index='test-index', doc_type='t00eet', body={
        "query": {
            "match": {
                "book": {
                    "query": "战争",
                    "type": "phrase"
                }
            }
        }
    })

normal_ret = es.search(index="email", doc_type="address", body={
    "query": {
        "match": {
            "habbit": "网球"
        }
    }
})

print("normal_ret =======", normal_ret)

# 短语查询
fox_ret = es.search(index="email", doc_type="address", body={
    "query": {
        "match": {
            "author": {
                "query": "quick fox",
                "type": "phrase"
            }
        }
    }
})

print('fox_ret: =====', fox_ret)

# 前缀匹配查询
prefix_ret = es.search(index="email", doc_type="address", body={
    "query": {
        "match_phrase_prefix": {
            "author": {
                "query": "qu",
                "slop": 10
            }
        }
    }
})
print('prefix_ret: ======', prefix_ret)

# 前缀bool查询
bool_prefix_ret = es.search(index="email", doc_type="address", body={
    "query": {
        "bool": {
            "must": [
                {"match_phrase_prefix": {"sn": {"query": "GX12220", "slop": 10, 'max_expansions': 10}}},
                {"match": {"status": 1}}
            ]
        }
    }
})
print("bool_prefix_ret: =====", bool_prefix_ret)

# or 匹配查询
result = es.search(index='test-tree', doc_type='tree', body={
    "query": {
        "bool": {
            "should": [
                {"match": {"parentId": 3}},
                {"match": {"parentId": 4}},
                {"match": {"parentId": 5}},
                {"match": {"parentId": 6}},
            ]
        }

    }
})

template = \
    {
        "mappings": {
            "goods": {
                "properties": {
                    "goods_id": {
                        "type": "long"
                    },
                    "goods_name": {
                        "type": "text",
                        "search_analyzer": "ik_max_word",
                        "analyzer": "ik_max_word"
                    },
                    "goods_status": {
                        "type": "long"
                    },
                    "goods_code": {
                        "type": "string"
                    },
                    "goods_sn": {
                        "type": "string",
                        "analyzer": "not_analyzed"
                    },
                    "goods_type": {
                        "type": "long"
                    },
                    "summary": {
                        "type": "string"
                    },
                    "short_code": {
                        "type": "string"
                    },
                    "basic_unit_id": {
                        "type": "long"
                    },
                    "brand_id": {
                        "type": "long"
                    },
                    "brand_name": {
                        "type": "string"
                    },
                    "shelf_life": {
                        "type": "string"
                    },
                    "shelf_life_unit": {
                        "type": "string"
                    },
                    "weight_upper": {
                        "type": "string"
                    },
                    "weight_floor": {
                        "type": "string"
                    },
                    "original_place": {
                        "type": "string"
                    },
                    "is_group_goods": {
                        "type": "boolean"
                    },
                    "is_standard_produce": {
                        "type": "boolean"
                    },
                    "k3_code": {
                        "type": "string"
                    },
                    "add_userid": {
                        "type": "long"
                    },
                    "add_username": {
                        "type": "string"
                    },
                    "goods_attribute": {
                        "type": "nested",
                        "properties": {
                            "id": {
                                "type": "long"
                            },
                            "attribute_name": {
                                "type": "string"
                            },
                            "attribute_value_type": {
                                "type": "string"
                            },
                            "attribute_value": {
                                "type": "string"
                            },
                            "remark": {
                                "type": "string"
                            },
                            "sequence": {
                                "type": "long"
                            }
                        }
                    },
                    "group_goods": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "long"
                            },
                            "goods_id": {
                                "type": "long"
                            },
                            "part_goods_id": {
                                "type": "long"
                            },
                            "part_goods_sn": {
                                "type": "string",
                                "analyzer": "not_analyzed"
                            },
                            "part_goods_name": {
                                "type": "string"
                            },
                            "part_goods_num": {
                                "type": "long"
                            },
                            "sequence": {
                                "type": "long"
                            }
                        }
                    }

                }
            }
        }
}