# -*- coding:utf-8 -*-

import time
from functools import wraps
import inspect

# cache装饰器，允许过期


def add(a, b):
    return a+b

add(1, 2)
