### 推送问题消息格式

#### 问题聊天语音消息

* apns参数: {'content_available': 1, 'data': data}
* 推送数据: {
	* "**push_type**": "service"
	* "**sender**": < str >  // 用户id 或客服id
	* "**sender_type**": < int > // 1:用户，2:客服
	* "**question_id**": < str >
	* "**message_id**": < str >
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：1
	* "**audio_url**": < str >  // 语音url
	* "**audio_len***": < int >  // 语音时长
* }

#### 问题聊天图片消息

* apns参数: {'content_available': 1, 'data': data}
* 推送数据: {
	* "**push_type**": "service"
	* "**sender**": < str >  // 用户id 或客服id
	* "**sender_type**": < int > // 1:用户，2:客服
	* "**question_id**": < str >
	* "**message_id**": < str >
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：2
	* "**image_url**": < str >  // 图像url
* }

#### 问题聊天文字消息

* apns参数: {'content_available': 1, 'data': data}
* 推送数据: {
	* "**push_type**": "service"
	* "**sender**": < str >  // 用户id 或客服id
	* "**sender_type**": < int > // 1:用户，2:客服
	* "**question_id**": < str >
	* "**message_id**": < str >
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：3
	* "**text**": < str >  //文本内容
* }

#### 问题聊天通知消息

* apns参数: {'content_available': 1, 'data': data}
* 推送数据: {
	* "**push_type**": "service"
	* "**sender**": < str >  // 用户id 或客服id
	* "**sender_type**": < int > // 1:用户，2:客服
	* "**question_id**": < str >
	* "**message_id**": < str >
	* "**timestamp**": < float >
	* "**type**": < int > // 消息类型：4
	* "**action**": < int > // 通知动作类型
* }
