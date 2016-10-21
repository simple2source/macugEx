# -*- coding: utf-8 -*-
"""
每个腕表连接所用的数据库缓存类
处理新建腕表数据
缓存腕表更新的数据
"""
from core.db import db

__all__ = ['ModelProxy', 'ModelNotExist']


class ModelNotExist(Exception):
    pass


class DeviceModelProxy(object):
    __slots__ = ('_id', '_data', '_update')

    def __new__(cls, imei):
        """
        if the class init failed!
        Exception RuntimeError: 'maximum recursion depth exceeded while calling a Python object' in <bound method WatchModelProxy.__del__ of <model.WatchModelProxy object at 0x102507fa0>> ignored
        """
        obj = super(DeviceModelProxy, cls).__new__(cls)
        object.__setattr__(obj, '_data', {})
        object.__setattr__(obj, '_update', {})
        object.__setattr__(obj, '_id', imei)
        return obj

    def check_document_exist(self):
        _model = db.device.find_one({'_id': self._id})
        if _model:
            object.__setattr__(self, '_data', _model)
            # miss handle self._update, buggy..
            return True
        else:
            return False

    def reload(self, retain=False):
        if self._update:
            if retain:
                result = db.device.update_one({'_id': self._id}, {'$set': self._update})
                if not result.matched_count:
                    raise ModelNotExist
            object.__setattr__(self, '_update', {})
        model = db.device.find_one({'_id': self._id})
        if not model:
            raise ModelNotExist
        object.__setattr__(self, '_data', model)

    def save(self):
        if self._update:
            db.device.update_one({'_id': self._id}, {'$set': self._update})
            object.__setattr__(self, '_update', {})

    def get(self, key, d=None):
        return self._data.get(key, d)

    def __getitem__(self, key):
        return getattr(self, key, None)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        return key in self._data

    def __getattr__(self, attr):
        return self._data.get(attr)

    def __setattr__(self, attr, value):
        """
        设置的属性和缓存中不一致时保存到 _update 字典
        重要的属性需要立刻同步到数据库中
        其他的属性在生命周期结束时,将 _update 中的数据同步到数据库
        """
        if value != self._data.get(attr):
            self._update[attr] = value
            self._data[attr] = value

    def __del__(self):
        if self._update:
            db.device.update_one({'_id': self._id}, {'$set': self._update}, upsert=True)


ModelProxy = DeviceModelProxy
