# -*- coding: utf-8 -*-
"""
apnsclient/backends/stdio.py
41 line:
- context = OpenSSL.SSL.Context(OpenSSL.SSL.SSLv3_METHOD)
+ context = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_METHOD)
188 line:
- self._connection.do_handshake()
+ while 1:
+     try:
+         self._connection.do_handshake()
+         break
+     except OpenSSL.SSL.WantReadError:
+         continue
"""
import OpenSSL
from apnsclient import Session, APNs, Message
import logging
import os

logger = logging.getLogger('push.apns')
import json

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), './config.json'), 'r') as f:
    config = json.loads(f.read())

for ident in config:
    conf = config[ident]
    conf['password'] = str(conf['password'])
    conf['dev_sess'] = Session()
    conf['dev_sess'].new_connection("push_sandbox", cert_file=conf['develop'], passphrase=conf['password'])
    conf['pro_sess'] = Session()
    conf['pro_sess'].new_connection("push_production", cert_file=conf['produce'], passphrase=conf['password'])


# config = {
#     "com.xTT.myWatch":{
#         "develop": "./cert/develop.pem",
#         "produce": "./cert/produce.pem",
#         "password": "mbmbmb",
#         "dev_sess": <Session>,
#         "pro_sess": <Session>
#     }
# }

def push_apns(push_token, push_params):
    """
    :param push_token:
            {'token': token, 'ident': ident, 'version': version},
    :param push_params:
            {
                'content_available': 1,
                'data': data
            } or {
                'alert': '新宝贝定位消息',
                'sound': 'default',
                'data': data
            }
            ...
    :return:
    """
    try:
        push_conf = config[push_token['ident']]
        message = Message(push_token['token'], **push_params)
        if push_token['version'] == 'develop':
            con = push_conf['dev_sess'].get_connection("push_sandbox", cert_file=push_conf['develop'],
                                                       passphrase=push_conf['password'])
        else:
            con = push_conf['pro_sess'].get_connection("push_production", cert_file=push_conf['produce'],
                                                       passphrase=push_conf['password'])
        srv = APNs(con)
        for i in range(5):
            try:
                res = srv.send(message)
            except OpenSSL.SSL.WantReadError:
                logger.error('want read error in push')
            except:
                logger.error('APNs fail:', exc_info=True)
            else:
                fail = 0
                for token, reason in res.failed.items():
                    code, errmsg = reason
                    if code == 8:  # Invalid Token
                        # FIXME 用户将APP删除后会造成无效token,清除无效用户token
                        # NOTE 每次message里只有一个token消息,无效时不重试
                        logger.error("APNs Device Invalid Token: {0}".format(token))
                        break
                    else:
                        logger.error("APNs Device failed: {0}, reason: {1}".format(token, errmsg))
                        fail = 1
                for code, errmsg in res.errors:
                    logger.error("APNs Error: {}".format(errmsg))
                    fail = 1
                if res.needs_retry():
                    # NOTE 每次message里只包含一个token的消息,所以不用重新赋值
                    # message = res.retry()
                    continue
                if not fail:
                    break
    except KeyError:
        logger.error('Nofind ident: %s' % repr(push_token))
