# -*- coding: utf-8 -*-
import gevent
import time

__all__ = ['ExpireBuffer', 'CacheBuffer']


class ExpireBuffer(object):
    def __init__(self, expire=60, check_cycle=None):
        """
        :param expire: buffer字典键过期时间
        :param check_cycle: buffer检查清理过期字典键的周期
        :return:
        """
        self.__key_expire = {}
        if check_cycle is None:
            self.cycle = expire * 2
        elif check_cycle < expire:
            raise ValueError('linger time must largest that expire time')
        else:
            self.cycle = check_cycle
        self.expire = expire
        gevent.spawn(self.__start)

    def get_timestamp(self, key):
        return self.__key_expire.get(key)

    def __getitem__(self, key):
        if key in self.__key_expire and time.time() - self.__key_expire[key] < self.expire:
            return True
        else:
            raise KeyError

    def __setitem__(self, key, value):
        self.__key_expire[key] = value

    def __delitem__(self, key):
        del self.__key_expire[key]

    def __contains__(self, key):
        if key in self.__key_expire and time.time() - self.__key_expire[key] < self.expire:
            return True
        else:
            return False

    def __len__(self):
        return len(self.__key_expire)

    def __iter__(self):
        return iter(self.__key_expire)

    def update(self, key):
        self.__key_expire[key] = time.time()

    def __flush_cache(self):
        now = time.time()
        stale = []
        for key, ktime in self.__key_expire.items():
            if now - ktime > self.expire:
                stale.append(key)
        for key in stale:
            del self.__key_expire[key]

    def __start(self):
        while 1:
            gevent.sleep(self.cycle)
            self.__flush_cache()


class CacheBuffer(object):
    def __init__(self, expire=120):
        """
        :param expire: buffer刷新键值时间
        :return:
        """
        self.__cache = {}
        self.expire = expire
        gevent.spawn(self.__start)

    def get(self, key, d=None):
        return self.__cache.get(key, d)

    def __getitem__(self, key):
        return self.__cache[key]

    def __setitem__(self, key, value):
        self.__cache[key] = value

    def __delitem__(self, key):
        del self.__cache[key]

    def __contains__(self, key):
        return key in self.__cache

    def __len__(self):
        return len(self.__cache)

    def __iter__(self):
        return iter(self.__cache)

    def __flush_cache(self):
        self.__cache.clear()

    def __start(self):
        while 1:
            gevent.sleep(self.expire)
            self.__flush_cache()
