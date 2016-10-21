推送频道接口
================

MQTT服务器：

    **push.xxx.com:1883**

MQTT客户端：

::

    账号：xunqun
    密码：xunqun
    圈子频道："xunqun/group/<group_id>/#"
    用户频道："xunqun/user/<user_id>/#"
    服务器频道："xunqun/app/status"
    服务器频道："xunqun/app/receipt" (未使用)

ios APP使用MQTT推送说明
~~~~~~~~~~~~~~~~~~~~~~~

APP在前台时,发送(连接时建议设定心跳时间为60s):

::

    {
        "user_id": < str >, //用户id
        "focus": 1
    }

到 ``xunqun/app/status`` 频道;

APP在后台时,发送(APP客户端在连接时建议将Last Will设置为该频道,消息):

::

    {
        "user_id": < str >, //用户id
        "focus": 0
    }

到 ``xunqun/app/status`` 频道;

当ios APP在前台并发送了focus状态到\ ``xunqun/app/status``\ 频道后, 所有
content\_available = 1 的APNS推送消息转为MQTT推送消息.

推送消息格式
~~~~~~~~~~~~

圈子语音消息
^^^^^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //消息圈子id
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**message\_id**": < str >
   -  "**type**": < int > // 消息类型：1
   -  "**content**": < str > // 语音url
   -  "**length**": < int > // 语音时长
   -  "**timestamp**": < float >

-  }

圈子图像消息
^^^^^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //消息圈子id
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**message\_id**": < str >
   -  "**type**": < int > // 消息类型：2
   -  "**content**": < str > // 图像url
   -  "**timestamp**": < float >

-  }

圈子文本消息
^^^^^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //消息圈子id
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**message\_id**": < str >
   -  "**type**": < int > // 消息类型：3
   -  "**content**": < str > //文本内容
   -  "**timestamp**": < float >

-  }

腕表定位推送
^^^^^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "watch\_locate"
   -  "**type**": < int > // 定位类型：1:GPS类型，2:LBS类型
   -  "**locus**": < int >// 是否轨迹点，1是，0否
   -  "**imei**": < str > // 腕表imei
   -  "**radius**": < int > // lbs定位的定位精度，gps定位时固定为0
   -  "**lat**": < float >
   -  "**lon**": < flaot >
   -  "**timestamp**": < float >

-  }

成员定位
^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "user\_locate"
   -  "**user\_id**": < str >
   -  "**lat**": < float >
   -  "**lon**": < float >
   -  "**timestamp**": < float > }

请求用户定位
^^^^^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "request\_user\_locate"
   -  "**group\_id**": < long > //请求的圈子id
   -  "**user\_id**": < str > //请求的用户id

-  }

圈子消息回执
^^^^^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "talk\_status"
   -  "**group\_id**": < long > //消息圈子id
   -  "**message\_id**": < str > //消息id
   -  "**status**": //消息状态，1为收到，0为未收到
   -  "**timestamp**": < float >

-  }

故事下载完毕消息
^^^^^^^^^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //消息圈子id
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**message\_id**": < str >
   -  "**type**": < int > // 消息类型：5
   -  "**content**": < str > //反馈文本消息
   -  "**story\_id**": < str > //故事id
   -  "**status**": < int > //下载状态，1为完成，0为未完成
   -  "**timestamp**": < float >

-  }

腕表低电量
^^^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //消息圈子id
   -  "**message\_id**": < str > //消息id
   -  "**type**": < int > // 消息类型：6
   -  "**percent**": < int > //腕表电量百分比
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**timestamp**": < float >

-  }

腕表新短信消息
^^^^^^^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //消息圈子id
   -  "**message\_id**": < str > //消息id
   -  "**type**": < int > // 消息类型：7
   -  "**phone**": < str > //短信发送方号码
   -  "**content**": < str > //短信内容
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**timestamp**": < float >

-  }

腕表存储卡容量不足消息
^^^^^^^^^^^^^^^^^^^^^^

-  apns参数: {'alert': u'手表存储卡容量不足', 'sound': 'default',
   'data': data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //消息圈子id
   -  "**message\_id**": < str > //消息id
   -  "**type**": < int > // 消息类型：8
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**timestamp**": < float >

-  }

腕表存储卡读取异常消息
^^^^^^^^^^^^^^^^^^^^^^

-  apns参数: {'alert': u'手表存储卡读取异常', 'sound': 'default',
   'data': data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //消息圈子id
   -  "**message\_id**": < str > //消息id
   -  "**type**": < int > // 消息类型：9
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**timestamp**": < float >

-  }

腕表脱落告警消息
^^^^^^^^^^^^^^^^

-  apns参数: {'alert': u'手表脱落告警', 'sound': 'default', 'data':
   data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //消息圈子id
   -  "**message\_id**": < str > //消息id
   -  "**type**": < int > // 消息类型：10
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**timestamp**": < float >

-  }

腕表进入休眠模式消息
^^^^^^^^^^^^^^^^^^^^

-  apns参数: {'alert': u'手表进入休眠模式', 'sound': 'default', 'data':
   data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //消息圈子id
   -  "**message\_id**": < str > //消息id
   -  "**type**": < int > // 消息类型：11
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**timestamp**": < float >

-  }

成员进入家庭圈消息
^^^^^^^^^^^^^^^^^^

-  apns参数: {'alert': u'新成员进入圈子', 'sound': 'default', 'data':
   data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //进入的圈子id
   -  "**user\_id**": < str > //该用户id
   -  "**user\_name**": < str > //该用户昵称
   -  "**user\_image\_url**": < str > //该用户头像url
   -  "**phone**": < str > //该用户手机号
   -  "**share\_locate**": < str > //该用户位置共享开关
   -  "**message\_id**": < str > //消息id
   -  "**type**": < int > // 消息类型：12
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**timestamp**": < float >

-  }

成员离开家庭圈消息
^^^^^^^^^^^^^^^^^^

-  apns参数: {'alert': u'有成员离开圈子', 'sound': 'default', 'data':
   data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //离开的圈子id
   -  "**user\_id**": < str > //该用户id（可能为用户自己的user\_id）
   -  "**operator**": < str > //操作者用户id（可能为用户自己的user\_id）
   -  "**message\_id**": < str > //消息id
   -  "**type**": < int > // 消息类型：13
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**timestamp**": < float >

-  }

腕表进入家庭圈消息
^^^^^^^^^^^^^^^^^^

-  apns参数: {'alert': u'新手表进入圈子', 'sound': 'default', 'data':
   data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**":< long > //进入的圈子id
   -  "**imei**": < str > //该腕表imei
   -  "**operator**": < str > //操作者用户id（可能为用户自己的user\_id）
   -  "**mac**": < str > //该腕表mac
   -  "**dev\_name**": < str > //该腕表昵称
   -  "**dev\_image\_url**": < str > //该腕表头像url
   -  "**phone**": < str > //该腕表手机号
   -  "**fast\_call\_phone**": < str > //该腕表快速拨打号码
   -  "**lock\_status**": < str > //该腕表锁定状态
   -  "**fall\_status**": < str > //该腕表脱落告警状态
   -  "**message\_id**": < str > //消息id
   -  "**type**": < int > // 消息类型：14
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**timestamp**": < float >

-  }

腕表离开家庭圈消息
^^^^^^^^^^^^^^^^^^

-  apns参数: {'alert': u'有手表离开圈子', 'sound': 'default', 'data':
   data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**":< long > //离开的圈子id
   -  "**imei**": < str > //该腕表imei
   -  "**operator**": < str > //操作者用户id（可能为用户自己的user\_id）
   -  "**message\_id**": < str > //消息id
   -  "**type**": < int > // 消息类型：15
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**timestamp**": < float >

-  }

腕表上下线消息
^^^^^^^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "talk"
   -  "**group\_id**": < long > //消息圈子id
   -  "**message\_id**": < str > //消息id
   -  "**status**": < int > //1:上线，2:下线
   -  "**type**": < int > // 消息类型：16
   -  "**sender**": < str > // 用户发为userid，腕表发为imei
   -  "**sender\_type**": < int > // 1:用户，2:腕表
   -  "**timestamp**": < float >

-  }

合并推送消息 (未使用)
^^^^^^^^^^^^^^^^^^^^^

-  apns参数: {'content\_available': 1, 'data': data}
-  data: {

   -  "**push\_type**": "merge"
   -  "**push\_list**": < data > //推送消息，为上面所有消息类型的消息体

-  }
