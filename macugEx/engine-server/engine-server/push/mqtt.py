# -*- coding: utf-8 -*-
import gevent
from gevent import queue
from gevent.pool import Pool
import paho.mqtt.client as mqtt
from gevent.core import READ
import random
import logging
import conf

try:
    import ujson as json
except ImportError:
    import json

from core.db import redis

logger = logging.getLogger('push')
message = queue.Queue()


def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload)
        user_id = data.get('user_id')
        if user_id:
            if data.get('focus'):
                redis.hset('User:%s' % user_id, 'app_focus', 1)
            else:
                redis.hdel('User:%s' % user_id, 'app_focus')
    except:
        logger.error('MQTT message error', exc_info=True)
    finally:
        logger.info('MQTT recv "%s"' % message.payload)


def push_mqtt(topic, pack):
    message.put((topic, pack))


def handle_write(client):
    client._sockpairR.recv(1)
    status = client.loop_write()
    if status != mqtt.MQTT_ERR_SUCCESS:
        logger.error('MQTT loop write error %s %s' % (id(client), mqtt.error_string(status)))


def handle_read(client):
    status = client.loop_read()
    if status != mqtt.MQTT_ERR_SUCCESS:
        logger.error('MQTT loop read error %s %s' % (id(client), mqtt.error_string(status)))


def keepalive(client, cycle=5):
    while client._state != mqtt.mqtt_cs_disconnecting:
        status = client.loop_misc()
        if status == mqtt.MQTT_ERR_SUCCESS:
            gevent.sleep(cycle)
        else:
            logger.error('MQTT keepalive error %s %s' % (id(client), mqtt.error_string(status)))


def pusher():
    try:
        client = mqtt.Client(client_id='%s_%s' % (conf.mqtt['prefix'], str(random.randint(0, 999999999))))
        client.username_pw_set(conf.mqtt['username'], conf.mqtt['password'])
        client.connect(conf.mqtt['host'], conf.mqtt['port'])
        loop = gevent.get_hub().loop
        watch1 = loop.io(client.socket().fileno(), READ)
        watch1.start(handle_read, client)
        watch2 = loop.io(client._sockpairR.fileno(), READ)
        watch2.start(handle_write, client)
        gevent.spawn(keepalive, client)
        while client._state != mqtt.mqtt_cs_disconnecting:
            topic, pack = message.get()
            status, mqtt_message_id = client.publish(topic, pack, 1)
            if status != mqtt.MQTT_ERR_SUCCESS:
                logger.error(
                    'MQTT publish error %s %s sending %s %s' % (id(client), mqtt.error_string(status), topic, pack))
                message.put((topic, pack))
                break
    except:
        logger.error('MQTT Exit:', exc_info=True)
    finally:
        pool.spawn(pusher)


def recver():
    try:
        client = mqtt.Client(client_id='%s_%s' % (conf.mqtt['prefix'], str(random.randint(0, 999999999))))
        client.username_pw_set(conf.mqtt['username'], conf.mqtt['password'])
        client.on_message = on_message
        client.connect(conf.mqtt['host'], conf.mqtt['port'])
        client.subscribe('%s/app/status' % conf.mqtt['prefix'])
        loop = gevent.get_hub().loop
        watch1 = loop.io(client.socket().fileno(), READ)
        watch1.start(handle_read, client)
        watch2 = loop.io(client._sockpairR.fileno(), READ)
        watch2.start(handle_write, client)
        # 阻塞运行keepalive
        keepalive(client)
    except:
        logger.error('MQTT Exit:', exc_info=True)
    finally:
        pool.spawn(recver)


pool = Pool(5)
for i in range(2):
    pool.spawn(pusher)
    gevent.sleep(0.2 * i)

pool.spawn(recver)
