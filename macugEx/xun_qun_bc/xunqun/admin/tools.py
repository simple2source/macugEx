# -*- coding: utf-8 -*-
"""
initialize admin's data
"""
from flask_scrypt import generate_password_hash
from types import StringTypes
import datetime
import struct
import sys
sys.path.append('..')

import setting
from core.db import db
from static.tools import story_image_put, story_audio_put, story_content_put

salt = setting.admin['salt']

menubar_list = [
    {
        '_id': 'base_info',
        'name': u'基础信息',
        'icon': 'fa-info-circle',
        'permissions': ['guest'],
        'submenubar': {
            'watch_info': {
                'name': u'腕表信息',
                'permissions': ['guest'],
            },
            'user_info': {
                'name': u'用户信息',
                'permissions': ['guest'],
            },
            'group_info': {
                'name': u'圈子信息',
                'permissions': ['guest'],
            },
            'watch_locate_info': {
                'name': u'腕表定位',
                'permissions': ['guest'],
            },
            'watch_locus_info': {
                'name': u'腕表轨迹',
                'permissions': ['guest'],
            },
            'user_locate_info': {
                'name': u'用户定位',
                'permissions': ['guest'],
            },
            'user_locus_info': {
                'name': u'用户轨迹',
                'permissions': ['guest'],
            },
            'devicetoken_info': {
                'name': u'devicetoken 信息',
                'permissions': ['guest'],
            },
        }
    },
    {
        '_id': 'watch_debug',
        'name': u'腕表调试',
        'icon': 'fa-question-circle-o',
        'permissions': ['debug'],
        'submenubar': {
            'watch_loger_info': {
                'name': u'指令日志',
                'permissions': ['debug'],
            },
            'watch_online': {
                'name': u'在线腕表',
                'permissions': ['debug'],
            },
        }
    },
    {
        '_id': 'story_manage',
        'name': u'应用管理',
        'icon': 'fa-shopping-bag',
        'permissions': ['guest', 'story_manage', 'game_manage'],
        'submenubar': {
            'appstore_category_info': {
                'name': u'应用分类',
                'permissions': ['story_manage'],
            },
            'story_info': {
                'name': u'故事信息',
                'permissions': ['guest', 'story_manage'],
            },
            'story_upload': {
                'name': u'上传故事',
                'permissions': ['story_manage'],
            },
            'banner_info': {
                'name': u'广告信息',
                'permissions': ['guest', 'story_manage'],
            },
            'answer_game_info': {
                'name': u'答题游戏',
                'permissions': ['guest', 'game_manage'],
            },
            'answer_game_category_info': {
                'name': u'答题分类',
                'permissions': ['game_manage'],
            },
        }
    },
    {
        '_id': 'account_manage',
        'name': u'账号管理',
        'icon': 'fa-users',
        'permissions': ['admin'],
        'submenubar': {
            'admin_info': {
                'name': u'管理员信息',
                'permissions': ['admin'],
            },
        }
    },
    {
        '_id': 'statistical',
        'name': u'统计分析',
        'icon': 'fa-line-chart',
        'permissions': ['guest'],
        'submenubar': {
            'watch_locate_analysis': {
                'name': u'腕表地域分布',
                'permissions': ['guest'],
            },
            'user_locate_analysis': {
                'name': u'用户地域分布',
                'permissions': ['guest'],
            },
            'user_create_analysis': {
                'name': u'用户注册趋势',
                'permissions': ['guest'],
            },
            'group_create_analysis': {
                'name': u'圈子注册趋势',
                'permissions': ['guest'],
            },
        }
    },
    {
        '_id': 'version_manage',
        'name': u'版本管理',
        'icon': 'fa-code-fork',
        'permissions': ['version_manage'],
        'submenubar': {
            'version_android': {
                'name': u'安卓版本管理',
                'permissions': ['version_manage'],
            },
            'bluetooth_info': {
                'name': u'蓝牙版本管理',
                'permissions': ['version_manage'],
            },
        }
    },
    {
        '_id': 'plaza_manage',
        'name': u'广场信息',
        'icon': 'fa-bullhorn',
        'permissions': ['guest', 'plaza_manage'],
        'submenubar': {
            'plaza_info': {
                'name': u'广场消息',
                'permissions': ['guest', 'plaza_manage'],
            },
        }
    },
    {
        '_id': 'submail_info',
        'name': u'邮件信息',
        'icon': 'fa-envelope-o',
        'permissions': ['guest'],
        'submenubar': {
            'submail_info': {
                'name': u'邮件信息',
                'permissions': ['guest'],
            },
        }
    },
    {
        '_id': 'service_manage',
        'name': u'客服模块',
        'icon': 'fa-yelp',
        'permissions': ['service_manage'],
        'submenubar': {
            'service_manage': {
                'name': u'客服信息',
                'permissions': ['service_manage'],
            },
            'question_manage': {
                'name': u'问题管理',
                'permissions': ['service_manage']
            },
            'answer_manage': {
                'name': u'答案管理',
                'permissions': ['service_manage']
            }
        }
    }
]

for menu in menubar_list:
    db.menubar.update_one({'_id': menu['_id']}, {'$set': menu}, upsert=True)


def create_admin(username, password, permissions):
    if not isinstance(permissions, (list, tuple)):
        raise ValueError('permissions must iterable')
    nowtime = datetime.datetime.now()
    db.admin.insert_one({
        '_id': username,
        'nickname': username,
        'password': generate_password_hash(password, salt),
        'permissions': permissions,
        'maketime': nowtime,
        'lasttime': nowtime
    })


if not db.admin.find_one({'_id': 'admin'}):
    create_admin('admin', 'admin', ['admin'])


def make_story_content(front_image, front_text, image_indexs, time_indexs, texts, images, audio_type, audio):
    """
    :param front_image:

        <file> : jpg 格式图片文件
        <bytes>: jpg 格式图片字节

    :param front_text:

        <unicode>: 封面标题文本
        <bytes>  : 封面标题字节(utf-8/utf-16-be encoding)

    :param image_indexs:

        [<int>] : 索引图片值列表

    :param texts:

        [<unicode>]: 索引文字文本列表
        [<bytes>]  : 索引文字字节列表(utf-8/utf-16-be encoding)

    :param time_index:

        [<int>]: 索引时间值(毫秒)列表

    :param images:

        [<file>] : 故事图片文件列表
        [<bytes>]: 故事图片字节列表

    :param audio_type:

        0     : amr故事语音文件类型
        1     : mp3故事语音文件类型
        'amr' : amr故事语音文件类型
        'mp3' : mp3故事语音文件类型

    :param audio:

        <file> : 故事语音文件
        <bytes>: 故事语音字节

    :return:

        腕表播放的故事文件内容

    打包文件夹结构:

        ├── img
        │   ├── 1.jpg
        │   ├── 2.jpg
        │   ├── 3.jpg
        │   └── 4.jpg
        ├── make.py
        ├── unmake.py
        ├── 守株待兔.amr
        ├── 守株待兔.data
        ├── 守株待兔.jpg
        ├── 守株待兔.mp3
        └── 守株待兔.txt

    字幕文件内容示例:

        1,2200,守株待兔
        1,6800,这个成语比喻不知变通
        1,10500,或想不经过努力而侥幸得到成功
        1,21000,宋国有个农夫正在田里干活
        2,25500,看见一只兔子奔来
        2,32500,兔子跑得太急
        2,35000,一下撞到树桩上
        2,38000,昏死过去
        3,42000,农夫见了
        3,43500,丢下农具
        3,46000,把兔子拾起来
        3,54000,农夫回到家里美美吃了一顿兔子肉
        4,62000,从此他不干活了
        4,65900,天天坐在树桩旁等着兔子来撞
        4,77500,可是他再也没等到兔子,田地却荒芜了
        4,88000,

    """
    # import pdb;pdb.set_trace()
    if len(image_indexs) != len(texts) != len(time_indexs):
        raise ValueError('imge,time,text index length mismatch')
    if not isinstance(front_image, bytes):
        if isinstance(front_image, StringTypes):
            front_image = front_image.encode('utf-8')
        elif getattr(front_image, 'read', None):
            front_image = front_image.read()
        else:
            raise ValueError('front image not has read method')
    front_image_length = len(front_image)

    if isinstance(front_text, bytes):
        try:
            front_text = front_text.decode('utf-8').encode('utf-16-be')
        except UnicodeDecodeError:
            try:
                front_text.decode('utf-16-be')
            except UnicodeDecodeError:
                raise ValueError('front text must utf-8/utf-16-be code')
    elif isinstance(front_text, StringTypes):
        front_text = front_text.encode('utf-16-be')
    else:
        raise ValueError('front text must a string')
    front_text_length = len(front_text)

    FIX_HEAD_LEN = 16  # 封面区头部固定长

    front_block = ''.join(['XQSF', struct.pack('>III', FIX_HEAD_LEN + front_text_length + front_image_length,
                                               front_text_length, front_image_length), front_text, front_image])  # 封面区

    text_list = []
    text_length_list = []
    for s in texts:
        if isinstance(s, bytes):
            try:
                s = s.decode('utf-8').encode('utf-16-be')
            except UnicodeDecodeError:
                try:
                    s.decode('utf-16-be')
                except UnicodeDecodeError:
                    raise ValueError('text index must utf-8/utf-16-be code')
        elif isinstance(s, StringTypes):
            s = s.encode('utf-16-be')
        else:
            ValueError('text index must a string')

        text_list.append(s)
        text_length_list.append(len(s))

    text_block = ''.join(text_list)  # 文字区

    image_list = []
    image_length_list = []
    for i in images:
        if not isinstance(i, bytes):
            i = i.read()
        image_list.append(i)
        image_length_list.append(len(i))

    image_block = ''.join(image_list)  # 图片区

    image_index_list = []
    image_list_length = len(images)
    for i in image_indexs:
        index = int(i)
        if index < 0:
            raise ValueError('image index must large that 0')
        if index + 1 > image_list_length:
            raise ValueError('image index overflow the image list')
        image_index_list.append(index)

    if 0 not in image_index_list:
        # 以 1 为图片序号开头的字幕文件
        image_index_list = map(lambda x: x - 1, image_index_list)

    time_index_list = []
    for i in time_indexs:
        index = int(i)
        if index < 0:
            raise ValueError('time detal must large that 0')
        time_index_list.append(index)

    index_list = []
    last_time_detal = 0
    for i, time_detal in enumerate(time_index_list):
        if time_detal < last_time_detal:
            raise ValueError('time detal must increasing')
        last_time_detal = time_detal
        if i == 0:
            text_offset = 0
        else:
            text_offset = sum(text_length_list[:i])

        image_offset = sum(image_length_list[:image_index_list[i]])
        index = struct.pack('>IIIII', time_detal, text_offset, text_length_list[i], image_offset,
                            image_length_list[image_index_list[i]])
        index_list.append(index)

    index_block = ''.join(index_list)  # 索引区

    HEAD_LEN = 20  # 头部区域固定长
    text_offset = HEAD_LEN + len(index_block)
    image_offset = text_offset + len(text_block)
    amr_offset = image_offset + len(image_block)
    if isinstance(audio_type, StringTypes):
        audio_type = 0 if audio_type == 'amr' else 1
    head_block = struct.pack('>IIIII', len(index_list), text_offset, image_offset, audio_type, amr_offset)

    if not isinstance(audio, bytes):  # 语音区
        audio_block = audio.read()
    else:
        audio_block = audio

    return ''.join([front_block, head_block, index_block, text_block, image_block, audio_block])


def create_story_document(title, brief, category_id, front_image, image_list, index_list, time_list, text_list,
                          audio_type, audio, content):
    """
    :param title:

        <unicode>: 故事标题文本
        <str>    : 故事标题字节(utf-8 encoding)

    :param brief:

        <str>: 标识简介

    :param category_id:

        <unicode>: 故事分类id文本
        <str>    : 故事分类id字节(utf-8 encoding)

    :param front_image:

        <file> : 封面图片文件
        <bytes>: 封面图片字节

    :param image_list:

        [<file>] : 索引图片文件列表
        [<bytes>]: 索引图片字节列表

    :param index_list:

        [<int>]: 索引图片索引值

    :param time_list:

        [<int>]: 索引时间毫秒数

    :param text_list:

        [<str>]  : 索引字幕文字
        [<bytes>]: 索引字幕字节(utf-8 encoding)

    :param audio_type:

        0     : amr故事语音文件类型
        1     : mp3故事语音文件类型
        'amr' : amr故事语音文件类型
        'mp3' : mp3故事语音文件类型

    :param audio:

        <file> : 语音文件
        <bytes>: 语音字节

    :param content:

        <bytes>: 故事文件内容

    :return:

        故事 ObjectId
    """
    story = {
        'title': title,
        'brief': brief,
    }
    if category_id:
        story['category_id'] = category_id
    if isinstance(front_image, bytes):
        f_id = story_image_put(front_image)
    else:
        f_id = story_image_put(front_image.read())
    story['image_id'] = f_id
    images = []
    for i in image_list:
        if isinstance(i, bytes):
            i_id = story_image_put(i)
        else:
            i_id = story_image_put(i.read())
        images.append(i_id)
    story['images'] = images
    story['slice_image'] = index_list
    story['slice_time'] = time_list
    story['slice_text'] = text_list
    if isinstance(audio, bytes):
        a_id = story_audio_put(audio)
    else:
        a_id = story_audio_put(audio.read())
    story['audio_id'] = a_id
    if isinstance(audio_type, int):
        audio_type = 'amr' if audio_type == 0 else 'mp3'
    story['audio_type'] = audio_type
    content_id = story_content_put(content)
    story['content_id'] = content_id
    return db.story.insert_one(story)


def decode_chinese(byte_string):
    try:
        byte_string2 = byte_string.decode('gbk').encode('utf-8')
    except Exception:
        try:
            byte_string2 = byte_string.decode('utf-8-sig').encode('utf-8')
        except Exception:
            return ''
    return byte_string2
