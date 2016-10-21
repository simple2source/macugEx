# -*- coding: utf-8 -*-
from PIL import Image, ExifTags
import io
import os
import conf
from bson.objectid import ObjectId

for Orientation in ExifTags.TAGS.keys():
    if ExifTags.TAGS[Orientation] == 'Orientation':
        break

# 头像模式中, normal级别,small级别的大小
normal_size = conf.static['normal_size']  # app端查看头像大小
small_size = conf.static['small_size']  # 腕表端查看头像大小


def image_drain_thumbnail(data, image_path_prefix, image_file_id):
    buff = io.BytesIO()
    buff.write(data)
    buff.seek(0)

    with Image.open(buff) as img:
        if hasattr(img, '_getexif'):
            exif = img._getexif()
            if exif:
                if exif[Orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[Orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[Orientation] == 8:
                    img = img.rotate(90, expand=True)
        img.thumbnail(normal_size, Image.ANTIALIAS)
        with open(image_path_prefix + '%s_normal.jpg' % image_file_id, 'wb') as f:
            img.save(f, format='JPEG')

    buff.seek(0)

    with Image.open(buff) as img:
        if hasattr(img, '_getexif'):
            exif = img._getexif()
            if exif:
                if exif[Orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[Orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[Orientation] == 8:
                    img = img.rotate(90, expand=True)
        img.thumbnail(small_size, Image.ANTIALIAS)
        # mask = Image.new('L', img.size, color=0)
        # draw = ImageDraw.Draw(mask)
        # draw.ellipse(small_box_size, fill=255)
        # img.putalpha(mask)
        with open(image_path_prefix + '%s_small.jpg' % image_file_id, 'wb') as f:
            img.save(f, format='JPEG')

    del buff

    with open(image_path_prefix + '%s_origin.jpg' % image_file_id, 'wb') as f:
        f.write(data)


def image_purge_thumbnail(image_path_prefix, image_file_id):
    try:
        os.remove(image_path_prefix + '%s_normal.jpg' % image_file_id)
    except OSError:
        pass
    try:
        os.remove(image_path_prefix + '%s_small.jpg' % image_file_id)
    except OSError:
        pass
    try:
        os.remove(image_path_prefix + '%s_origin.jpg' % image_file_id)
    except OSError:
        pass


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
    oid = ObjectId()
    image_drain_thumbnail(data, '../cache/user/', oid)
    return oid


def user_image_delete(oid):
    image_purge_thumbnail('../cache/user/', oid)


def user_image_find(oid):
    try:
        return open('../cache/user/%s_origin.jpg' % oid, 'rb')
    except IOError:
        return None


def watch_image_put(data):
    oid = ObjectId()
    image_drain_thumbnail(data, '../cache/watch/', oid)
    return oid


def watch_image_delete(oid):
    image_purge_thumbnail('../cache/watch/', oid)


def watch_image_find(oid):
    try:
        return open('../cache/watch/%s_origin.jpg' % oid, 'rb')
    except IOError:
        return None


def group_image_put(data):
    oid = ObjectId()
    image_drain_thumbnail(data, '../cache/group/', oid)
    return oid


def group_image_delete(oid):
    image_purge_thumbnail('../cache/group/', oid)


def group_image_find(oid):
    try:
        return open('../cache/group/%s_origin.jpg' % oid, 'rb')
    except IOError:
        return None


def plaza_image_put(data):
    oid = ObjectId()
    image_drain_thumbnail(data, '../cache/plaza/', oid)
    return oid


def plaza_image_delete(oid):
    image_purge_thumbnail('../cache/plaza/', oid)


def plaza_image_find(oid):
    try:
        return open('../cache/plaza/%s_origin.jpg' % oid, 'rb')
    except IOError:
        return None


def story_image_put(data):
    oid = ObjectId()
    image_drain_thumbnail(data, '../cache/story/', oid)
    return oid


def story_image_delete(oid):
    image_purge_thumbnail('../cache/story/', oid)


def story_image_find(oid):
    try:
        return open('../cache/story/%s_origin.jpg' % oid, 'rb')
    except IOError:
        return None


def story_audio_put(data):
    oid = ObjectId()
    with open('../cache/story/%s.amr' % oid, 'wb') as f:
        f.write(data)
    return oid


def story_audio_delete(oid):
    try:
        os.remove('../cache/story/%s.amr' % oid)
    except OSError:
        pass


def story_audio_find(oid):
    try:
        return open('../cache/story/%s.amr' % oid, 'rb')
    except IOError:
        return None


def story_content_put(data):
    oid = ObjectId()
    with open('../cache/story/%s.data' % oid, 'wb') as f:
        f.write(data)
    return oid


def story_content_delete(oid):
    try:
        os.remove('../cache/story/%s.data' % oid)
    except OSError:
        pass


def story_content_find(oid):
    try:
        return open('../cache/story/%s.data' % oid, 'rb')
    except IOError:
        return None
