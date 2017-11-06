# -*- coding:utf-8 -*-
# http://blog.jobbole.com/21351/  理解元类

# 元类是用来创建类的类,type是创建元类的类，type本身就是type的元类


# 使用type创建一个普通类,类本身也是一个对象

def eat():
    print('eating....')

Fish = type('Fish', (object,), {'color': 'blue', 'eat': eat})
fish = Fish()
print(Fish.__dict__)   # 继承了object中的魔术方法
print(object.__dict__)

# 创建一个元类，元类继承自type
# 步骤：1、type创建元类，2、元类创建普通类
# 使用元类创建类，默认将其首先变为大写开头，（注意这里是类属性，不适实例属性，实例属性在__init__方法中生成）


# 方法1
class UpperMetaClass(type):
    def __new__(mcs, cls_name, bases, dct):
        attrs = ((name, value) for name, value in dct.items() if not name.startswith('__'))
        upper_dct = dict((name.upper(), value) for name, value in attrs)
        return type.__new__(mcs, cls_name, bases, upper_dct)
        # return type(cls_name, bases, upper_dct)


# 方法2
class UpperMetaClass2(type):
    def __new__(mcs, cls_name, bases, dct):
        attrs = ((name, value) for name, value in dct.items() if not name.startswith('__'))
        upper_dct = dict((name.upper(), value) for name, value in attrs)
        print(mcs, cls_name, '......')
        return super(UpperMetaClass2, mcs).__new__(mcs, cls_name, bases, upper_dct)


class FlyFish(object):
    __metaclass__ = UpperMetaClass2
    name = 'fls'

    def ming(self):
        print('swmming...')


# 类增加属性
class AttrMetaClass(type):

    def __init__(cls, name, bases, attrs):
        cls.abc = 'abc'
        super(AttrMetaClass, cls).__init__(name, bases, attrs)


class ShaFish(object):
    __metaclass__ = AttrMetaClass

print(ShaFish.__dict__)

