# -*- coding: utf-8 -*-
"""
APP接口验证表单
"""
from __future__ import absolute_import
from .validate import Form, StrictForm, StringField, IntField, FloatField, EmailField, ImageField, ListField


class GroupCreate(StrictForm):
    group_name = StringField(max_length=20)
    group_image = ImageField()
    password = StringField(min_length=3, max_length=20)
    group_email = EmailField()
    brief = StringField(max_length=80)
    user_name = StringField(max_length=20)
    user_image = ImageField()
    phone = StringField(min_length=3, max_length=20)
    identify = StringField()


class GroupNew(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_name = StringField(max_length=20)
    group_image = ImageField()
    password = StringField(min_length=3, max_length=20)
    group_email = EmailField()
    brief = StringField(max_length=80)
    user_name = StringField(max_length=20)
    user_image = ImageField()
    phone = StringField(min_length=3, max_length=20)
    identify = StringField()


class GroupModifyUserInfo(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    user_name = StringField(max_length=20)
    phone = StringField(min_length=3, max_length=20)
    user_image = ImageField()
    share_locate = IntField()


class GroupNewWatch(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    imei = StringField(required=True, min_length=15, max_length=15)
    authcode = StringField(required=True, min_length=6, max_length=6)
    watch_name = StringField(max_length=20)
    phone = StringField(min_length=3, max_length=20)
    watch_image = ImageField()
    user_phone = StringField(min_length=3, max_length=20)
    identify = StringField()


class SessionImei(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei = StringField(required=True, min_length=15, max_length=15)


class Session(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)


class Imei(StrictForm):
    imei = StringField(required=True, min_length=15, max_length=15)


class GroupInfo(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    timestamp = FloatField()  # 不传时为None,None与所有值比较都小,可以获得圈子所有数据


class SessionGroupId(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)


class GroupAcceptInvite(StrictForm):
    invitecode = StringField(required=True, min_length=6, max_length=6)
    group_id = IntField(required=True)


class GroupEnter(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    invitecode = StringField(min_length=6, max_length=6)
    group_id = IntField(required=True, min_value=1000000000, max_value=9999999999)
    group_password = StringField(min_length=3, max_length=20)
    user_name = StringField(max_length=20)
    user_image = ImageField()
    phone = StringField(min_length=3, max_length=20)
    identify = StringField()


class GroupJoin(StrictForm):
    invitecode = StringField(min_length=6, max_length=6)
    group_id = IntField(required=True, min_value=1000000000, max_value=9999999999)
    group_password = StringField(min_length=3, max_length=20)
    user_name = StringField(max_length=20)
    user_image = ImageField()
    phone = StringField(min_length=3, max_length=20)
    identify = StringField()


class SessionGroupIdUserId(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    user_id = StringField(required=True, min_length=24, max_length=24)


class SessionTimestamp(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    timestamp = FloatField(default=0.0)


class GroupAddContact(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    contact_name = StringField(max_length=20)
    phone = StringField(required=True, min_length=3, max_length=20)
    identify = StringField()


class GroupDelContact(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    phone = StringField(required=True, min_length=3, max_length=20)


class GroupSendMessage(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    type = IntField(required=True, enumerate=(1, 2, 3))
    content = StringField(required=True)
    length = IntField(max_value=20)


class GroupRecvMessage(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=20)
    message_id = StringField(min_length=24, max_length=24)
    sort = IntField(default=-1)


class UserBindDeviceToken(Form):
    devicetoken = StringField(min_length=64, max_length=64)
    identify = StringField(min_length=1, max_length=80)
    version = StringField(enumerate=('produce', 'develop'))


class GroupModifyInfo(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    group_image = ImageField()
    group_name = StringField(max_length=20)
    newpassword = StringField(min_length=3, max_length=20)
    group_email = EmailField()


class WatchRequestLocate(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei = StringField(required=True, min_length=15, max_length=15)
    # num = IntField(required=True, min_value=1, max_value=120)
    # interval = IntField(min_value=1, max_value=300)
    type = StringField(default='gps', enumerate=('gps', 'lbs'))


class WatchAlarmSet(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei = StringField(required=True, min_length=15, max_length=15)
    id = StringField()
    status = StringField(enumerate=('on', 'off', 'delete'))
    cycle = StringField(max_length=14)
    time = StringField(max_length=5, min_length=5)
    label = StringField(max_length=20)
    pattern = StringField(enumerate=('cycle', 'single'))


class UserUploadLocate(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    type = IntField(required=True)
    # FIXME app上传参数错误时暂时在endpoint函数中处理
    # lon = FloatField(required=True, max_value=180, min_value=-180)
    # lat = FloatField(required=True, max_value=90, min_value=-90)
    lon = FloatField(required=True)
    lat = FloatField(required=True)
    radius = FloatField(required=True)


class DelWatch(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    imei = StringField(required=True, min_length=15, max_length=15)
    throughly = IntField(default=1)


class WatchInfo(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei = StringField(min_length=15, max_length=15)
    mac = StringField(min_length=12, max_length=12)


class GroupModifyWatchInfo(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    imei = StringField(required=True, min_length=15, max_length=15)
    watch_name = StringField(max_length=20)
    phone = StringField(min_length=3, max_length=20)
    watch_image = ImageField()
    fast_call_phone = StringField(min_length=3, max_length=20)
    gps_strategy = StringField(min_length=3, max_length=20, enumerate=('default', 'delete'))


class WatchGetLoc(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei = StringField(required=True, min_length=15, max_length=15)
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50)
    start_timestamp = FloatField()
    end_timestamp = FloatField()
    type = StringField(enumerate=('gps', 'lbs'))


class WatchGetLocDateNum(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei = StringField(required=True, min_length=15, max_length=15)
    start_timestamp = FloatField()
    end_timestamp = FloatField()


class UserGetLoc(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    group_id = IntField(required=True)
    user_id = StringField(required=True, min_length=24, max_length=24)
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=10)
    start_timestamp = FloatField()
    end_timestamp = FloatField()


class AppstoreIndex(StrictForm):  # FIXME 应用未用到
    identify = StringField()


class StoryList(StrictForm):
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=10)
    category_id = StringField()
    story_id = StringField(min_length=24, max_length=24)


class StoryHotList(StrictForm):
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=10)
    category_id = StringField(required=True)
    story_id = StringField(min_length=24, max_length=24)


class StoryId(StrictForm):
    story_id = StringField(required=True, min_length=24, max_length=24)


class SendStory(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei = StringField(required=True, min_length=15, max_length=15)
    story_id = StringField(required=True, min_length=24, max_length=24)


class LastVersion(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    platform = StringField(enumerate=('android', 'ios'))
    model = StringField(required=True, min_length=1, max_length=50)
    current_version = IntField(required=True, min_value=1)
    identify = StringField()  # FIXME 更新android版本未用到app包名


class PlazaSendMessage(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    content = StringField()
    images = ListField(ImageField())
    lon = FloatField()
    lat = FloatField()
    address = StringField()


class PlazaRecvMessage(Form):
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=20)
    post_id = StringField(min_length=24, max_length=24)
    identify = StringField()


class PlazaLike(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    post_id = StringField(required=True, min_length=24, max_length=24)
    liking = IntField(required=True, enumerate=(1, 2))


class PlazaComment(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    post_id = StringField(required=True, min_length=24, max_length=24)
    content = StringField(required=True)


class PlazaLikeRecord(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    post_id = StringField(required=True, min_length=24, max_length=24)
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=20)
    timestamp = FloatField()
    identify = StringField()
    sort = IntField(default=-1)


class PlazaCommentRecord(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    post_id = StringField(required=True, min_length=24, max_length=24)
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=20)
    comment_id = StringField(min_length=24, max_length=24)
    identify = StringField()
    sort = IntField(default=-1)


class FaceSetSession(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    face_image = ImageField(required=True)


class FaceGetSession(StrictForm):
    face_id = StringField(required=True, min_length=32, max_length=32)


class GroupActiveWatch(StrictForm):
    session = StringField(min_length=12, max_length=12)
    group_id = IntField()
    imei = StringField(required=True, min_length=15, max_length=15)
    mac = StringField(required=True, min_length=12, max_length=12)
    watch_name = StringField(max_length=20)
    phone = StringField(min_length=3, max_length=20)
    watch_image = ImageField()
    user_phone = StringField(min_length=3, max_length=20)
    identify = StringField()
    customer_id = IntField()


class SessionPostId(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    post_id = StringField(required=True, min_length=24, max_length=24)


class GroupGenerate(StrictForm):
    imei = StringField(required=True, min_length=15, max_length=15)
    mac = StringField(min_length=12, max_length=12)
    authcode = StringField(min_length=6, max_length=6)
    group_name = StringField(max_length=20)
    group_image = ImageField()
    password = StringField(min_length=3, max_length=20)
    group_email = EmailField()
    brief = StringField(max_length=80)
    user_name = StringField(max_length=20)
    user_image = ImageField()
    watch_name = StringField(max_length=20)
    watch_phone = StringField(min_length=3, max_length=20)
    watch_image = ImageField()
    user_phone = StringField(min_length=3, max_length=20)
    identify = StringField()
    customer_id = IntField()


class GroupMake(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei = StringField(required=True, min_length=15, max_length=15)
    mac = StringField(required=True, min_length=12, max_length=12)
    group_name = StringField(max_length=20)
    group_image = ImageField()
    password = StringField(min_length=3, max_length=20)
    group_email = EmailField()
    brief = StringField(max_length=80)
    user_name = StringField(max_length=20)
    user_image = ImageField()
    watch_name = StringField(max_length=20)
    watch_phone = StringField(min_length=3, max_length=20)
    watch_image = ImageField()
    user_phone = StringField(min_length=3, max_length=20)
    identify = StringField()
    customer_id = IntField()


class AnswerGameSend(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei = StringField(required=True, min_length=15, max_length=15)
    game_id_list = ListField(StringField(required=True, min_length=24, max_length=24), required=True)


class AnswerGameRank(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=10)
    identify = StringField()


class AnswerGameSearch(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei_list = ListField(StringField(required=True, min_length=15, max_length=15), required=True)


class SessionIdentify(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    identify = StringField()


class AnswerGameQuestion(StrictForm):
    category_id = StringField(required=True)
    num = IntField(min_value=1, max_value=50, default=10)
    identify = StringField()


class AnswerGameList(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei = StringField(required=True, min_length=15, max_length=15)
    page = IntField(min_value=0, max_value=50, default=0)
    num = IntField(min_value=1, max_value=50, default=20)
    timestamp = FloatField()


class AnswerGame(StrictForm):
    session = StringField(required=True, min_length=12, max_length=12)
    imei = StringField(required=True, min_length=15, max_length=15)
    answer_id = StringField(required=True, min_length=24, max_length=24)


class RenewSession(StrictForm):
    user_id = StringField(required=True, min_length=24, max_length=24)
    identify = StringField()  # TODO identify 识别


class NewUser(StrictForm):
    user_name = StringField(max_length=20)
    user_image = ImageField()
    identify = StringField()


class AuthCode(StrictForm):
    authcode = StringField(required=True, min_length=4, max_length=4)


class AnswerMedalQuestion(StrictForm):
    medal_id = StringField(required=True)
