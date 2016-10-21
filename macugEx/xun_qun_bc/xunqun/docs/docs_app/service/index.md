### 服务器地址

接口访问url前缀：

> **<https://app.ios16.com:8080/v1>**

> **<https://app.mobilebrother.net:8080/v1>**

请求失败时返回的一般性数据：

* {
    * status : 300,
    * error: 错误代码,
    * field: 错误字段(如果错误因为该请求字段引起时存在)
    * debug: 具体错误原因
* }

#### 客户提问问题
* URL: **/question/new**

* 发送POST参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **title**| | | |问题标题
    **label**| | | |问题标签列表字符串,eg:'["激活","安卓4.3"]'

* 说明:

    客户提问后,可以在 [客服获取'待解决'用户问题列表](./#_3) 查看该问题;

* 返回json数据:

```
{
    'status': 200,
    'question_id': < str >, //问题id
    'question': {
        'id': < str >, //问题id
        'status': < int >, //问题状态
    }
}
```

#### 客服登陆(绑定APP)
* URL: **/serv/bind**

* 发送POST参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **serv_id**|Y| |1~20|客服账号
    **password**|Y| |1~20|客服密码

* 说明:

    因为客服账号可以给多个APP使用,所以将客服账号用户与用户绑定(登录)后该手机就可以收到推送;

* 返回json数据:

```
{
    'status': 200
}
```

#### 客服获取'待解决'用户问题列表
* URL: **/question/list**

* 发送GET参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **question_id**| | |24|前一页最后一条问题的id
    **sort**| |-1|(1,-1)|消息的获取顺序,默认是倒序-1
    **label**| | | |筛选问题标签
    **identify**| | |1~80|APP包名

* 返回json数据:

```
{
    'status': 200,
    'questions': [
        {
            'question_id': < str >, //问题id
            'user_id': < str >, //提问用户
            'user_image_url': < str >, //用户头像url
            'user_name': < str >, //用户昵称
            'title': < str >, //问题标题
            'last_mess_text': < str >, //该问题最后一次聊天消息内容
            'last_mess_timestamp': < float >, //该问题最后一次聊天消息时间戳
            'last_mess_sender': < int >, //该问题最后一次聊天消息发送者
            'last_mess_sender_type': < int >, //该问题最后一次聊天消息发送者类型（1:用户、2:客服）
            'timestamp': < float >, //问题创建时间戳
        }
    ]
}
```

#### 开始回答用户问题
* URL: **/question/< question_id >/serve**

* 发送POST参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **serv_id**|Y| |1~20|客服账号

* 说明:

    客服开始回答用户问题后,该问题即从 [客服获取'待解决'用户问题列表](./#_3) 中下线;

* 返回json数据:

```
{
    'status': 200,
    'message_id': < str > //新通知消息id
}
```

#### 客服'解决中'问题列表
* URL: **/serv/< serv_id >/tasks**

* 发送GET参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **question_id**| | |24|前一页最后一条问题的id
    **sort**| |-1|(1,-1)|消息的获取顺序,默认是倒序-1
    **identify**| | |1~80|APP包名

* 说明:

    该客服当前需要解决的问题,包括客服主动开始的问题与用户重开(客服结束解答后再次开始)的问题;

* 返回json数据:

```
{
    'status': 200,
    'questions': [
        {
            'question_id': < str >, //问题id
            'user_id': < str >, //提问用户
            'user_image_url': < str >, //用户头像url
            'user_name': < str >, //用户昵称
            'title': < str >, //问题标题
            'last_mess_text': < str >, //该问题最后一次聊天消息内容
            'last_mess_timestamp': < float >, //该问题最后一次聊天消息时间戳
            'last_mess_sender': < int >, //该问题最后一次聊天消息发送者
            'last_mess_sender_type': < int >, //该问题最后一次聊天消息发送者类型（1:用户、2:客服）
            'timestamp': < float >, //问题创建时间戳
        }
    ]
}
```

#### 用户'待解决'问题列表
* URL: **/user/< user_id >/waits**

* 发送GET参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **question_id**| | |24|前一页最后一条问题的id
    **sort**| |-1|(1,-1)|消息的获取顺序,默认是倒序-1
    **identify**| | |1~80|APP包名

* 说明:

    该用户所有还没有客服开始回答的问题;

* 返回json数据:

```
{
    'status': 200,
    'questions': [
        {
            'question_id': < str >, //问题id
            'timestamp': < float >, //问题创建时间戳
        }
    ]
}
```

#### 用户'解决中'问题列表
* URL: **/user/< user_id >/tasks**

* 发送GET参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **question_id**| | |24|前一页最后一条问题的id
    **sort**| |-1|(1,-1)|消息的获取顺序,默认是倒序-1
    **identify**| | |1~80|APP包名

* 说明:

    该用户所有客服正在回答的问题;

* 返回json数据:

```
{
    'status': 200,
    'questions': [
        {
            'question_id': < str >, //问题id
            'timestamp': < float >, //问题创建时间戳
            'serv_id': < str >, //该问题客服id
        }
    ]
}
```

#### 用户'已解决'问题列表
* URL: **/user/< user_id >/overs**

* 发送GET参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **question_id**| | |24|前一页最后一条问题的id
    **sort**| |-1|(1,-1)|消息的获取顺序,默认是倒序-1
    **identify**| | |1~80|APP包名

* 说明:

    该用户所有客服已经结束回答的问题;

* 返回json数据:

```
{
    'status': 200,
    'questions': [
        {
            'question_id': < str >, //问题id
            'timestamp': < float >, //问题创建时间戳
            'serv_id': < str >, //该问题客服id
        }
    ]
}
```

#### 用户所有问题列表
* URL: **/user/< user_id >/alls**

* 发送GET参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **question_id**| | |24|前一页最后一条问题的id
    **sort**| |-1|(1,-1)|消息的获取顺序,默认是倒序-1
    **identify**| | |1~80|APP包名

* 返回json数据:

```
{
    'status': 200,
    'questions': [
        {
            'question_id': < str >, //问题id
            'status': < int >, //问题状态(1:待解决,2:解决中,3:已解决)
            'timestamp': < float >, //问题创建时间戳
            'serv_id': < str >, //该问题客服id
        }
    ]
}
```

#### 获取问题聊天消息
* URL: **/question/< question_id >/message**

* 发送GET参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **message_id**| | |24|前一页最后一条消息的id
    **sort**| |-1|(1,-1)|消息的获取顺序,默认是倒序-1
    **identify**| | |1~80|APP包名

* 返回json数据:

```
{
    'status': 200,
    'messages': [
        { //语音消息
            'message_id': < str >, //消息id
            'sender': < str >, //发送者id
            'sender_type': < int >, //发送者类型（1:用户、2:客服）
            'timestamp': < float >, //消息时间戳
            'type': 1
            'audio_url': < str >, //语音url
            'audio_len': < int >, //语音长度
        },
        { //图片消息
            'message_id': < str >, //消息id
            'sender': < str >, //发送者id
            'sender_type': < int >, //发送者类型（1:用户、2:客服）
            'timestamp': < float >, //消息时间戳
            'type': 2
            'image_url': < str >, //图片url
        },
        { //文本消息
            'message_id': < str >, //消息id
            'sender': < str >, //发送者id
            'sender_type': < int >, //发送者类型（1:用户、2:客服）
            'timestamp': < float >, //消息时间戳
            'type': 3
            'text': < str >, //文本内容
        },
        { //通知消息
            'message_id': < str >, //消息id
            'sender': < str >, //发送者id
            'sender_type': < int >, //发送者类型（1:用户、2:客服）
            'timestamp': < float > //消息时间戳
            'type': 4,
            'action': < int >,
            /* 动作类型（1:客服开始处理、2:客服退出处理、3:客服请求结束处理、4:本问题已完成处理、5:本问题已超时、6:用户重开问题）*/
        }
    ]
}
```

#### 发送问题聊天文字消息
* URL: **/question/< question_id >/message/send_text**

* 发送POST参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **sender**|Y| | |用户id或与客服id
    **sender_type**|Y| |(1,2)|发送者类型（1:用户、2:客服）
    **text**|Y| | |utf8字符串

* 说明:

    若该问题:已被其他客服接受,还未开始,已经结束等情况会返回对应错误码;

* 返回json数据:

```
{
    'status': 200,
    'message_id': < str >, //消息id
}
```

#### 发送问题聊天图片消息
* URL: **/question/< question_id >/message/send_image**

* 发送POST参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **sender**|Y| | |用户id或与客服id
    **sender_type**|Y| |(1,2)|发送者类型（1:用户、2:客服）
    **image**|Y| | |jpg格式图片base64字符串

* 说明:

    若该问题:已被其他客服接受,还未开始,已经结束等情况会返回对应错误码;

* 返回json数据:

```
{
    'status': 200,
    'message_id': < str >, //消息id
    'image_url': < str > //url链接
}
```

#### 快速回答模板列表
* URL: **/answer/templates**

* 发送GET参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **identify**| | |1~80|APP包名

* 返回json数据:

```
{
    'status': 200,
    'templates': [
        {
            'template_id': < str >, //模板id
            'title': < str >, //模板标题
        }
    ]
}
```

#### 快速回答列表
* URL: **/answer/template/< template_id >**

* 发送GET参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **item_id**| | |24|前一页最后一条问题的id
    **sort**| |-1|(1,-1)|消息的获取顺序,默认是倒序-1
    **identify**| | |1~80|APP包名

* 返回json数据:

```
{
    'status': 200,
    'items': [
        {
            'item_id': < str >, //快速回答id
            'question': < str >, //提问
            'content': < str >, //应答
        }
    ]
}
```

#### 退出回答用户问题
* URL: **/question/< question_id >/quit**

* 发送POST参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **serv_id**|Y| |1~20|客服账号

* 返回json数据:

```
{
    'status': 200,
    'message_id': < str > //新通知消息id
}
```

#### 完成用户问题
* URL: **/question/< question_id >/finish**

* 发送POST参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **serv_id**|Y| |1~20|客服账号

* 返回json数据:

```
{
    'status': 200,
    'message_id': < str > //新通知消息id
}
```

#### 客服注销(解绑APP)
* URL: **/serv/unbind**

* 发送POST参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **serv_id**|Y| |1~20|客服账号
    **password**|Y| |1~20|客服密码

* 返回json数据:

```
{
    'status': 200
}
```

#### 客服获取用户信息
* URL: **/user **

* 发送GET参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **question_id**|Y| |1-20|问题ID

* 返回html页面:
```
{
    用户名
    用户设备数
    用户组数
}
```

#### 客户重开问题
* URL: **/question/< question_id >/reopen**

* 发送POST参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session

* 返回json数据:

```
{
    'status': 200,
    'message_id': < str > //新通知消息id
}
```