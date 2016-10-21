# -*- coding: utf-8 -*-
from core.db import db
import gridfs

user_image = gridfs.GridFS(db, collection='user.image')
watch_image = gridfs.GridFS(db, collection='watch.image')
group_image = gridfs.GridFS(db, collection='group.image')
plaza_image = gridfs.GridFS(db, collection='plaza.image')
story_image = gridfs.GridFS(db, collection='story.image')
story_audio = gridfs.GridFS(db, collection='story.audio')
story_content = gridfs.GridFS(db, collection='story.content')

__all__ = (
    'user_image_put', 'user_image_delete', 'user_image_find',
    'watch_image_put', 'watch_image_delete', 'watch_image_find',
    'group_image_put', 'group_image_delete', 'group_image_find',
    'plaza_image_put', 'plaza_image_delete', 'plaza_image_find',
    'story_image_put', 'story_image_delete', 'story_image_find',
    'story_audio_put', 'story_audio_delete', 'story_audio_find',
    'story_content_put', 'story_content_delete', 'story_content_find',
)


def user_image_put(data):
    return user_image.put(data)


def user_image_delete(oid):
    return user_image.delete(oid)


def user_image_find(oid):
    return user_image.find_one(oid)


def watch_image_put(data):
    return watch_image.put(data)


def watch_image_delete(oid):
    return watch_image.delete(oid)


def watch_image_find(oid):
    return watch_image.find_one(oid)


def group_image_put(data):
    return group_image.put(data)


def group_image_delete(oid):
    return group_image.delete(oid)


def group_image_find(oid):
    return group_image.find_one(oid)


def plaza_image_put(data):
    return plaza_image.put(data)


def plaza_image_delete(oid):
    return plaza_image.delete(oid)


def plaza_image_find(oid):
    return plaza_image.find_one(oid)


def story_image_put(data):
    return story_image.put(data)


def story_image_delete(oid):
    return story_image.delete(oid)


def story_image_find(oid):
    return story_image.find_one(oid)


def story_audio_put(data):
    return story_audio.put(data)


def story_audio_delete(oid):
    return story_audio.delete(oid)


def story_audio_find(oid):
    return story_audio.find_one(oid)


def story_content_put(data):
    return story_content.put(data)


def story_content_delete(oid):
    return story_content.delete(oid)


def story_content_find(oid):
    return story_content.find_one(oid)
