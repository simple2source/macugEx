##### 配置步骤

1. cp setting.py.sample setting.py复制默认配置文件,并进行配置
2. 进入core,执行 db.py 建立数据库索引
3. 进入static目录,配置静态文件处理方法
4. 复制 supervisor_config.md 文件内容至 supervisor 配置文件并修改

##### 数据库model定义

watch (腕表):

* _id < str > [index]
* group_id < int > (*可选) //腕表圈子id
* imsi < str > (*可选)
* mac < str > [index]
* authcode < str >
* status < int >
    * //1: 已激活
    * //2: 已锁定
    * //3: 未激活
* serverip < str > (*可选) //腕表最新登录ip
* heartbeat < int > (*可选) //腕表登陆时设置的心跳时间
* alarms < dict > (*可选) //腕表闹钟列表
    * < str > //闹铃id值
        * < dict >
            * status: < str > 状态('on','off'),
            * cycle: < list > //eg:[1, 2, 3, 4, 5]
                * < int > //星期数
            * time: < str > 时间, eg:'08:00',
            * label: < str > 标签,
            * pattern: < str > 模式('cycle', 'single'),
            * timestamp: < float > 创建时间戳,
* fast_call_phone < str > (*可选) //腕表一键拨打号码
* fall_status < int > (*可选) //腕表脱落报警状态
* lasttime < float > (*可选) //腕表最新登录时间戳
* last_almanac_timestamp < float > (*可选) //上次同步星历的时间戳
* name < name > (*可选) //用户默认昵称(同步到圈子)
* image_id < ObjectId > (*可选) //默认头像(同步到圈子),collection='watch.image'
* phone < str > (*可选) //默认手机(同步到圈子)
* gps_start_timestamp < int > (*可选) //腕表最后一次开启gps的时间戳,用于开机时发送默认gps策略
* gps_strategy < str > (*可选) //腕表gps策略,用于设定调试模式
* software_v < int > (*可选) //腕表软件版本
* bluetooth_v < int > (*可选) //腕表蓝牙软件版本
* customer_id < int > (*可选) //腕表客户号
* medals < list > (*可选) //腕表获得勋章列表
    * < str > //勋章id
* storys < list > (*可选) //腕表已读的故事列表
    * < str > //故事id字符串
* maketime < datetime > //创建时间

watch.image (腕表头像) #gridfs.GridFS

watch.bluetooth.file (腕表蓝牙版本) #gridfs.GridFS

* version < int >

watch_loger (腕表指令日志):

* _id < ObjectId > [index]
* imei < int >
* event < str > //'send': 发送指令事件,'recv': 收到指令事件
* itype < int > //指令类型的十进制值
* data < list or str >
    * //指令参数 < list >
    * //指令数据 < str >
* timestamp < float >

watch_jobbox (腕表离线指令):

* _id < ObjectId > [index]
* imei < str > [index]
* instruct < Binary > //指令类型
* data < Binary > //指令数据
* timestamp < float >

user (用户):

* _id < ObjectId > [index]
* session < str > [index] //用户登录session
* faces < dict > (*可选) //用户人脸数据
    * < str > //face_images中 user.face._id 的字符串
        * < dict >
            * face数据,其中face\['face_id'\]为face_id
* face_images < list > (*可选)
    * ObjectId //用户人脸图像id,collection='user.face'
* face_person_id < str > (*可选) //用户person_id
* face_group_name < str > (*可选) //用户person分配到的group_name
* phone < str > (*可选) //用户第一个圈子中的手机
* share_locate < int > (*可选) //用户第一个圈子中的位置开关
* name < name > (*可选) //用户第一个圈子中的名称
* image_id < ObjectId > (*可选) //用户第一个圈子中的头像
* group_id < name > (*可选) //用户第一个圈子id
* group_name < name > (*可选) //用户第一个圈子名称
* groups < dict > (*可选) //用户圈子数据
    * < str > //圈子id字符串
        * < dict >
            * 'status': < int >, //进入1,离开0
            * 'timestamp': < float >, //进入离开时间戳
* app_token < str > (*可选) //苹果用户token
* app_ident < str > (*可选) //用户包名
* app_version < str > (*可选) //苹果用户app版本(produce, develop)
* mac < str > (*可选) 用户手机mac地址(激活腕表时的手机)
* type < int > //用户创建类型,1:一般方式; 2:NewUser接口创建
* maketime < datetime >

user.image (用户头像) #gridfs.GridFS

user.face (用户人脸图像) #gridfs.GridFS

group (圈子):

* _id < int > [index]
* name < str >
* email < str > [index]
* image_id < ObjectId > (*可选) //collection='group.image'
* password < str >
* brief < str > (*可选)
* users < dict >
    * < str > //用户_id字符串
        * < dict >
            * 'timestamp': < float > 更新时间戳
            * 'name': < str > 用户圈子昵称
            * 'phone': < str > (*可选) 用户圈子手机号
            * 'mac': < str > (*可选) 用户蓝牙mac地址
            * 'image_id': < ObjectId > (*可选) 用户圈子头像,collection='user.image'
            * 'share_locate': < int > 是否共享位置(默认关), 1:开, 0:关
            * 'status': < int > 是否被删除
* devs < dict >
    * < str > //腕表imei
        * < dict >
            * 'timestamp': < float > 更新时间戳
            * 'name': < str > 腕表家庭圈昵称
            * 'phone': < str > (*可选) 腕表家庭圈手机号
            * 'image_id': < ObjectId > (*可选) 腕表圈子头像,collection='watch.image'
            * 'operator': < ObjectId > 添加该腕表的用户id
            * 'status': < int > 是否被删除
* contacts < dict >
    * < str > //手机号phone
        * < dict >
            * 'timestamp': < float > 更新时间戳,
            * 'name': < str > 联系人昵称,
            * 'image_id': < ObjectId > 联系人头像(预留),
            * 'status': < int > 是否被删除
* timestamp < float >
    * 圈子最后修改时间(成员加入,成员修改信息,成员离开,新增联系人,删除联系人)
* maketime < datetime >
    * 圈子创建时间

group.image (圈子头像) #gridfs.GridFS

message (消息):

* _id < ObjectId > [index]
* group_id < int > [index]
* type < int >
    * 1: 语音消息 'audio'
    * 2: 图片消息 'image'
    * 3: 文字消息 'text'
    * 4: 腕表轨迹点信息
    * 5: 腕表故事确认
* content < dict or unicode or ObjectId >
    * type=1: < ObjectId >,collection='message.audio'
    * type=2: < ObjectId >,collection='message.image'
    * type=3,5,7: < unicode >
    * type=4: < dict >
* length < int > (*可选) //语音长度,type=1时存在
* percent < int > (*可选) //腕表电量,type=6时存在
* watch_locate < dict > (*可选) //腕表轨迹点信息,type=4时存在
* story_id < str > (*可选) //腕表下载完成的故事id,type=5时存在
* sender < str > //用户id 或是 腕表imei
* sender_type < int >
    * 1: 用户发送消息
    * 2: 腕表发送消息
* timestamp < float >

message.audio (消息语音) #gridfs.GridFS

message.image (消息图片) #gridfs.GridFS

watch_locate (腕表定位):

* _id < ObjectId > [index]
* imei < str > [index]
* address < str > (*可选)
* province < str > (*可选)
* city < str > (*可选)
* citycode < str > (*可选) //城市编码
* adcode < str > (*可选) //区域编码
* type < int >
    * 1: GPS定位方式
    * 2: 基站定位方式
* loc < lon < float >, lat < float > > [2dsphere]
* raw_loc < lon < float >, lat < float > > (*可选) //原始gps经纬度, loc_type=1时存在
* radius < int > //LBS定位高德返回定位精度,GPS定位时为0
* timestamp < float > [index]

watch_locus (腕表定位轨迹点):

* _id < ObjectId > [index]
* imei < str > [index]
* type < int > //定位类型,1:GPS,2:LBS
* lon < float >
* lat < float >
* radius < int > //轨迹有效半径,为下个轨迹点与该点距离,200~500
* lbs_radius < str > (*可选) //lbs轨迹点的定位点半径,高德返回
* address < str >
* timestamp < float >

user_locate (用户定位):

* _id < ObjectId > [index]
* user_id < str > [index]
* address < str > (*可选)
* province < str > (*可选)
* city < str > (*可选)
* citycode < str > (*可选)
* adcode < str > (*可选)
* loc < < float >, < float > > [2dsphere]
* radius < int > //APP上传的定位精度
* timestamp < float > [index]

user_locus (用户定位轨迹点):

* _id < ObjectId > [index]
* user_id < str > [index]
* lon < float >
* lat < float >
* radius < int > //轨迹有效半径,为下个轨迹点与该点距离,200~500
* timestamp < float >

devicetoken (苹果token集合):

* _id < str > [index] //64位长度苹果deviceToken字符串
* user_id < str > //用户id字符串

banner (幻灯片)

* _id < ObjectId > [index]
* image_id < ObjectId >
* story_id < ObjectId > (*可选) //故事id
* url < str > (*可选) //链接url

banner.image (应用页面幻灯片) #gridfs.GridFS

appstore.category (应用分类)

* _id < str > [index]
* name < str > //分类名字
* image_id < ObjectId > //分类彩色图片
* image_id2 < ObjectId > //分类黑白图片
* sort < int > //排序值,越小越前

appstore.category.image (应用图片) #gridfs.GridFS

story (故事)

* _id < ObjectId > [index]
* image_id < ObjectId > //故事封面图片,collection='story.image'
* images < list >
    * < ObjectId > //故事内容图片,collection='story.image'
* slice_text < list >
    * < str > //故事内容分段文字
* slice_image < list >
    * < int > //故事内容分段图片索引
* slice_time < list >
    * < int > //故事内容分段时间毫秒
* category_id < str > (*可选) [index] //故事分类id,暂时全是 story
* audio_id < str > //故事语音id,collection='story.audio'
* audio_type < str > //故事语音的类型, 'amr' or 'mp3'
* content_id < ObjectId > //故事内容id,collection='story.content'
* title < str > //故事名字
* brief < str > //故事简介

story.image (故事图片) #gridfs.GridFS

story.audio (故事语音) #gridfs.GridFS

story.content (故事内容) #gridfs.GridFS

version (APP版本记录)

* _id < ObjectId > [index]
* number < int > [index] //版本号数
* name < str > //版本名字
* platform < str > //版本适配平台
* log < str > //版本更新说明
* file_id < ObjectId > //版本文件id,collection='version.file'
* maketime < datetime >

version.file (版本软件) #gridfs.GridFS

plaza (广场消息)

* _id < ObjectId > [index]
* user_id < str > //发送用户id
* content < str > //消息内容
* images < list >
    * < ObjectId > //消息图片,collection='plaza.image'
* likes < list > //点赞列表
    * < dict > :
        * 'user_id' : < str >, //点赞用户id
        * 'timestamp': < float >, //点赞时间
* like_num < int > //消息点赞数目
* comments < list > //评论列表
    * < dict > :
        * 'comment_id': < str >, //评论id字符串
        * 'user_id': < str >, //评论用户id
        * 'content': < str >, //评论内容
        * 'timestamp': < float >, //评论时间
* comment_num < int > //消息评论数目
* lon < float > //消息经度标记
* lat < float > //消息纬度标记
* address < float > //消息位置标记
* timestamp < float >

plaza.image (广场消息图片) #gridfs.GridFS

plaza_like (广场消息点赞记录)

* _id < str > [index] //"%s-%s" % (广场消息id, 用户id)
* user_id < str > //点赞用户id
* timestamp < float >  [index]

plaza_comment (广场消息评论记录)

* _id < ObjectId > [index]
* post_id < str > [index] //评论的消息id字符串
* user_id < str > //评论用户id
* content < str > //评论内容
* timestamp < float >

submail (submail事件)

* _id < ObjectId > [index]
* email < str > //操作email
* events < str > //触发事件
* message_id < str > (*可选) //SMTP ID
* send_id < str > (*可选) //发送ID（唯一标示）
* tag < str > (*可选) //自定义标签
...
* timestamp < float > [index]

watch_gps_loger (腕表调试用定位记录)

* _id < ObjectId > [index]
* imei < str > [index]
* address < str >
* province < str >
* city < str >
* citycode < str >
* adcode < str >
* loc < lon < float >, lat < float > >
* spendtime < float >
* spendid < int > [index]
* send_timestamp < float >
* recv_timestamp < float >

answer_game (腕表答题游戏)

* _id < ObjectId > [index]
* category_id < str > //问题分类id
* question < str > //问题文字
* answer < str > //答案文字
* option < int > //正确选项1(对勾)或2(打叉)

answer_game.category (腕表答题游戏分类)

* _id < str > [index]
* name < str >
* image_id < ObjectId >
* sort < int > //排序值,越小越前

answer_game.category.image (腕表答题游戏图片) #gridfs.GridFS

watch_answer_game (腕表答题游戏结果)

* _id < ObjectId > [index]
* imei < str > [index] //腕表imei
* question_list < list > //问题列表
    * < str > //问题id
* result_list < list >
    * < int > //答题结果(1:对,0:错)
* num < int > //答对数目
* start_timestamp < float > //开始答题时间戳
* end_timestamp < float > [index] //结束答题时间戳

medal (勋章)

* _id < str > //勋章id
* story_list < list > //关联故事列表
    * < str > //故事id字符串
* question_list < list > //关联问题列表
    * < str > //问题id
* sort < int > //排序值,越小越前

......


##### Redis 数据键值定义

* 'Watch:%s' % imei
    * 类型: Hash
    * 键值:
        * authcode:
            * 随机5位字符,腕表登陆后获得的加密秘钥
            * 腕表访问http时使用的session字段
        * group_id:
            * 圈子id
        * operator:
            * 添加该腕表的用户id字符串
        * request_gps_users:
            * user_list < ','.join([user_id]) >
                * APP请求将gps定位推送到用户
        * request_lbs_users:
            * user_list < ','.join([user_id]) >
                * APP请求将gps,lbs定位推送到用户
        * monitor_user_id:
            * 当前监听腕表的用户id
        * watch_star:
            * 腕表当前搜索到的gps卫星数目
        * catch_star:
            * 腕表当前捕捉到的gps卫星数目
        * star_quality:
            * 腕表当前gps卫星质量
        * gps_logging:
            * {'id': id, 'timestamp': timestamp}
            * gps测试开启时间,用于服务器记录gps定位时间
        * customer_id:
            * 腕表客户号
        * answering:
            * 是否正在进行答题游戏
    * 过期: 永不过期

* 'WatchToken:%s:%s' % (imei, code)
    * 类型: String
    * 键值:
        * 随机6位字符
            * APP请求添加腕表的验证码
    * 过期: 1小时

* 'Session:%s' % session前三位
    * 类型: Hash
    * 键值:
        * session后九位: 用户id
            * 用户session的对应值
    * 过期: 永不过期

* 'User:%s' % user_id
    * 类型: Hash
    * 键值:
        * groups < 需要事务操作 >: { //用户所有圈子信息json字典字符串
            * group_id: 
                * {'status': 1, 'timestamp': timestamp}
        * }
        * app_token: 苹果用户token
        * app_ident: 苹果用户包名
        * app_version: 苹果用户app版本(produce, develop)
            * 获得用户苹果devicetoken
        * app_focus: 苹果用户APP正在前台运行的标识位
        * map_push_user: [
            * user_list < ','.join([user_id]) >
                * 请求该用户定位的其他用户
        * ]
        * session: 用户session数据,用于删除用户redis数据时不到数据库查找
        * clean: 该用户的redis数据应该被清除
    * 过期: 永不过期

* 'GroupAppleUser:%s' % group_id
    * 类型: Set
    * 键值:
        * 苹果用户id
            * 得到圈子中所有的苹果用户,再获得用户token
    * 过期: 永不过期

* 'GroupInvite:%s' % group_id
    * 类型: String
    * 键值:
        * 随机6位数字
            * 圈子的邀请验证码
    * 过期: 1天

* 'HotCategory:%s' % category_id
    * 类型: Zset
    * 键:
        * 故事id
    * 值:
        * 故事被发送到手表的次数
    * 过期: 永不过期

* 'AnswerGame'
    * 类型: Zset
    * 键:
        * imei
    * 值:
        * 腕表答对题目的总分数
    * 过期: 永不过期

* 'AlmanacTimestamp'
    * 类型: String
    * 键值:
        * 星历文件的有效时间戳
    * 过期: 永不过期

* 'ResumeUser:%s' % code
    * 类型: String
    * 键:
        * 随机4位字符(英文为大写)
    * 值:
        * 所找回用户的userid
    * 过期: 10分钟
