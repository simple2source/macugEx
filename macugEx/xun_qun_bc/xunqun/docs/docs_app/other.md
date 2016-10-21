#### 应用主页
* URL: **/appstore_index**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **identify**| | |1~80|APP包名(显示不同主页)

* 返回data:

```
{
    'banner': [ //幻灯图片播放列表
        {
            'banner_image_url': < str >, //幻灯图片url
            'banner_type': < str >, //“story”或 “advert”（story跳转到story_id指定的故事，advert跳转到url指定的链接）
            'story_id': < str >, //故事id
            'url': < str > //外部链接
        },
    ],
    'category': [ //应用分类
        {
            'category_name': < str >, //分类名字
            'category_image_url': < str >, //分类图片url
            'category_id': < str >, //分类id
            'category_num': < int >, //该栏目是否开通（0:未开通，1:已开通）
        },
    ],
    'hot': [ //热门故事
        {
            'story_image_url': < str >, //故事图片url
            'story_id': < str >, //故事id
            'story_category_id': < str >, //故事分类id
            'story_name': < str >, //故事名字
            'story_brief': < str >, //故事简介
            'story_audio_url': < str >, //故事语音url
        },
    ],
}
```

* 应用分类id:

    * story: 故事模块
    * answer_game: 答题游戏模块
    * cartoon: 卡通模块（未开通）
    * rhyme: 儿歌模块（未开通）
    * sinology: 国学模块（未开通）
    * english: 英语模块（未开通）

#### 故事列表
* URL: **/story_list**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**| | |12|用户session
    **category_id**| | |0<x<20|故事分类id
    **page**| |0|0~50|页数
    **num**| |10|1~50|每页数目
    **story_id**| | |24|前一页最后一个故事的id

* 返回data:

```
[ //故事列表
    'story_id': < str >, //故事id
    'story_name': < str >, //故事名字
    'story_category_id': < str >, //故事分类id
    'story_image_url': < str >, //故事图片链接
    'story_brief': < str >, //故事简介
    'story_audio_url': < str >, //故事语音url
]
```

#### 热门故事列表
* URL: **/story_hot_list**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**| | |12|用户session
    **category_id**|Y| |0<x<20|故事分类id
    **page**| |0|0~50|页数
    **num**| |10|1~50|每页数目

* 返回data:

```
[ //故事列表
    'story_id': < str >, //故事id
    'story_name': < str >, //故事名字
    'story_category_id': < str >, //故事分类id
    'story_image_url': < str >, //故事图片链接
    'story_brief': < str >, //故事简介
    'story_audio_url': < str >, //故事语音url
]
```

#### 故事详情
* URL: **/story_detail**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**| | |12|用户session
    **story_id**|Y| |24|前一页最后一个故事的id

* 返回data:

```
{
    'story_id': < str >, //故事id
    'story_name': < str >, //故事名字
    'story_category_id': < str >, //故事分类id
    'story_image_url': < str >, //故事图片链接
    'story_brief': < str >, //故事简介
    'story_audio_url': < str >, //故事语音url
    'story_slice_text': [ < str > ], //故事字幕文字列表
    'story_slice_images_url': [ < str > ], //故事字幕图片url列表
    'story_slice_time': [ < str > ], //故事字幕时间点列表
    'story_slice_images_num': [ < int > ], //故事字幕图片索引
}
```

#### 发送故事
* URL: **/story_send**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei
    **story_id**|Y| |24|前一页最后一个故事的id

* 返回data:

```
{}
```

#### 获取广场消息
* URL: **/plaza**

* 如果服务器没有最新版本信息,返回空数据,请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **post_id**| | |24|前一页最后一条消息的id
    **identify**| | |1~80|APP包名

* 返回data:

```
[ //广场消息列表
    {
        'post_id': < str >, //消息id
        'user_id': < str >, //发出广播的用户
        'user_image': < str >, //发送者头像
        'user_name': < str >, //发送者圈子昵称
        'group_id': < int >, //发送者圈子id
        'group_name': < int >, //发送者圈子名称
        'user_image_url': < str >, //发送者头像url
        'lon': < float >, //发送者经度
        'lat': < float >, //发送者纬度
        'address': < str >, //发送者地址
        'likes': [ //点赞用户列表
            {
                'user_id': < str >, //点赞用户id
                'user_name': < str >, //点赞用户名
                'user_image_url': < str >, //点赞用户头像url
                'group_id': < int >, //点赞用户圈子id
                'group_name': < int >, //点赞用户圈子名称
                'timestamp': < float >, //点赞时间戳
            }
        ],
        'like_num': < int >, //点赞个数
        'liking': < int >, //1:已经点赞,2:还未点赞
        'content': < str >, //消息内容
        'images': [ //消息图片列表
            < str >, //图像url
        ],
        'comments': [ //评论列表
            {
                'comment_id': < str >, //评论id
                'user_id': < str >, //评论用户id
                'user_name': < str >, //评论用户名
                'user_image_url': < str >, //评论用户头像url
                'group_id': < int >, //评论用户圈子id
                'group_name': < int >, //评论用户圈子名称
                'content': < str >, //评论内容
                'timestamp': < float >, //评论时间戳
            }
        ],
        'comment_num': < int >, //评论个数
        'timestamp': < float >, //消息发送时间戳
    }
]
```

#### 发送广场消息
* URL: **/plaza_post**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **content**|Y(1)| |1~500|消息文本内容
    **images**|Y(1)| |字符串数组|（JPEG格式，base64编码）
    **lon**| | |火星坐标系|发送者经度
    **lat**| | |火星坐标系|发送者纬度
    **address**| | |1~200|发送者地址

* 返回data:

```
{
    'post_id': < str >, //消息id
}
```

#### 点赞广场消息
* URL: **/plaza_like**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **post_id**|Y| |24|消息id
    **liking**|Y| |(1,2)|1:点赞,2:取消点赞

* 返回data:

```
{
}
```

#### 评论广场消息
* URL: **/plaza_comment**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **post_id**|Y| |24|消息id
    **content**|Y| |1~500|评论文本内容

* 返回data:

```
{
    'comment_id': < str >, //评论id
    'user_name': < str >, //用户名
    'user_image_url': < str >, //用户头像url
    'group_id': < int >, //用户圈子id
    'group_name': < int >, //用户圈子名称
}
```

#### 获取广场消息点赞记录
* URL: **/plaza_like_record**

* 已经点赞的用户再次点赞会取消点赞,请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **post_id**|Y| |24|消息id
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **timestamp**| | |24|前一页最后一条点赞的时间戳
    **identify**| | |1~80|APP包名
    **sort**| |-1|(1,-1)|消息的获取顺序,默认是倒序-1

* 返回data:

```
[ //广场消息点赞列表
    {
        'user_id': < str >, //点赞用户id
        'user_name': < str >, //点赞用户名
        'user_image_url': < str >, //点赞用户头像url
        'group_id': < int >, //点赞用户圈子id
        'group_name': < int >, //点赞用户圈子名称
        'timestamp': < float >, //点赞时间戳
    }
]
```

#### 获取广场消息评论记录
* URL: **/plaza_comment_record**

* 已经点赞的用户再次点赞会取消点赞,请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **post_id**|Y| |24|消息id
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **comment_id**| | |24|前一页最后一条评论的id
    **identify**| | |1~80|APP包名
    **sort**| |-1|(1,-1)|消息的获取顺序,默认是倒序-1

* 返回data:

```
[ //广场消息评论列表
    {
        'comment_id': < str >, //评论id
        'user_id': < str >, //评论用户id
        'user_name': < str >, //评论用户名
        'user_image_url': < str >, //评论用户头像url
        'group_id': < int >, //评论用户圈子id
        'group_name': < int >, //评论用户圈子名称
        'content': < str >, //评论内容
        'timestamp': < float >, //评论时间戳
    }
]
```

#### 删除广场消息(没用到)
* URL: **/plaza_delete**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **post_id**|Y| |24|消息id

* 返回data:

```
{}
```

#### 上传人脸图像
* URL: **/face_set_session**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **face_image**|Y| | |人脸图像（JPEG格式，base64编码）

* 返回data:

```
{}
```

#### 人脸图像获取session
* URL: **/face_get_session**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **face_id**|Y| |32|图像face_id

* 返回data:

```
{
    'session': < str >, //用户session
}
```

#### 发送答题游戏
* URL: **/answer_game_send**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei
    **game_id_list**|Y| | |题目id列表:['55f43cb60bdb82a0fd9ff49c']

* 返回data:

```
{}
```

#### 答题游戏排行榜
* URL: **/answer_game_rank**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **page**| |0|0~50|页数
    **num**| |10|1~50|每页数目
    **identify**| | |1~80|APP包名

* 返回data:

```
{
    'rank': [
        {
            'imei': < str >, //腕表imei
            'name': < str >, //腕表名称
            'image_url': < str >, //腕表头像url
            'rank': < int >, //排名
            'score': < int > //分数
        },
    ]
}
```

#### 查询答题游戏排行
* URL: **/answer_game_search**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei_list**|Y| | |腕表imei列表:['355372020827303']

* 返回data:

```
{
    'imei_list': {
        'imei': < str >, //imei列表中的imei:'355372020827303'
        'rank': < int >, //排名
        'score': < int > //分数
    }
}
```

#### 答题游戏分类列表
* URL: **/answer_game_category**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**| | |12|用户session
    **identify**| | |1~80|APP包名

* 返回data:

```
{
    'game_category': [
        {
            'category_id': < str >, //分类id:'math'
            'category_name': < str >, //分类名称:'数学'
            'category_image_url': < str >, //分类图标url
        }
    ]
}
```

#### 获取答题游戏题目
* URL: **/answer_game_question**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **category_id**|Y| |字符串|答题题组分类id
    **num**| |10|1~50|题组题目数量
    **identify**| | |1~80|APP包名

* 返回data:

```
{
    'question_list': [
        {
            'question_id': < str >, //题目id
            'question_content': < str >, //题目内容
        }
    ]
}
```

#### 查询腕表答题结果列表
* URL: **/watch_answer_game_list**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei
    **page**| |0|0~50|页数
    **num**| |20|1~50|每页数目
    **timestamp**| | | |答题结束时间戳

* 返回data:

```
{
    'answer_list': [ //腕表答题结果列表
        {
            'answer_id': < str >, //答题结果id
            'num': < int >, //答对数目
            'timestamp': < float >, //答题时间戳
        }
    ]
}
```

#### 查询腕表答题结果详情
* URL: **/watch_answer_game**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei
    **answer_id**|Y| |24|答题结果id

* 返回data:

```
{
    'answer_detail_list': [
        {
            'question_id': < str >, //题目id
            'question_content': < str >, //题目内容
            'answer_content': < str >, //答案内容
            'result': < int >, //答题结果
        }
    ]
}
```

* 答题结果result字段:

    1: 正确;<br/>
    0: 错误;

#### 获取腕表勋章墙
* URL: **/watch_medal_wall**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **session**|Y| |12|用户session
    **imei**|Y| |15|腕表imei

* 返回data:

```
{
    'wall': [
        {
            'medal_id': < str >, //勋章id
            'medal_name': < str >, //勋章名称
            'status': < str >, //勋章状态（1:已获得，0:未获得）
            'goals': [
                {
                    'story_id': < str >, //故事id
                    'story_name': < str >, //故事名称
                    'status': < str >, //阅读状态（1:已阅，0:未阅）
                }
            ]
        }
    ]
}
```

#### 获取勋章答题题目
* URL: **/answer_medal_question**

* 请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
    **medal_id**|Y| |字符串|勋章id
    **identify**| | |1~80|APP包名

* 返回data:

```
{
    'question_list': [
        {
            'question_id': < str >, //题目id
            'question_content': < str >, //题目内容
        }
    ]
}
```