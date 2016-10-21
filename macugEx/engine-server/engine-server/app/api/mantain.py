# -*- coding: utf-8 -*-
"""
程序后台维护数据模块
"""
import gevent
import random
from bson.objectid import ObjectId
from pymongo.cursor import CursorType
from core.db import db, redis
from static.define import banner_image_path, category_image_path, story_image_small_path, story_audio_path, \
    game_category_image_path
from .tools import logger

# 默认故事分类
default_category = {
    'story': u'故事',
    # 'cartoon': u'漫画',
    # 'rhyme': u'儿歌',
    # 'sinology': u'国学',
    'english': u'英语',
    'answer_game': u'趣味答题',
}

valid_category = ['story', 'answer_game']

for i, (_id, name) in enumerate(default_category.items()):
    if not db.appstore.category.find_one({'_id': _id}):
        db.appstore.category.insert_one({
            '_id': _id,
            'name': name,
            'sort': i,
        })

banner_list = []
category_list = []
hot_list = []


def get_banner_list():
    return banner_list


def get_category_list():
    return category_list


def get_hot_list():
    return hot_list


def fresh_appstore_index():
    """
    定期刷新应用首页
        1.广告栏
        2.分类栏
        3.热门故事列表
    """
    banner_list[:] = []
    for banner in db.banner.find().limit(5):
        story_id = str(banner.get('story_id', ''))
        banner_list.append({
            'banner_image_url': banner_image_path % banner['image_id'],
            'banner_type': 'story' if story_id else 'advert',
            'story_id': story_id,
            'url': banner.get('url', ''),
        })

    category_list[:] = []
    for category in db.appstore.category.find().sort('sort', 1).limit(5):
        category_num = 1 if category['_id'] in valid_category else 0
        image_id1 = category.get('image_id')
        if not image_id1:
            logger.warning('category "%s" image id notfind.' % category['_id'])
            image_id1 = 'None'
        image_id2 = category.get('image_id2')
        if not image_id2:
            logger.warning('%s category image id2 notfind.' % category['_id'])
            image_id2 = 'None'
        category_list.append({
            'category_name': category['name'],
            'category_image_url': category_image_path % (image_id1 if category_num > 0 else image_id2),
            'category_id': category['_id'],
            'category_num': category_num,
        })

    hot_list[:] = []
    for category in category_list:
        story_id_list = [ObjectId(i) for i in redis.zrevrange('HotCategory:%s' % category['category_id'], 0, 5)]
        if story_id_list:
            result = db.story.find({'_id': {'$in': story_id_list}})
            for story in result:
                hot_list.append({
                    'story_image_url': story_image_small_path % story['image_id'],
                    'story_audio_url': story_audio_path % story['audio_id'],
                    'story_id': str(story['_id']),
                    'story_name': story['title'],
                    'story_category_id': story.get('category_id', ''),
                    'story_brief': story['brief'],
                })


game_category_list = []


def get_game_category_list():
    return game_category_list


def fresh_game_data():
    """
    定期刷新答题游戏数据
    """
    answer_game_dict.clear()
    for A in db.answer_game.find(cursor_type=CursorType.EXHAUST):
        try:
            category_id = A['category_id']
            A['_id'] = str(A['_id'])
            try:
                answer_game_dict[category_id].append(A)
            except KeyError:
                answer_game_dict[category_id] = [A]
        except KeyError:
            pass
    answer_game_dict_length.clear()
    for k, v in answer_game_dict.items():
        answer_game_dict_length[k] = len(v)

    game_category_list[:] = []
    for category in db.answer_game.category.find().sort('sort', 1):
        game_category_list.append({
            'category_name': category['name'],
            'category_image_url': game_category_image_path % category['image_id'],
            'category_id': category['_id'],
        })


answer_game_dict = {}
answer_game_dict_length = {}
"""
answer_game_dict = {
    'math': [
        {
            '_id': '55f43cb60bdb82a0fd9ff49c',
            'question': '...',
        }
    ]
}
answer_game_dict_length = {
    'math': 1,
}
"""


def get_random_game_list(category_id, num=10):
    game_list = []
    if category_id in answer_game_dict:
        indexs = []
        i = 0
        answer_game_length = answer_game_dict_length[category_id]
        answer_game_list = answer_game_dict[category_id]
        while i < answer_game_length and i < num:
            index = random.randint(0, answer_game_length - 1)
            if index not in indexs:
                game_list.append(answer_game_list[index])
                indexs.append(index)
                i += 1
    return game_list


def build():
    while 1:
        fresh_appstore_index()
        fresh_game_data()
        gevent.sleep(300)


gevent.spawn(build)
