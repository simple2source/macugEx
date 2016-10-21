### 服务器地址

接口访问url前缀:

> **<https://app.ios16.com:8080/v1>**

> **<https://app.mobilebrother.net:8080/v1>**

接口访问方式为 POST 请求

成功返回参数：

* {
    * status : 200,
    * data: data    
* }

失败返回参数：

* {
    * status : 300,
    * data: {
        * error: 错误代码,
        * field: 错误字段(如果错误因为该请求字段引起时存在)
        * debug: 具体错误原因(服务器调试时存在)
    * }    
* }

语言选择,所有接口都可以通过设置语言参数获得对应字符串:

* chinese: 中文(默认)
* english: 英语

#### 新用户创建圈子
* URL: **/group_create**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **group_name**| |圈子xxx|1~20|圈子名字
    **brief**| | |1~80|圈子简介
    **group_image**| | | |圈子头像（JPEG格式，base64编码）
    **brief**| | |1~80|圈子简介
    **password**| | |3~20|圈子密码
    **group_email**| | | |圈子邮箱
    **user_name**| |APP用户xxx|1~20|用户圈子昵称
    **user_image**| | | |用户头像（JPEG格式，base64编码）
    **phone**| | | |用户圈子手机号
    **identify**| | |1~80|APP包名

* 返回data:

```
{
    'group_id': < long >, //圈子id
    'session': < str >, //用户session,12位字符串
    'user_id': < str >, //用户id
    'user_name': < str >, //用户名字
    'user_image_url': < str > //用户头像url
}
```

* 圈子id:

    圈子id为1000000000到9999999999之间的数字

#### 新建圈子
* URL: **/group_new**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_name**| |圈子xx|1~20|圈子名字
    **password**| | |3~20|圈子密码
    **brief**| | |1~80|圈子简介
    **group_email**| | | |圈子邮箱
    **group_image**| | | |圈子头像（JPEG格式，base64编码）
    **user_image**| | | |用户圈子头像
    **user_name**| |APP用户xx|1~20|用户圈子昵称
    **phone**| | | |用户圈子手机号
    **identify**| | |1~80|APP包名

* 返回data:

```
{
    'group_id': < long >, //圈子id
    'user_image_url': < str > //用户头像url
}
```

#### 修改圈子中的个人信息
* URL: **/group_modify_user_info**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|成员session
    **group_id**|Y| |10|圈子id
    **user_name**| | |1~20|用户在圈子中的昵称
    **phone**| | |3~20|用户在圈子中的手机号
    **user_image**| | | |用户头像（JPEG格式，base64编码）
    **share_locate**| | | |是否共享用户位置（1、0）

* 返回data:

```
{
    'user_image_url': < str > //用户头像url
}
```

#### 请求腕表验证码
* URL: **/watch_get_authcode**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **imei**|Y| |15|腕表imei

* 返回data:

```
{
    'crypt_authcode': < str > //加密后的腕表验证码（base64编码）
}
```

#### 添加腕表
* URL: **/group_new_watch**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|成员session
    **group_id**|Y| |10|圈子id
    **imei**|Y| |15|设备imei
    **authcode**|Y| |6|设备验证码
    **watch_name**| |手表用户xxx|1~20|设备昵称
    **phone**| | |3~20|设备手机号
    **watch_image**| | | |设备头像(JPEG格式图片，base64编码)
    **user_phone**| | |3~20|用户手机号
    **identify**| | |1~80|APP包名
    **customer_id**| | |非负整数|腕表客户号

* authcode:

    APP通过与腕表进行蓝牙交互获得 imei、authcode、customer_id 参数(已弃用,下版本会被移除),
    蓝牙交互见APP蓝牙文档;<br/>
    APP通过扫描腕表二维码获得 imei、authcode、customer_id 参数,扫描二维码后得到的链接例如为:

        http://fir.im/xq02?imei=355372020827303&authcode=123456&ttl=1469934156.173931&customer_id=1

    ttl 参数为该二维码的过期时间,用于本地判断。


* 返回data:

```
{
    'dev_image_url': < str > //腕表头像url
}
```

#### 生成邀请
* URL: **/group_generate_invite**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|成员session
    **group_id**|Y| |10|圈子id

* 返回data:

```
{
    'invitecode': < str > //邀请验证码
    'ttl': < int >    //验证码有效时间（秒）
}
```

#### 接受邀请
* URL: **/group_accept_invite**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **invitecode**|Y| |6|邀请码
    **group_id**|Y| |10|圈子id

* 返回data:

```
{
    'group_password': < str > //圈子密码
}
```

#### 进入圈子
* URL: **/group_enter**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **group_id**|Y| |10|圈子id
    **group_password**|Y(1)| |3~20|圈子密码
    **invitecode**|Y(1)| |6|圈子邀请码
    **session**|Y| |12|用户session
    **user_name**| |(用户名,APP用户xxx)|1~20|用户圈子昵称
    **user_image**| | | |用户圈子头像（JPEG格式，base64编码）
    **phone**| | |3~20|用户圈子手机
    **identify**| | |1~80|APP包名

* 返回data:

```
{
    'user_image_url': < str > //用户头像url
}
```
    
#### 新用户进入圈子
* URL: **/group_join**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **group_id**|Y| |10|圈子id
    **group_password**|Y(1)| |3~20|圈子密码
    **invitecode**|Y(1)| |6|圈子邀请码
    **user_name**| |APP用户xxx|1~20|用户圈子昵称
    **user_image**| | | |用户圈子头像（JPEG格式，base64编码）
    **phone**| | |3~20|用户圈子手机
    **identify**| | |1~80|APP包名

* 返回data:

```
{
    'session': < str > //用户session
    'user_id': < str > //用户id
    'user_name': < str > //用户名字
    'user_image_url': < str > //用户头像url
}
```

#### 移出成员
* URL: **/group_remove**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **group_id**|Y| |10|圈子id
    **session**|Y| |12|用户session
    **user_id**|Y| |12|移出成员的id

* 返回data:

```
{}
```

#### 圈子详情
* URL: **/group_info**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **group_id**|Y| |10|圈子id
    **session**|Y| |12|用户session
    **timestamp**| | | |时间戳

* 返回data:

```
{
    'group_name': < str >, //圈子名字
    'brief': < str >, //圈子简介
    'password': < str >, //圈子密码
    'group_email': < str >, //圈子邮箱
    'group_image_url': < str >, //圈子图像url
    'users': [ //圈子用户列表（列表中为有变化的记录）
        {
            'user_id': < str >, //用户id
            'user_name': < str >, //用户圈子昵称
            'user_image_url': < str >, //用户头像url
            'phone': < str >, //用户手机号
            'share_locate': < int >, //用户位置共享开关
            'status': < str > //用户在圈子状态（0:已删除、1:已进入）
        }
    ],
    'devs': [ //圈子设备列表（列表中为有变化的记录）
        {
            'imei': < str >, //腕表imei
            'mac': < str >, //腕表mac
            'group_id': < int >, //圈子id
            'dev_name': < str >, //腕表名字
            'dev_image_url': < str >, //腕表头像url
            'phone': < str >, //腕表手机号
            'fast_call_phone': < str >, //腕表一键拨打号码
            'lock_status': < int >, //腕表锁定状态（0:未锁定、1:已锁定）
            'fall_status': < int >, //腕表脱落告警状态（0:未启用、1:已启用）
            'gps_strategy': < str >, //腕表gps策略
            'status': < int > //腕表在圈子状态（0:已删除、1:已进入）
        }
    ],
    'contacts': [ //圈子设备列表（列表中为有变化的记录）
        {
            'phone': < str >, //联系人手机号
            'contact_name': < str >, //联系人名称
            'contact_image_url': < str >, //联系人头像
            'status': < int >, //联系人在圈子状态（0:已删除、1:已添加）
        }
    ],
    'group_timestamp': < float >, //圈子最后更新时间戳
}
```

#### 用户圈子列表
* URL: **/user_group_list**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **timestamp**| | | |时间戳

* 返回data:

```
[ //用户圈子列表
    {
        'group_id': < str >, //圈子id
        'group_name': < str >, //圈子昵称
        'group_image_url': < str >, //圈子头像
        'status': < int > //圈子状态（0:已退出、1:已进入）
        'timestamp': < float > //进入或退出时间戳
    }
]
```

* 圈子被删除时:

    若用户圈子status为0时，该圈子被删除或用户退出该圈子;

#### 添加圈子联系人
* URL: **/group_add_contact**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id
    **contact_name**| |通讯录用户xx|1~20|联系人昵称
    **phone**|Y| |3~20|联系人手机号(手机号唯一，重复则覆盖联系人信息)
    **identify**| | |1~80|APP包名

* 返回data:

```
{
    'contact_name': < str >, //通讯录用户昵称
    'contact_image_url': < str > //通讯录用户头像
}
```

#### 删除圈子联系人
* URL: **/group_del_contact**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id
    **phone**|Y| |3~20|联系人手机号(手机号唯一，重复则覆盖联系人信息)

* 返回data:

```
{}
```

#### 发送圈子消息
* URL: **/group_message_send**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id
    **type**|Y| |(1,2,3)|消息类型（1：audio，2：image，3：text）
    **content**|Y| | |消息内容（语音消息为amr格式语音base64，图片消息为jpg格式图片base64，文本消息为utf8字符串）
    **length**|Y*| |0<x<=20|语音长度，如果消息类型为1则必填

* 返回data:

```
{
    'message_id': < str >, //消息id
    'content_url': < str > //内容（语音及图片为url链接，文本类型为""）
}
```

#### 接收圈子消息
* URL: **/group_message_recv**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **message_id**|Y| |24|前一页最后一条消息的id
    **sort**| |-1|(1,-1)|消息的获取顺序,默认是倒序-1

* 返回data枚举:

```
{ //圈子语音消息
    'message_id': < str >, //消息id
    'type': 1
    'content': < str >, //语音url
    'length': < int >, //语音长度
    'sender': < str >, //发送者id
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float >, //消息时间戳
    'status': < int > //消息回执标识（1收到，或0未收到）
},
{ //圈子图片消息
    'message_id': < str >, //消息id
    'type': 2
    'content': < str >, //图片url
    'sender': < str >, //发送者id
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float >, //消息时间戳
    'status': < int > //消息回执标识（1收到，或0未收到）
},
{ //圈子文本消息
    'message_id': < str >, //消息id
    'type': 3
    'content': < str >, //文本内容
    'sender': < str >, //发送者id
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float >, //消息时间戳
    'status': < int > //消息回执标识（1收到，或0未收到）
},
/* { //腕表轨迹点消息(没用到)
    'message_id': < str >, //消息id
    'type': 4,
    'watch_locate': {
        "lat": < float >, //纬度
        "lon": < float >, //经度
        "type": < int >, //类型（1、2）
        "radius": < int >, //半径
        "address": < str >, //轨迹点定位地址
    },
    'sender': < str >, //腕表imei
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
}, */
{ //腕表故事确认消息
    'message_id': < str >, //消息id
    'type': 5,
    'content': < str >, //故事反馈具体文本消息
    'story_id': < story_id >, //故事id
    'status': < status >, //故事接收状态（1下载完成，0失败）
    'sender': < str >, //腕表imei
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表低电量消息
    'message_id': < str >, //消息id
    'type': 6,
    'percent': < int >, //电量百分比（0~100）
    'sender': < str >, //腕表imei
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表短信消息
    'message_id': < str >, //消息id
    'type': 7,
    'phone': < str >, //短信发送方号码
    'content': < str >, //短信消息
    'sender': < str >, //腕表imei
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表存储卡容量不足
    'message_id': < str >, //消息id
    'type': 8,
    'sender': < str >, //腕表imei
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表存储卡读取异常
    'message_id': < str >, //消息id
    'type': 9,
    'sender': < str >, //腕表imei
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表脱落告警
    'message_id': < str >, //消息id
    'type': 10,
    'sender': < str >, //腕表imei
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表进入休眠模式
    'message_id': < str >, //消息id
    'type': 11,
    'sender': < str >, //腕表imei
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //用户进入圈子
    'message_id': < str >, //消息id
    'type': 12,
    'sender': < str >, //进入圈子的用户id
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //用户离开圈子
    'message_id': < str >, //消息id
    'type': 13,
    'user_id': < str >, //被删除用户user_id
    'sender': < str >, //发送者id(将用户移出圈子的操作者,可能是用户自己)
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表进入圈子
    'message_id': < str >, //消息id
    'type': 14,
    'imei': < str >, //进入圈子内的腕表imei
    'sender': < str >, //添加该腕表的用户id
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表离开圈子
    'message_id': < str >, //消息id
    'type': 15,
    'imei': < str >, //离开圈子的腕表imei
    'sender': < str >, //删除该腕表的用户id
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表上下线消息
    'message_id': < str >, //消息id
    'type': 16,
    'status': < int >, //1:上线，2:下线
    'sender': < str >, //腕表imei
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表加解锁消息
    'message_id': < str >, //消息id
    'type': 17,
    'lock_status': < int >, //0:未锁定、1:已锁定
    'imei': < str >, //腕表imei
    'sender': < str >, //对腕表进行操作的用户id
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表故事已阅消息
    'message_id': < str >, //消息id
    'type': 18,
    'content': < str >, //故事反馈具体文本
    'story_id': < story_id >, //故事id
    'sender': < str >, //腕表imei
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
},
{ //腕表新勋章状态消息
    'message_id': < str >, //消息id
    'type': 19,
    'medal_id': < str >, //勋章id
    'status': < status >, //勋章状态（1:已获得，0:未获得）
    'sender': < str >, //腕表imei
    'sender_type': < int >, //发送者类型（1:用户、2:腕表）
    'timestamp': < float > //消息时间戳
}
```

#### 绑定deviceToken
* URL: **/user_bind_devicetoken**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **devicetoken**|Y| |64|用户devicetoken（64位）
    **identify**|Y| |1~80|ios应用包名
    **version**|Y| |("produce","develop")|ios版本（token或identify或version为空则用户为安卓用户）

* 返回data:

```
{}
```

#### 修改圈子信息
* URL: **/group_modify_info**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id
    **group_image**| | | |圈子头像（JPEG格式，base64编码）
    **group_name**| | |1~20|圈子新名字
    **newpassword**| | |3~20|圈子新密码
    **group_email**| | | |圈子新邮箱

* 返回data:

```
{
    'group_image_url': < str > //圈子头像url
}
```

#### 圈子联系人列表
* URL: **/group_contact_list**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id

* 返回data:

```
[ //联系人列表
    {
        'contact_name': < str >, //联系人名字
        'phone': < str >, //联系人手机号
        'type': < int > //0：联系人，1：家庭成员，2：腕表
    }
]
```

#### 请求腕表定位
* URL: **/watch_request_locate**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei
    **type**| |"gps"|("gps","lbs")|请求腕表定位的类型

* 返回data:

```
{}
```

#### 结束腕表定位
* URL: **/watch_finish_locate**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{}
```

#### 锁定腕表
* URL: **/watch_locking**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{}
```

#### 解锁腕表
* URL: **/watch_unlock**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{}
```

#### 监听腕表
* URL: **/watch_monitor**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{
    'monitor_user_id': < str > //当前监听该腕表的用户id
}
```

#### 腕表重新登陆
* URL: **/watch_relogin**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{}
```

#### 重启腕表
* URL: **/watch_reboot**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{}
```

#### 腕表开启飞行模式
* URL: **/watch_fightmode**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{}
```

#### 设置腕表闹铃
* URL: **/watch_alarm_set**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei
    **id**| | |6|闹铃id（不填时为新建闹铃且status不能为delete）
    **status**| |不填id时为on|(on,off,delete)|闹铃状态
    **cycle**|Y*|"1,2,3,4,5"(新建闹钟时)|0<x<14|重复星期数（星期列表，1~7，eg:"1,2,5,7"）
    **time**| |"08:00"(新建闹钟时)|5|时间（闹铃时间字符串，eg:"08:00"）
    **label**| |"闹铃"(新建闹钟时)|0<x<20|闹铃标签
    **pattern**| |("cycle","single")|0<x<20|闹铃模式(如果模式为 single，cycle参数必填且只能设定一个星期数)

* 返回data:

```
{
    'id': < int >, //闹铃id
}
```

#### 获取腕表闹铃
* URL: **/watch_alarm_get**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
[ //闹铃列表
    {
        'id': < int >, //闹铃id
        'status': < str >, //闹铃状态
        'cycle': [ //重复星期数列表
            < int >, //星期数(1~7)
        ],
        'time': < str >, //时间
        'label': < str >, //标签
        'pattern': < str >, //模式
    }
]
```

#### APP上传定位
* URL: **/user_upload_locate**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **type**|Y| |(1,2)|定位类型（1为定期上传的定位，2为收到定位请求后上传的定位）
    **lon**|Y| |火星坐标系|经度
    **lat**|Y| |火星坐标系|纬度
    **radius**|Y| |整型|定位半径

* 返回data:

```
{}
```

#### 查询用户信息
* URL: **/user_info**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id
    **user_id**|Y| |12|用户id

* 返回data:

```
{
    'user_id': < str >, //用户id
    'user_name': < str >, //用户圈子昵称
    'user_image_url': < str >, //用户头像url
    'phone': < str >, //用户手机号
    'share_locate': < int >, //用户位置共享开关
}
```

#### 删除腕表
* URL: **/group_del_watch**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id
    **imei**|Y| |15|腕表imei
    **throughly**| |1|(0,1)|是否彻底删除腕表数据,默认开启

* 返回data:

```
{}
```

#### 查询腕表信息
* URL: **/watch_info**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y(1)| |15|腕表imei
    **mac**|Y(1)| |12|腕表mac

* 返回data:

```
{
    'imei': < str >, //腕表imei
    'mac': < str >, //腕表mac
    'group_id': < int >, //圈子id
    'dev_name': < str >, //腕表名字
    'dev_image_url': < str >, //腕表头像url
    'lock_status': < int >, //腕表锁定状态
    'fall_status': < int >, //腕表脱落告警状态（0:未启用、1:已启用）
    'phone': < str >, //腕表手机号
    'fast_call_phone': < str >, //一键拨打号码
    'gps_strategy': < str >, //腕表gps策略
}
```

#### 修改腕表信息
* URL: **/group_modify_watch_info**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id
    **imei**|Y| |15|腕表imei
    **watch_name**| | |1~20|腕表昵称
    **phone**| | |3~20|腕表手机号
    **watch_image**| | | |设备头像(JPEG格式图片，base64编码)
    **fast_call_phone**| | |(3~20, 'delete')|一键拨打号码（要为设备联系人中的号码，如果需要删除腕表一键拨打号码，值为"delete"）
    **gps_strategy**| | |('default', 'delete')|设置腕表gps调试策略时只能设置为'default',删除策略时为'delete'

* 返回data:

```
{
    'dev_image_url': < str >, //设备头像url
}
```

#### 查询腕表轨迹信息
* URL: **/watch_locus**

* 分组1、2都不填时,查询当天早上至今的所有轨迹点
* `type` 不填为请求所有类型轨迹点,请求如下:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei
    **page**|(1)|0|0~50|页数
    **num**|(1)|10|1~50|每页个数
    **start_timestamp**|(2)| | |开始时间戳
    **end_timestamp**|(2)| | |结束时间戳
    **type**| | |('gps','lbs')|轨迹定位点类型

* 返回data:

```
[ //轨迹列表
    {
        'type': < int >, //1(GPS定位方式)、2(基站定位方式)
        'lon': < float >, //经度
        'lat': < float >, //纬度
        'radius': < int >, //轨迹有效半径
        'timestamp': < float >, //时间戳
    }
]
```

#### 查询腕表每天轨迹条数
* URL: **/watch_locus_datenum**

* 时间戳都不填时,查询90天前至今的每天轨迹条目,请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei
    **start_timestamp**| | | |开始天数00:00时间戳
    **end_timestamp**| | | |结束天数00:00时间戳

* 返回data:

```
[ //每天轨迹数目列表
    {
        'timestamp': < float >, //日期00:00时间戳
        'gps_num': < int >, //gps条数
        'lbs_num': < int >, //lbs条数
    }
]
```

* 日期:

    日期为时间戳转换为GMT时间

#### 查询腕表定位记录
* URL: **/watch_locate**

* 分组1、2都不填时,查询最后一条定位记录,请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei
    **page**|(1)|0|0~50|页数
    **num**|(1)|10|1~50|每页个数
    **start_timestamp**|(2)| | |开始时间戳
    **end_timestamp**|(2)| | |结束时间戳

* 返回data:

```
[ //定位记录列表
    {
        'type': < int >, //1(GPS定位方式)、2(基站定位方式)
        'lon': < float >, //经度
        'lat': < float >, //纬度
        'radius': < int >, //半径
        'timestamp': < float >, //时间戳
    }
]
```

#### 查询用户轨迹信息
* URL: **/user_locus**

* 分组1、2都不填时,查询当天早上至今的所有轨迹点,请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id
    **user_id**|Y| |12|被查询用户的id
    **page**|(1)|0|0~50|页数
    **num**|(1)|10|1~50|每页个数
    **start_timestamp**|(2)| | |开始时间戳
    **end_timestamp**|(2)| | |结束时间戳

* 返回data:

```
[ //轨迹列表
    {
        'lon': < float >, //经度
        'lat': < float >, //纬度
        'radius': < int >, //轨迹有效半径
        'timestamp': < float >, //时间戳
    }
]
```

#### 查询用户定位记录
* URL: **/user_locate**

* 分组1、2都不填时,查询最后一条定位记录,请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id
    **user_id**|Y| |12|被查询用户的id
    **page**|(1)|0|0~50|页数
    **num**|(1)|10|1~50|每页个数
    **start_timestamp**|(2)| | |开始时间戳
    **end_timestamp**|(2)| | |结束时间戳

* 返回data:

```
[ //定位记录列表
    {
        'lon': < float >, //经度
        'lat': < float >, //纬度
        'radius': < int >, //半径
        'timestamp': < float >, //时间戳
    }
]
```

#### 请求用户定位
* URL: **/user_request_locate**

* 分组1、2都不填时,查询最后一条定位记录,请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **group_id**|Y| |10|圈子id
    **user_id**|Y| |12|用户id

* 返回data:

```
{}
```

#### 开启腕表脱落告警
* URL: **/watch_falling**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{}
```

#### 关闭腕表脱落告警
* URL: **/watch_unfalling**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{}
```

#### APP预激活腕表
* URL: **/group_active_watch_request**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**| | |12|成员session
    **group_id**| | |10|圈子id
    **imei**|Y| |15|设备imei
    **mac**|Y| |12|设备mac
    **watch_name**| |手表用户xxx|1~20|设备昵称
    **phone**| | |3~20|设备手机号
    **watch_image**| | | |设备头像(JPEG格式图片，base64编码)
    **user_phone**| | |3~20|用户手机号
    **identify**| | |1~80|APP包名
    **customer_id**| | |非负整数|腕表客户号

* 返回data:

```
{
    'user_id': < str >, //正在添加该腕表的用户id,当前没有人添加腕表的时候user_id是用户自己
    'timestamp': < float > //腕表被操作的时间戳,当前没有人添加腕表的时候是当前时间戳
}
```

#### APP激活腕表
* URL: **/group_active_watch**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|成员session
    **group_id**|Y| |10|圈子id
    **imei**|Y| |15|设备imei
    **mac**|Y| |12|设备mac
    **watch_name**| |手表用户xxx|1~20|设备昵称
    **phone**| | |3~20|设备手机号
    **watch_image**| | | |设备头像(JPEG格式图片，base64编码)
    **user_phone**| | |3~20|用户手机号
    **identify**| | |1~80|APP包名
    **customer_id**| | |非负整数|腕表客户号

* 返回data:

```
{
    'dev_image_url': < str > //腕表头像url
}
```

#### 腕表gps状态信息
* URL: **/watch_gps_info**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{
    'watch_star': < int >, //腕表搜索到的卫星数目(默认-1)
    'catch_star': < int >, //腕表追踪到的卫星数目(默认-1)
    'quality': < int > //gps信号质量(默认-1)
}
```

#### 关机手表
* URL: **/watch_power_off**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{}
```

#### 新用户创建圈子并添加腕表
* URL: **/group_generate**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **imei**|Y| |15|设备imei
    **mac**|Y(1)| |12|设备mac
    **authcode**|Y(1)| |6|设备验证码
    **group_name**| |圈子xxx|1~20|圈子名字
    **brief**| | |1~80|圈子简介
    **group_image**| | | |圈子头像（JPEG格式，base64编码）
    **password**| | |3~20|圈子密码
    **group_email**| | | |圈子邮箱
    **user_name**| |APP用户xxx|1~20|用户圈子昵称
    **user_image**| | | |用户头像（JPEG格式，base64编码）
    **user_phone**| | |3~20|用户手机号
    **watch_name**| |手表用户xxx|1~20|设备昵称
    **watch_phone**| | |3~20|设备手机号
    **watch_image**| | | |设备头像(JPEG格式图片，base64编码)
    **identify**| | |1~80|APP包名
    **customer_id**| | |非负整数|腕表客户号

* mac:

    APP通过与腕表进行蓝牙交互获得 imei、authcode、customer_id 参数(已弃用),
    蓝牙交互见APP蓝牙文档;

* authcode:

    APP通过扫描腕表二维码获得 imei、authcode、customer_id 参数,扫描二维码后得到的链接例如为:

        http://fir.im/xq02?imei=355372020827303&authcode=123456&ttl=1469934156.173931&customer_id=1

    ttl 参数为该二维码的过期时间,用于本地判断;

    `authcode` 与 `mac` 参数不能同时存在。

* 返回data:

```
{
    'group_id': < long >, //圈子id
    'session': < str >, //用户session,12位字符串
    'user_id': < str >, //用户id
    'user_name': < str >, //用户名字
    'user_image_url': < str > //用户头像url
    'dev_image_url': < str > //腕表头像url
}
```

#### 创建圈子并添加腕表
* URL: **/group_make**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|设备imei
    **mac**|Y| |12|设备mac
    **group_name**| |圈子xxx|1~20|圈子名字
    **brief**| | |1~80|圈子简介
    **group_image**| | | |圈子头像（JPEG格式，base64编码）
    **password**| | |3~20|圈子密码
    **group_email**| | | |圈子邮箱
    **user_name**| |APP用户xxx|1~20|用户圈子昵称
    **user_image**| | | |用户头像（JPEG格式，base64编码）
    **user_phone**| | |3~20|用户手机号
    **watch_name**| |手表用户xxx|1~20|设备昵称
    **watch_phone**| | |3~20|设备手机号
    **watch_image**| | | |设备头像(JPEG格式图片，base64编码)
    **identify**| | |1~80|APP包名
    **customer_id**| | |非负整数|腕表客户号

* 返回data:

```
{
    'group_id': < long >, //圈子id
    'user_name': < str >, //用户名字
    'user_image_url': < str > //用户头像url
    'dev_image_url': < str > //腕表头像url
}
```

#### 用户圈子列表详情
* URL: **/user_group_watch_list**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **timestamp**| | | |时间戳

* 返回data:

```
{
    'groups': [ //用户圈子列表
        {
            'group_id': < str >, //圈子id
            'group_name': < str >, //圈子名字
            'brief': < str >, //圈子简介
            'password': < str >, //圈子密码
            'group_email': < str >, //圈子邮箱
            'group_image_url': < str >, //圈子图像url
            'devs': [ //圈子设备列表（列表中为有变化的记录）
                {
                    'imei': < str >, //腕表imei
                    'group_id': < long >, //腕表所在圈子id
                    'mac': < str >, //腕表mac
                    'dev_name': < str >, //腕表名字
                    'dev_image_url': < str >, //腕表头像url
                    'phone': < str >, //腕表手机号
                    'fast_call_phone': < str >, //腕表一键拨打号码
                    'lock_status': < int >, //腕表锁定状态（0:已锁定、1:未锁定）
                    'fall_status': < int >, //腕表脱落告警状态（0:未启用、1:已启用）
                    'gps_strategy': < str >, //腕表gps策略
                    'status': < int > //腕表在圈子状态（0:已删除、1:已进入）
                }
            ],
            'users': [ //圈子用户列表（列表中为有变化的记录）
                {
                    'user_id': < str >, //用户id
                    'user_name': < str >, //用户圈子昵称
                    'user_image_url': < str >, //用户头像url
                    'phone': < str >, //用户手机号
                    'share_locate': < int >, //用户位置共享开关
                    'status': < str > //用户在圈子状态（0:已删除、1:已进入）
                }
            ],
            'contacts': [ //圈子设备列表（列表中为有变化的记录）
                {
                    'phone': < str >, //联系人手机号
                    'contact_name': < str >, //联系人名称
                    'contact_image_url': < str >, //联系人头像
                    'status': < int >, //联系人在圈子状态（0:已删除、1:已添加）
                }
            ],
            'group_timestamp': < float >, //圈子最后更新时间戳
            'status': < int > //用户在该圈子中的状态
        }
    ]
}
```

* 圈子被删除时:

    该 group 字典数据只有: `group_id`, `status`,标识该圈已被删除;<br/>
    应同时删除该圈所有数据,包括该圈腕表信息;

#### 刷新用户session
* URL: **/renew_session**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **user_id**|Y| |12|用户的id
    **identify**| | |1~80|APP包名

* 返回data:

```
{
    'session': < str >, //用户session,12位字符串
}
```

#### 新建用户
* URL: **/new_user**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **user_name**| |游客xxx|1~20|用户昵称
    **user_image**| | | |用户头像（JPEG格式，base64编码）
    **identify**| | |1~80|APP包名

* 返回data:

```
{
    'session': < str >, //用户session,12位字符串
    'user_id': < str >, //用户id
    'user_name': < str >, //用户名字
    'user_image_url': < str > //用户头像url
}
```

#### 找回用户
* URL: **/resume_user**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **authcode**| | |4|找回验证码

* 返回data:

```
{
    'session': < str >, //用户session,12位字符串
    'user_id': < str >, //用户id
    'user_name': < str >, //用户名字
    'user_image_url': < str > //用户头像url
}
```