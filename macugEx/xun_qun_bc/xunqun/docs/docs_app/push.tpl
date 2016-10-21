### 推送服务器

MQTT服务器：

> **xq.push.ios16.com:1883**

> **xq.push.mobilebrother.net:1883**

MQTT客户端：

	账号：{{username}}
	密码：{{password}}
	圈子频道："{{prefix}}/group/<group_id>/#"
	用户频道："{{prefix}}/user/<user_id>/#"
	服务器频道："{{prefix}}/app/status"
	服务器频道："{{prefix}}/app/receipt" (未使用)

### ios APP使用MQTT推送说明

APP在前台时,发送(连接时建议设定心跳时间为60s):

```
{
    "user_id": < str >, //用户id
    "focus": 1
}
```

到 `{{prefix}}/app/status` 频道;

APP在后台时,发送(APP客户端在连接时建议将Last Will设置为该频道,消息):

```
{
    "user_id": < str >, //用户id
    "focus": 0
}
```

到 `{{prefix}}/app/status` 频道;

当ios APP在前台并发送了focus状态到`{{prefix}}/app/status`频道后,
所有 content_available = 1 的APNS推送消息转为MQTT推送消息.

### 推送消息格式

#### 圈子语音消息

* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id
	* "**message_id**": < str >
	* "**sender**": < str >  // 用户发为userid，腕表发为imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**type**": < int > // 消息类型：1
	* "**content**": < str >  // 语音url
	* "**length**": < int >  // 语音时长
	* "**timestamp**": < float >
* }

#### 圈子图像消息

* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id
	* "**message_id**": < str >
	* "**sender**": < str >  // 用户发为userid，腕表发为imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**type**": < int > // 消息类型：2
	* "**content**": < str >  // 图像url
	* "**timestamp**": < float >
* }

#### 圈子文本消息

* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id
	* "**message_id**": < str >
	* "**sender**": < str >  // 用户发为userid，腕表发为imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**type**": < int > // 消息类型：3
	* "**content**": < str >  //文本内容
	* "**timestamp**": < float >
* }

#### 腕表定位推送
* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "watch_locate"
	* "**type**": < int >   // 定位类型：1:GPS类型，2:LBS类型
	* "**locus**": < int >// 是否轨迹点，1是，0否
	* "**imei**": < str >  // 腕表imei
	* "**radius**": < int > // lbs定位的定位精度，gps定位时固定为0
	* "**lat**": < float >
	* "**lon**": < flaot >
	* "**timestamp**": < float >
* }

#### 成员定位
* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "user_locate"
	* "**user_id**": < str >
	* "**lat**": < float >
	* "**lon**": < float >
	* "**timestamp**": < float >
}

#### 请求用户定位
* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "request_user_locate"
	* "**group_id**": < long >  //请求的圈子id
	* "**user_id**": < str >   //请求的用户id
* }

#### 圈子消息回执
* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "talk_status"
	* "**group_id**": < long >  //消息圈子id 
	* "**message_id**": < str >  //消息id
	* "**timestamp**": < float >
	* "**status**": <status>  //消息状态，1为收到，0为未收到
* }

#### 故事下载完毕消息
* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id
	* "**message_id**": < str >
	* "**sender**": < str >  //腕表imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：5
	* "**content**": < str >  //反馈文本消息
	* "**story_id**": < str >  //故事id
	* "**status**": < int >  //下载状态，1为完成，0为未完成
* }

#### 腕表低电量
* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id 
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //腕表imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：6
	* "**percent**": < int >  //腕表电量百分比
* }

#### 腕表新短信消息
* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id 
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //腕表imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：7
	* "**phone**": < str >  //短信发送方号码
	* "**content**": < str >  //短信内容
* }

#### 腕表存储卡容量不足消息
* apns参数: {'alert': u'手表存储卡容量不足', 'sound': 'default', 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id 
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //腕表imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：8
* }

#### 腕表存储卡读取异常消息
* apns参数: {'alert': u'手表存储卡读取异常', 'sound': 'default', 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id 
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //腕表imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：9
* }

#### 腕表脱落告警消息
* apns参数: {'alert': u'手表脱落告警', 'sound': 'default', 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id 
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //腕表imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：10
* }

#### 腕表进入休眠模式消息
* apns参数: {'alert': u'手表进入休眠模式', 'sound': 'default', 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id 
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //腕表imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：11
* }

#### 成员进入家庭圈消息
* apns参数: {'alert': u'新成员进入圈子', 'sound': 'default', 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //进入的圈子id
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //进入圈子的用户id
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：12
	* "**user_id**": < str >   //该用户id
	* "**user_name**": < str >   //该用户昵称
	* "**user_image_url**": < str >   //该用户头像url
	* "**phone**": < str >   //该用户手机号
	* "**share_locate**": < str >   //该用户位置共享开关
* }

#### 成员离开家庭圈消息
* apns参数: {'alert': u'有成员离开圈子', 'sound': 'default', 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //离开的圈子id
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //发送者id(将用户移出圈子的操作者,可能是用户自己)
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：13
	* "**user_id**": < str >   //该用户id（可能为用户自己的user_id）
	* "**operator**": < str >   //操作者用户id(将用户移出圈子的操作者,可能是用户自己)
* }

#### 腕表进入家庭圈消息
* apns参数: {'alert': u'新手表进入圈子', 'sound': 'default', 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**":< long >  //进入的圈子id
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //添加该腕表的用户id
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：14
	* "**imei**": < str >   //该腕表imei
	* "**operator**": < str >   //操作者用户id（可能为用户自己的user_id）
	* "**mac**": < str >   //该腕表mac
	* "**dev_name**": < str >   //该腕表昵称
	* "**dev_image_url**": < str >   //该腕表头像url
	* "**phone**": < str >   //该腕表手机号
	* "**fast_call_phone**": < str >   //该腕表快速拨打号码
	* "**lock_status**": < str >   //该腕表锁定状态
	* "**fall_status**": < str >   //该腕表脱落告警状态
* }

#### 腕表离开家庭圈消息
* apns参数: {'alert': u'有手表离开圈子', 'sound': 'default', 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**":< long >  //离开的圈子id
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //删除该腕表的用户id
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：15
	* "**imei**": < str >   //该腕表imei
	* "**operator**": < str >   //操作者用户id（可能为用户自己的user_id）
* }

#### 腕表上下线消息
* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id 
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //腕表imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：16
	* "**status**": < int > //1:上线，2:下线
* }

#### 腕表加解锁消息
* apns参数: {'alert': u'手表已被锁定', 'sound': 'default', 'data': data}
* apns参数: {'alert': u'手表已被解锁', 'sound': 'default', 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //对腕表进行操作的用户id
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：17
	* "**lock_status**": < int > //0:未锁定、1:已锁定
	* "**imei**": < str > //腕表imei
* }

#### 腕表故事已阅消息
* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：18
	* "**content**": < str >, //故事反馈具体文本消息
	* "**story_id**": < str >, //故事id
* }

#### 腕表新勋章状态消息
* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "talk"
	* "**group_id**": < long >  //消息圈子id
	* "**message_id**": < str >  //消息id
	* "**sender**": < str >  //imei
	* "**sender_type**": < int > // 1:用户，2:腕表
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：19
	* "**medal_id**": < str >, //勋章id
	* "**status**": < status >, //勋章状态（1:已获得，0:未获得）
* }

#### 合并推送消息 (未使用)
* apns参数: {'content_available': 1, 'data': data}
* data: {
	* "**push_type**": "merge"
	* "**push_list**": < data >  //推送消息，为上面所有消息类型的消息体
* }

