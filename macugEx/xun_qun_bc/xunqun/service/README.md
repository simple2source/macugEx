#### 客服模块

用于客户咨询问答的交互模块

##### 数据库model定义

question (问题):

* _id < ObjectId > [index]
* user_id < str > [index] //提问者id
* status < int > [index] //问题状态(1:待解决,2:解决中,3:已解决)
* serv_id < str > [index] //解答该问题的客服id
* star < int > //该问题客服得分
* title < str > //该问题显示标题
* timestamp < float >

question_message (问题消息):

* _id < ObjectId > [index]
* question_id < str > [index] //问题id
* type < int > //消息类型
    * 1: 语音消息
    * 2: 图片消息
    * 3: 文字消息
    * 4: 动作消息

* audio_id < ObjectId >  (*可选) //语音id,type=1时存在
* audio_len < int > (*可选) //语音长度,type=1时存在

* image_id < ObjectId > (*可选) //图片id,type=2时存在

* text < str > (*可选) //图片id,type=3时存在

* action < int > (*可选) //动作类型,type=4时存在
    * //1:客服开始处理、2:客服退出处理、3:客服请求结束处理、4:本问题已完成处理、5:本问题已超时

* sender < str > //用户id或客服id
* sender_type < int >
    * 1: 用户发送消息
    * 2: 客服发送消息
* timestamp < float >

question_message.audio (问题语音) #gridfs.GridFS

question_message.image (问题图片) #gridfs.GridFS

service (客服):

* _id < str > [index]
* password < str >
* user_id < ObjectId > //客服绑定的用户id
* maketime < datetime >

serv_template (客服回答模板):

* _id < str > [index]
* title < str > //模板问题
* content <str> //模板答案

serv_template_item (客服回答模板条目):

* _id < ObjectId > [index]
* template_id < str > [index]
* content < str > //模板条目内容
