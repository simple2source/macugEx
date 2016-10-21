# 汕头大学校友会文档

1.服务器返回的数据一般为 'application/json' 方式;
2.返回的数据中的 code 为状态码,成功时为0;

## 校友

### 校友信息

url: /resource/user/[userid]

method: GET

return:
    
```
{
    'code'       : 请求状态,
    'name'       : 校友姓名,
    'grade'      : 校友年级,
    'specialty'  : 校友专业,
    'phone'      : 手机号,
    'career'     : 行业,
    'profession' : 职业,
    'image_url'  : 头像url
}
```

### 修改校友信息

url: /resource/user/[userid]

method: POST

params:

    'name'       : 校友姓名[可选]
    'grade'      : 校友年级[可选]
    'specialty'  : 校友专业[可选]
    'phone'      : 手机号[可选]
    'career'     : 行业[可选],
    'profession' : 职业[可选],
    'image_file' : 头像[可选](form-data文件参数),
    'lon'        : 经度[可选](火星坐标),
    'lat'        : 纬度[可选](火星坐标)

return:
    
```
{
    'code': 请求状态
}
```

## 校企

### 附近校企信息

url: /resource/company/near

method: GET

params:

    'lon' : 经度[必选]
    'lat' : 纬度[必选]

return:

```
{
    'code'     : 请求状态,
    'companys' : [
        {
            'companyid' : 校企id,
            'image_url' : 附近校企展示图片,
            'area'      : 校企所在区域,
            'name'      : 校企名称,
            'type'      : 校企类型,
            'address'   : 校企地址
        }
    ]
}
```

### 校企详情

url: /resource/company/[companyid]

method: GET

return:

```
{
    'code'      : 请求状态,
    'name'      : 校企名称,
    'type'      : 校企类型,
    'area'      : 校企所在区域,
    'address'   : 详细地址,
    'title'     : 校企描述标题,
    'content'   : 校企描述内容
}
```

## 头大同行

### 同行列表

url: /resource/career/[career name]/peers

method: GET

params:

    'page' : 页数[可选][默认:0]
    'num'  : 数目[可选][默认:10]

return:

```
{
    'code'  : 请求状态,
    'peers' : [
        {
            'userid'     : 校友id,
            'name'       : 校友姓名,
            'grade'      : 校友年级,
            'specialty'  : 校友专业,
            'profession' : 职业
        }
    ]
}
```

## 附近校友

### 附近校友信息

url: /resource/alumnus/near

method: GET

params:

    'lon' : 经度[必选]
    'lat' : 纬度[必选]

return:

```
{
    'code'    : 请求状态,
    'alumnus' : [
        {
            'userid'         : 校友id,
            'image_url'      : 附近校友头像,
            'name'           : 校友姓名,
            'grade'          : 校友年级,
            'specialty'      : 校友专业,
            'distance'       : 校友距离,
            'last_timestamp' : 最近一次时间戳
        }
    ]
}
```

## 活动列表

### 最新活动列表(todo)

url: /resource/events/newest

method: GET

params:

    'page' : 页数[可选]
    'num'  : 数目[可选]

return:

```
{
    'code'   : 请求状态,
    'events' : [
        {
            'eventid'   : 活动id,
            'brief'     : 活动简介,
            'lon'       : 经度,
            'lat'       : 纬度,
            'address'   : 活动地址,
            'timestamp' : 活动时间戳
        }
    ]
}
```

### 各类型活动(todo)

url: /resource/events/[event type]

method: GET

params:

    'page' : 页数[可选]
    'num'  : 数目[可选]

return:

```
{
    'code'  : 请求状态,
    'events': [
        {
            'eventid'   : 活动id,
            'brief'     : 活动简介,
            'lon'       : 经度,
            'lat'       : 纬度,
            'address'   : 活动地址,
            'timestamp' : 活动时间戳
        }
    ]
}
```

## 活动

### 活动详情(todo)

url: /resource/event/[eventid]

method: GET

return:

```
{
    'code'      : 请求状态,
    'eventid'   : 活动id,
    'brief'     : 活动简介,
    'lon'       : 经度,
    'lat'       : 纬度,
    'address'   : 活动地址,
    'timestamp' : 活动时间戳,
    'joins'     : [
        {
            'userid'    : 校友id,
            'name'      : 校友名字,
            'image_url' : 头像url,
        }
    ]
}
```

### 发布活动(todo)

url: /resource/events

method: POST

params:

    'brief'      : 活动简介[必选]
    'type'       : 活动类型[必选]
    'lon'        : 经度[必选]
    'lat'        : 纬度[必选]
    'address'    : 活动地址[必选]
    'timestamp'  : 活动时间戳[必选]
    'join_limit' : 活动人数限制[必选]

return:

```
{
    'code'    : 请求状态,
    'eventid' : 活动id,
}
```

### 我的已发布活动(todo)

url: /resource/user/[userid]/events/published

method: GET

return:
    
```
{
    'code'   : 请求状态,
    'events' : [
        {
            'eventid'   : 活动id,
            'brief'     : 活动简介,
            'lon'       : 经度,
            'lat'       : 纬度,
            'address'   : 活动地址,
            'timestamp' : 活动时间戳,
            'joins': [
                {
                    'userid'    : 校友id,
                    'name'      : 校友名字,
                    'image_url' : 头像url,
                }
            ]
        }
    ]
}
```

### 我的已加入活动(todo)

url: /resource/user/[userid]/events/joined

method: GET

return:
    
```
{
    'code'   : 请求状态,
    'events' : [
        {
            'eventid'   : 活动id,
            'brief'     : 活动简介,
            'lon'       : 经度,
            'lat'       : 纬度,
            'address'   : 活动地址,
            'timestamp' : 活动时间戳,
            'joins': [
                {
                    'userid'    : 校友id,
                    'name'      : 校友名字,
                    'image_url' : 头像url,
                }
            ]
        }
    ]
}
```

## 圈子

### 圈子信息(todo)

url: /resource/groups

method: GET

params:

    'page' : 页数[可选]
    'num'  : 数目[可选]

return:

```
{
    'code'   : 请求状态,,
    'groups' : [
        {
            'groupid'   : 圈子id,
            'name'      : 圈子名字,
            'image_url' : 圈子头像url
        }
    ]
}
```

### 最新圈子话题(todo)

url: /resource/groups/topics/newest

method: GET

params:

    'page' : 页数[可选]
    'num'  : 数目[可选]

return:

```
{
    'code'   : 请求状态,,
    'topics' : [
        {
            'topicid'   : 话题id,
            'title'     : 话题标题,
            'timestamp' : 话题时间戳
        }
    ]
}
```

### 圈子话题列表(todo)

url: /resource/group/[groupid]/topics

method: GET

params:

    'page' : 页数[可选]
    'num'  : 数目[可选]

return:

```
{
    'code'   : 请求状态,
    'topics' : [
        {
            'topicid'   : 话题id,
            'title'     : 话题标题,
            'timestamp' : 话题时间戳
        }
    ]
}
```

## 话题

### 话题详情(todo)

url: /resource/topic/[topicid]

method: GET

params:

    'page' : 页数[可选]
    'num'  : 数目[可选]

return:

```
{
    'code'      : 请求状态,
    'title'     : 话题简介,
    'content'   : 话题内容,
    'userid'    : 话题发送者id,
    'timestamp' : 话题时间戳,
    'comments'  : [
        {
            'userid'    : 评论者id,
            'content'   : 评论内容,
            'like_num'  : 点赞数,
            'timestamp' : 评论时间戳,
        }
    ]
}
```

## 校友会

### 校友会列表

url: /resource/association/overview

method: GET

return:

```
{
    'code'         : 请求状态,
    'associations' : {
        [分类id]: [
            {
                'associationid' : 校友会id,
                'name'          : 校友会名字
            }
        ]
    }
}
```

### 校友会详情

url: /resource/association/[associationid]

method: GET

return:

```
{
    'code'    : 请求状态,
    'name'    : 校友会名字,
    'content' : 校友会介绍,
    'type'    : 校友会分类
}
```

## 资讯

### 资讯列表

url: /resource/news

method: GET

params:

    'page' : 页数[可选]
    'num'  : 数目[可选]

return:

```
{
    'code' : 请求状态,
    'news' : [
        {
            'newsid'    : 资讯id,
            'title'     : 资讯标题,
            'brief'     : 资讯简介,
            'timestamp' : 资讯时间戳
        }
    ]
}
```

### 资讯详情

url: /resource/news/[newid]

method: GET

return:

```
{
    'code'      : 请求状态,
    'source'    : 咨询来源,
    'title'     : 资讯标题,
    'content'   : 资讯内容,
    'timestamp' : 资讯时间戳
}
```

## 诚哥语录

### 语录列表

url: /resource/quotes

method: GET

params:

    'page' : 页数[可选]
    'num'  : 数目[可选]

return:

```
{
    'code'   : 请求状态,
    'quotes' : [
        {
            'quoteid'   : 语录id,
            'brief'     : 语录简介,
            'author'    : 语录作者,
            'timestamp' : 语录时间戳,
            'image_url' : 语录图片
        }
    ]
}
```

### 语录详情

url: /resource/quote/[quoteid]

method: GET

return:

```
{
    'code'      : 请求状态,
    'content'   : 语录内容,
    'author'    : 语录作者,
    'timestamp' : 语录时间戳,
}
```

## 捐赠

### 校友捐赠份数

url: /resource/donate/acount

method: GET

return:

```
{
    'code'  : 请求状态,
    'count' : 捐赠总共份数
}
```

### 基金会列表

url: /resource/foundations

method: GET

return:

```
{
    'code'        :请求状态,
    'foundations' : [
        {
            'foundationid' : 基金会id,
            'name'         : 基金会名称,
            'brief'        : 基金会简介,
            'acount'       : 受捐赠次数总计,
            'image_url'    : 图片url
        }
    ]
}
```

### 基金会详情

url: /resource/foundation/[foundationid]

method: GET

return:

```
{
    'code'      : 请求状态,
    'name'      : 基金会名称,
    'content'   : 基金会详细描述,
    'acount'    : 受捐赠次数总计,
    'amount'    : 受捐赠金额总计,
    'image_url' : 图片url,
}
```

### 基金会受捐赠情况

url: /resource/foundation/[foundationid]/donates

method: GET

params:

    'page' : 页数[可选]
    'num'  : 数目[可选]

return:

```
{
    'code'      : 请求状态,
    'donates': [
        {
            'donateid'  : 捐赠id,
            'userid'    : 用户id,
            'image_url' : 用户头像url,
            'brief'     : 用户身份简写,
            'named'     : 用户填写名字,
            'wishe'     : 寄语,
            'amount'    : 金额,
            'timestamp' : 时间戳
        }
    ]
}
```

### 校友情怀榜

url: /resource/users/donateRanks

method: GET

params:

    'page' : 页数[可选]
    'num'  : 数目[可选]

return:

```
{
    'code'      : 请求状态,
    'users': [
        {
            'userid'    : 用户id,
            'image_url' : 用户头像url,
            'name'      : 校友姓名,
            'grade'     : 校友年级,
            'specialty' : 校友专业,
            'amount'    : 总计金额,
        }
    ]
}
```

### 我的捐赠记录

url: /resource/user/[userid]/donates

method: GET

params:

    'page' : 页数[可选]
    'num'  : 数目[可选]

return:

```
{
    'code'    : 请求状态,
    'donates' : {
        [基金会id] : {
            'name'      : 基金会名称,
            'amount'    : 已捐赠金额,
            'acount'    : 已捐赠次数,
            'image_url' : 基金会图片url
        }
    }
}
```

### 发起捐赠

url: /resource/donate/action

method: POST

params:

    'foundationid' : 基金会id[必选]
    'userid'       : 用户id[必选]
    'amount'       : 金额[必选]

return:

```
{
    'code'                 : 请求状态,
    'wechatParamSerialize' : 微信支付json序列化参数
}
```

### 确认捐赠

url: /resource/user/[userid]/donates

method: POST

params:

    'foundationid' : 基金会id[必选]
    'amount'       : 金额[必选]
    'prepayid'     : 微信预支付id[必选]
    'brief'        : 用户身份简写[可选]
    'named'        : 用户填写名字[可选]
    'wishe'        : 寄语[可选]

return:

```
{
    'code': 请求状态
}
```


# 接口错误码定义

code|说明
-----|-----
0|请求成功
1001|传参错误
1002|无效参数
