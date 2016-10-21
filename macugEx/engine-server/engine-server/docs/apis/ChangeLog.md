#### Changes in 1.23.6

1. [新用户创建圈子并添加腕表](../app/#_43) 接口增加`authcode`参数

#### Changes in 1.23.5

1. 增加 [10070](../app/error/) 错误码
2. 客服模块 - 客户向已关闭问题发消息自动重开该问题

#### Changes in 1.23.4

1. 增加 [客户提问问题](../app/service/#_2) 返回参数

#### Changes in 1.23.3

1. 增加 [客户重开问题](../app/service/#_18) 接口
2. 增加 [客服模块-错误码](../app/service/error/)

#### Changes in 1.23.2

1. 增加 [快速回答列表](../app/service/#_14) 'question' 参数

#### Changes in 1.23.1

1. 修改 [添加腕表](../app/#_6) 说明

#### Changes in 1.23.0

1. 增加 [客服获取用户信息](../app/service/#_17) 接口

#### Changes in 1.22.9

1. 增加 [客服注销(解绑APP)](../app/service/#app_1) 接口

#### Changes in 1.22.8

1. [客服获取'待解决'用户问题列表](../app/service/#_3) 接口增加返回参数
2. [客服'解决中'问题列表](../app/service/#_5) 接口增加返回参数

#### Changes in 1.22.7

1. [客户提问问题](../app/service/#_2) 接口增加 `title` 参数
2. [开始回答用户问题](../app/service/#_4) 接口删除 `user_id` 参数
3. 新增 [退出回答用户问题](../app/service/#_15) 接口
4. 新增 [完成用户问题](../app/service/#_16) 接口

#### Changes in 1.22.6

1. 增加 [快速回答模板列表](../app/service/#_13) 接口
2. 增加 [快速回答列表](../app/service/#_14) 接口

#### Changes in 1.22.5

1. [删除腕表](../app/#_31) 接口增加请求参数

#### Changes in 1.22.4

1. 增加 [用户所有问题列表](../app/service/#_7) 接口

#### Changes in 1.22.3

1. 增加 [客服模块-错误码](../app/service/error/)

#### Changes in 1.22.2

1. 修改接口访问 url 前缀

#### Changes in 1.22.1

1. 修改 [客户提问问题](../app/service/#_2) 接口
2. 修改 [获取问题聊天消息](../app/service/#_8) 接口返回数据`content`字段
3. 修改`content`字段相关推送

#### Changes in 1.22.0

1. 完善客服系统api接口文档

#### Changes in 1.21.9

1. 添加客服系统api接口文档

#### Changes in 1.21.8

1. 修改 [刷新用户session](../app/#session) 接口请求参数

#### Changes in 1.21.7

1. 增加 [新建用户](../app/#_46) 接口

#### Changes in 1.21.6

1. 增加 [刷新用户session](../app/#session) 接口

#### Changes in 1.21.5

1. 增加 [10067](../app/error/) 错误码

#### Changes in 1.21.4

1. 增加 [获取广场消息点赞记录](../app/other/#_10) 接口`sort`参数
2. 增加 [获取广场消息评论记录](../app/other/#_11) 接口`sort`参数

#### Changes in 1.21.3

1. [获取答题游戏题目](../app/other/#_18) 接口`session`参数选填
2. 修改 [查询腕表答题结果列表](../app/other/#_19) 接口
3. 修改 [查询腕表答题结果详情](../app/other/#_20) 接口
4. 修改 [获取最新版本信息](../app/apiv2/#_2) 接口参数

#### Changes in 1.21.2

1. 修改 [答题游戏分类列表](../app/other/#_17) 接口
3. 增加 [查询腕表答题结果详情](../app/other/#_20) 接口

#### Changes in 1.21.1

1. 增加 [答题游戏分类列表](../app/other/#_17) 接口
2. 增加 [获取答题游戏题目](../app/other/#_18) 接口
3. 修改 [发送答题游戏](../app/other/#_14) 接口

#### Changes in 1.21.0

1. 增加 [发送答题游戏](../app/other/#_14) 接口
2. 增加 [答题游戏排行](../app/other/#_15) 接口
3. 增加 [查询答题游戏排行](../app/other/#_16) 接口

#### Changes in 1.20.9

1. [添加圈子联系人](../app/#_14) 接口返回增加`contact_image_url`参数

#### Changes in 1.20.8

1. [故事详情](../app/other/#_4) 接口增加参数

#### Changes in 1.20.7

1. 增加 [10065](../app/error/) 错误码

#### Changes in 1.20.6

1. [新用户创建圈子](../app/#_2) 接口增加`identify`参数
2. [新建圈子](../app/#_3) 接口增加`identify`参数
3. [添加腕表](../app/#_6) 接口增加`identify`参数
4. [进入圈子](../app/#_9) 接口增加`identify`参数
5. [新用户进入圈子](../app/#_10) 接口增加`identify`参数
6. [添加圈子联系人](../app/#_14) 接口增加`identify`参数
7. [应用首页](../app/other/#_1) 接口请求增加`identify`参数
8. [获取广场消息](../app/other/#_6) 接口请求增加`identify`参数
9. [获取广场消息点赞记录](../app/other/#_10) 接口请求增加`identify`参数
10. [获取广场消息评论记录](../app/other/#_11) 接口请求增加`identify`参数
11. [APP预激活腕表](../app/#app_1) 接口增加`identify`参数
12. [APP预激活腕表](../app/#app_1) 接口增加`customer_id`参数
13. [APP激活腕表](../app/#app_2) 接口增加`identify`参数
14. [APP激活腕表](../app/#app_2) 接口增加`customer_id`参数
15. [新用户创建圈子并添加腕表](../app/#_43) 接口增加`identify`参数
16. [新用户创建圈子并添加腕表](../app/#_43) 接口增加`customer_id`参数
17. [创建圈子并添加腕表](../app/#_44) 接口增加`identify`参数
18. [创建圈子并添加腕表](../app/#_44) 接口增加`customer_id`参数

#### Changes in 1.20.5

1. [应用首页](../app/other/#_1) 接口删除`session`参数

#### Changes in 1.20.4

1. 增加迪士尼版本域名

#### Changes in 1.20.3

1. [圈子详情](../app/#_12) 接口增加`devs.group_id`参数
2. [查询腕表信息](../app/#_32) 接口增加`group_id`参数

#### Changes in 1.20.2

1. 修改 [用户圈子列表详情](../app/#_45) 接口

#### Changes in 1.20.1

1. 删除 [用户腕表列表](../app) 接口
2. 增加 [用户圈子列表详情](../app/#_45) 接口
3. [获取最新版本信息](../app/apiv2/#_2) 接口增加`vendor`参数

#### Changes in 1.20.0

1. [APP预激活腕表](../app/#app_1) 接口`session`,`group_id`参数选填
2. 增加 [创建圈子并添加腕表](../app/#_44) 接口
3. 增加 [用户腕表列表](../app) 接口
4. 除了 [上传人脸图像](../app/other/#_13) 外删除其他接口 `face_image` 请求参数

#### Changes in 1.19.9

1. [新用户创建圈子](../app/#_2) `group_email`参数选填
2. [新建圈子](../app/#_3) `group_email`参数选填
3. 增加 [新用户创建圈子并添加腕表](../app/#_43) 接口
4. 增加 [10064](../app/error/) 错误码

#### Changes in 1.19.8

1. [接收圈子消息](../app/#_17) 接口增加新参数`sort`

#### Changes in 1.19.7

1. 增加 [腕表上下线消息](../app/push/#_21) 推送,圈子消息类型
2. [接收圈子消息](../app/#_17) 接口增加消息类型

#### Changes in 1.19.6

1. 增加 [修改腕表信息](../app/#_33) 接口增加`gps_strategy`请求参数

#### Changes in 1.19.5

1. [圈子详情](../app/#_12) 接口返回增加`gps_strategy`参数
2. [查询腕表信息](../app/#_32) 接口返回增加`gps_strategy`参数

#### Changes in 1.19.4

1. 增加 [关机手表](../app/#_42) 接口

#### Changes in 1.19.3

1. ios APP推送使用 MQTT 时推送特定消息切换使用推送方式

#### Changes in 1.19.2

1. [腕表进入休眠模式](../app/push/#_20) 消息推送使用

#### Changes in 1.19.1

1. 增加 [腕表gps状态信息](../app/#gps) 接口

#### Changes in 1.19.0

1. [腕表进入休眠模式](../app/push/#_20) 消息推送不使用

#### Changes in 1.18.9

1. 增加 [删除广场消息](../app/other/#_12) 接口
2. 增加 [10063](../app/error/) 错误码

#### Changes in 1.18.8

1. 增加 [APP预激活腕表](../app/#app_1) 接口修改请求参数
2. 增加 [10062](../app/error/) 错误码

#### Changes in 1.18.7

1. [添加腕表](../app/#_6) 接口增加`user_phone`参数
2. [APP激活腕表](../app/#app_2) 接口增加`user_phone`参数
3. 增加 [10056~10061](../app/error/) 错误码
4. [10029](../app/error/) 错误码不使用
4. [10033](../app/error/) 错误码不使用

#### Changes in 1.18.6

1. 接口 v1,v2 返回增加 field,errorKey 字段

#### Changes in 1.18.5

1. 增加 [APP预激活腕表](../app/#app_1) 接口
1. 增加 [APP激活腕表](../app/#app_2) 接口

#### Changes in 1.18.4

1. 增加`腕表进入休眠模式`消息推送,圈子消息类型

#### Changes in 1.18.3

1. [成员进入家庭圈](../app/push/#_17) 推送增加参数
2. [腕表进入家庭圈](../app/push/#_19) 推送增加参数

#### Changes in 1.18.2

1. [请求腕表定位](../app/#_20) 接口`num`,`inteval`参数被忽略

#### Changes in 1.18.1

1. [添加圈子联系人](../app/#_14) 接口返回增加`contact_name`参数

#### Changes in 1.18.0

1. [新用户创建圈子](../app/#_2) 接口`group_email`参数必填
2. [新建圈子](../app/#_3) 接口`group_email`参数必填

#### Changes in 1.17.9

1. [故事下载完毕反馈](../app/push/#_10) 修改推送格式
2. [腕表低电量](../app/push/#_11) 修改推送格式
3. [腕表新短信](../app/push/#_12) 修改推送格式
4. [腕表存储卡容量不足](../app/push/#_13) 修改推送格式
5. [腕表存储卡读取异常](../app/push/#_14) 修改推送格式
6. [腕表脱落告警](../app/push/#_15) 修改推送格式

#### Changes in 1.17.8

1. 增加 [10053](../app/error/) 错误码
1. 增加 [10054](../app/error/) 错误码

#### Changes in 1.17.7

1. [新用户创建圈子](../app/#_2) 接口增加`face_image`参数
2. 增加 [上传人脸图像](../app/other/#_13) 接口
3. 增加 [人脸图像获取session](../app/other/#session) 接口
4. 增加 [10051](../app/error/) 错误码
5. 增加 [10052](../app/error/) 错误码

#### Changes in 1.17.6

1. 圈子邮箱唯一错误码不使用 [10020](../app/error/)

#### Changes in 1.17.5

1. 增加`腕表脱落告警`消息推送,圈子消息类型

#### Changes in 1.17.4

1. 新增 [热门故事列表](../app/other/#_3) 接口

#### Changes in 1.17.3

1. 圈子邮箱唯一错误码启用 [10020](../app/error/)

#### Changes in 1.17.2

1. [圈子详情](../app/#_12) 接口返回增加`contact_image_url`参数

#### Changes in 1.17.1

1. [添加圈子联系人](../app/#_14) 接口请求`contact_name`参数选填

#### Changes in 1.17.0

1. [新用户创建圈子](../app/#_2) 接口请求`password`参数选填
2. [新建圈子](../app/#_3) 接口请求`password`参数选填

#### Changes in 1.16.9

1. 增加 [开启腕表脱落告警](../app/#_40) 接口
2. 增加 [关闭腕表脱落告警](../app/#_41) 接口
3. [圈子详情](../app/#_12) 接口返回增加`fall_status`参数
4. [查询腕表信息](../app/#_32) 接口返回增加`fall_status`参数

#### Changes in 1.16.8

1. [获取广场消息](../app/other/#_6) 接口请求删除`session`参数

#### Changes in 1.16.7

1. [监听腕表](../app/#_24) 接口增加返回参数`monitor_user_id`

#### Changes in 1.16.6

1. 增加`广场`相关错误码 [10050](../app/error/)
2. [应用首页](../app/other/#_1) 接口增加`category_num`参数

#### Changes in 1.16.5

1. [评论广场消息](../app/other/#_9) 接口返回值增加参数

#### Changes in 1.16.4

1. [评论广场消息](../app/other/#_9) 接口返回值增加`comment_id`参数

#### Changes in 1.16.3

1. 修改 `广场` 相关接口

#### Changes in 1.16.2

1. [成员离开家庭圈](../app/push/#_18) 增加 `operator`(操作者user_id)参数
2. [腕表进入家庭圈](../app/push/#_19) 增加 `operator`(操作者user_id)参数
3. [腕表离开家庭圈](../app/push/#_20) 增加 `operator`(操作者user_id)参数

#### Changes in 1.16.1

1. 修改 [版本获取](../app/apiv2/#_2) 接口实现为 apiv2 方式

#### Changes in 1.16.0

1. 增加`广场`相关错误码 [10049](../app/error/)

#### Changes in 1.15.9

1. 增加`广场`功能相关接口

#### Changes in 1.15.8

1. 增加`腕表存储卡容量不足`消息推送,圈子消息类型
2. 增加`腕表存储卡读取异常`消息推送,圈子消息类型

#### Changes in 1.15.7

1. 新增 [获取最新版本信息](../app/apiv2/#_2) 接口

#### Changes in 1.15.6

1. [查询腕表每天轨迹条数](../app/#_35) 接口修改返回类型

#### Changes in 1.15.5

1. [查询腕表轨迹信息](../app/#_34) 接口增加 `type` 参数

#### Changes in 1.15.4

1. `watch_locate` 推送类型删除 `message_id`,`group_id` 参数
2. [接收圈子消息](../app/#_17) 接口弃用 `腕表轨迹点消息` 类型
2. 增加 [查询腕表每天轨迹条数](../app/#_35) 接口

#### Changes in 1.15.3

1. `请求腕表定位` 增加 type 参数

#### Changes in 1.15.2

1. 增加`腕表短信`消息推送,圈子消息类型

#### Changes in 1.15.1

1. `用户`,`腕表`,`联系人`信息修改更新圈子时间戳
2. 文档发布到 <https://web.ios16.com/docs/app>
3. 根据轨迹点推送中的`message_id`字段,没有时为静默推送
4. 修改推送地址,频道

#### Changes in 1.15.0

1. 除了`圈子轨迹点`消息，删除服务器所有返回中的 address 参数
2. 删除`信标`相关接口
