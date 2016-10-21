# SUAA 项目数据定义文档

## user: 用户

* _id [ObjectId] [unique index] : 用户id
* name [str]                    : 名字
* grade [str]                   : 年级
* specialty [str]               : 专业
* phone [str]                   : 手机号
* career [str] [index]          : 行业
* profession [str]              : 职业
* img [str]                     : 头像文件名
* UserId [str]                  : 微信企业账号id
* OpenId [str]                  : 微信账号OpenId
* loc [float, float] [2dsphere] : [经度, 纬度]
* lasttime [datetime]           : 最后定位时间
* donateNum [int] [index]       : 捐赠金额总计

## company: 校企

* _id [ObjectId] [unique index] : 校企id
* name [str]                    : 名称
* province [str]                : 省
* city [str]                    : 市
* citycode [str]                : 城市编号
* district [str]                : 县/区
* adcode [str]                  : 区域编码
* loc [float, float] [2dsphere] : [经度, 纬度]
* address [str]                 : 地址
* img [str]                     : 图片文件名
* type [str]                    : 校企类型
* title [str]                   : 校企描述标题
* content [str]                 : 校企描述内容

## association: 校友会

* _id [ObjectId] [unique index] : 校友会id
* name                          : 校友会名字
* type [str]                    : 校友会分类
* content [str]                 : 校友会详细介绍

## news: 资讯

* _id [ObjectId] [unique index] : 资讯id
* title [str]                   : 资讯标题
* content [str]                 : 资讯内容
* maketime [datetime]           : 创建时间

## quote: 语录

* _id [ObjectId] [unique index] : 资讯id
* content [str]                 : 语录内容
* author [str]                  : 语录作者
* img [str]                     : 图片文件名
* maketime [datetime]           : 创建时间

## foundation: 受捐赠基金会

* _id [ObjectId] [unique index] : 基金会id
* name [str]                    : 名称
* brief [str]                   : 简介
* img [str]                     : 图片文件名
* content [str]                 : 详细介绍
* amount [int]                  : 受捐金额总计
* acount [int]                  : 受捐次数总计
* maketime [datetime]           : 成立时间

## donate: 所有捐赠

* _id [ObjectId] [unique index] : 捐赠id
* found_id [objectId] [index]   : 基金会id
* num [int]                     : 金额
* user_id [ObjectId] [index]    : 用户id
* brief [str]                   : 用户身份简写
* named [str]                   : 用户填写名字
* wishe [str]                   : 寄语
* timestamp [float]             : 时间戳

## donateFlight: 待确认捐赠

* _id [ObjectId] [unique index] : 待支付订单id
* found_id [objectId]           : 基金会id
* num [int]                     : 金额
* user_id [ObjectId]            : 用户id
* brief [str]                   : 用户身份简写
* named [str]                   : 用户填写名字
* wishe [str]                   : 寄语
* timestamp [float]             : 时间戳




