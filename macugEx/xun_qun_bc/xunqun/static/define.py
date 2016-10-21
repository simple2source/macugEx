# -*- coding: utf-8 -*-
"""
图片url 的定义,用于在APP,Admin,Watch间共用相同链接定义
"""
import os as os
import setting as setting

try:
    import ujson as json
except ImportError:
    import json as json

_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_path, './config.json')) as f:
    """
    __config = {
      "default": {
        "images": {
          "group": "./misc/group_default.jpg",
          "user": "./misc/user_default.jpg",
          "watch": "./misc/watch_default.jpg",
          "contact": "./misc/contact_default.jpg"
        },
        "customer_id": null
      },
      ...
    }
    config_images = {
      "default": {
        "group": "./misc/group_default.jpg",
        "user": "./misc/user_default.jpg",
        "watch": "./misc/watch_default.jpg",
        "contact": "./misc/contact_default.jpg"
      },
      ...
    }
    config_customer = {
      None: "default",
      0: "default",
      100: "com.xunqun.disney",
      ...
    }
    """
    __config = json.loads(f.read())
    config_images = {ident: _data['images'] for ident, _data in __config.items()}
    config_customer = {_data['customer_id']: ident for ident, _data in __config.items()}


# 获取头像

class DefaultImageUrl(object):
    def __init__(self, path, config):
        """
        config = {
            'default': 'user_default.jpg',
            'com.xunqun.disney': 'user_disney.jpg'
        }
        """
        self.path = path
        self.config = config

    def __mod__(self, ident):
        """
        ident: 应用包名
        """
        if ident in self.config:
            return self.path % self.config[ident]
        else:
            return self.path % self.config['default']


_config = {}
for ident, data in config_images.items():
    for _t, _p in data.items():
        if _t not in _config:
            _config[_t] = {}
        _config[_t][ident] = _p.rsplit('/', 1)[1].split('.', 1)[0]

"""
_config = {
    "group": {
        "default": "user_default.jpg",
        'com.xunqun.disney': 'user_disney.jpg'
    }
}
"""

static_uri = setting.static['uri']

group_image_normal_path = 'http://%s/group/image/normal/%%s.jpg' % static_uri
group_image_normal_path_default = DefaultImageUrl(group_image_normal_path, _config['group'])

user_image_normal_path = 'http://%s/user/image/normal/%%s.jpg' % static_uri
user_image_normal_path_default = DefaultImageUrl(user_image_normal_path, _config['user'])
user_image_small_path = 'http://%s/user/image/small/%%s.jpg' % static_uri
user_image_small_path_default = DefaultImageUrl(user_image_small_path, _config['user'])

contact_image_normal_path = 'http://%s/user/image/normal/%%s.jpg' % static_uri
contact_image_normal_path_default = DefaultImageUrl(contact_image_normal_path, _config['contact'])
contact_image_small_path = 'http://%s/user/image/small/%%s.jpg' % static_uri
contact_image_small_path_default = DefaultImageUrl(contact_image_small_path, _config['contact'])

watch_image_normal_path = 'http://%s/watch/image/normal/%%s.jpg' % static_uri
watch_image_normal_path_default = DefaultImageUrl(watch_image_normal_path, _config['watch'])

# 家庭圈聊天消息
message_image_normal_path = 'http://%s/message/image/normal/%%s.jpg' % static_uri
message_audio_path = 'http://%s/message/audio/%%s.amr' % static_uri
# 客服模块聊天消息
Q_message_image_normal_path = 'http://%s/question_message/image/normal/%%s.jpg' % static_uri
Q_message_audio_path = 'http://%s/question_message/audio/%%s.amr' % static_uri
# 故事界面广告图片
banner_image_path = 'http://%s/banner/image/%%s.jpg' % static_uri
story_image_normal_path = 'http://%s/story/image/normal/%%s.jpg' % static_uri
story_audio_path = 'http://%s/story/audio/%%s.amr' % static_uri
# 腕表故事内容url
story_content_path = 'http://%s/story/content/%%s.data' % static_uri
# 应用分类图片
category_image_path = 'http://%s/category/image/%%s.jpg' % static_uri
# 答题游戏分类图片
game_category_image_path = 'http://%s/game_category/image/%%s.jpg' % static_uri
# app广场图片url
plaza_image_path = 'http://%s/plaza/image/normal/%%s.jpg' % static_uri
# app安卓版本下载链接
android_file_path = 'http://%s/android/%%s.apk' % static_uri

chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

__all__ = ['group_image_normal_path',
           'group_image_normal_path_default',
           'user_image_normal_path',
           'user_image_normal_path_default',
           'user_image_small_path',
           'user_image_small_path_default',
           'contact_image_normal_path',
           'contact_image_normal_path_default',
           'contact_image_small_path',
           'contact_image_small_path_default',
           'watch_image_normal_path',
           'watch_image_normal_path_default',
           'message_image_normal_path',
           'message_audio_path',
           'Q_message_image_normal_path',
           'Q_message_audio_path',
           'banner_image_path',
           'story_image_normal_path',
           'story_audio_path',
           'story_content_path',
           'category_image_path',
           'game_category_image_path',
           'plaza_image_path',
           'android_file_path',
           'chars',
           'static_uri',
           ]
