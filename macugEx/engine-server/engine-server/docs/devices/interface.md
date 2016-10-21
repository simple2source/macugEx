#### 获取身份信息
* url: **/watch/info**

* method: GET

* 请求参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |长度5|session
    **imei**|Y| |长度15|imei

* 返回数据示例:

```
{
    'name':  '\u738b\u5927\u54aa', //腕表名字
    'phone': '13524287904', //腕表手机号
}
```

* 返回数据说明:

    * name：腕表名字
    * phone：腕表手机号

#### 获取联系人列表
* url: **/watch/contactbook**

* method: GET

* 请求参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |长度5|session
    **imei**|Y| |长度15|imei
    **timestamp**| |0|浮点数|腕表最后一次请求该接口获得的圈子更新时间戳

* 返回数据示例:

```
{
    'timestamp': 1447150237.17163,
    'contacts': [
        {
            'id': '562dadd50bdb823a52190914',
            'name': '\u8001\u66fe',
            'phone': '13352379090',
            'portrait': 'http://server.com:8080/static/portrait/56452.jpg',
            'mac': 'c4544458cb7a',
            'status': 1
        },
        {
            'id': '13352379090',
            'name': '\u5c0f\u66fe',
            'phone': '13352379090',
            'portrait': 'http://server.com:8080/static/portrait/86352.jpg',
            'mac': '',
            'status': 0
        }
    ]
}
```

* 返回数据说明:

    * timestamp：圈子更新时间戳，圈子最后一次有数据更新的时间；
    * id：如果有24位长度，则为家庭圈`APP用户`id，否则为家庭圈`联系人`的手机号；(为了使每个结构都有唯一id)
    * name：昵称；
    * phone：手机号，`APP用户`手机号默认为空字符串；
    * portrait：头像url，`APP用户`，`联系人`都有默认头像地址；
    * mac：`APP用户`手机mac地址，由腕表上传，`联系人`该值为空字符串；
    * status：该数据在家庭圈中的状态；(1：在家庭圈内，0：已被删除)

#### 发送语音消息
* url: **/watch/sendaudio**

* method: POST

* 请求参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |长度5|session
    **imei**|Y| |长度15|imei
    **audio**|Y| |语音文件数据|imei
    **length**|Y| |大于0|imei

* 返回数据示例:

```
result
```

* 返回数据说明:

    * result：上传文件状态；('succed'：成功，'failed'：失败)

#### 获取激活二维码
* url: **/watch/activeme**

* method: GET

* 请求参数:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |长度5|session
    **imei**|Y| |长度15|imei
    **customer_id**|Y| |数字|客户号id

* 返回数据:

    jpeg格式图片(激活用二维码,APP扫码后激活腕表)


