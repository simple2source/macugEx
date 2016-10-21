# -*- coding: utf-8 -*-
from PIL import Image, ExifTags  # , ImageDraw
import io
import define
import conf

for Orientation in ExifTags.TAGS.keys():
    if ExifTags.TAGS[Orientation] == 'Orientation':
        break

# 头像模式中, normal级别,small级别的大小
normal_size = conf.static['normal_size']  # app端查看头像大小
small_size = conf.static['small_size']  # 腕表端查看头像大小

import file_store
import mongodb_store

__all__ = ['image_pattern_thumbnail', 'image_resize_to', 'default_image_handle']
__all__.extend(file_store.__all__)
__all__.extend(mongodb_store.__all__)
__all__ = tuple(set(__all__))


def image_pattern_thumbnail(image_file, pattern, image_path_prefix, image_file_id):
    image_path = image_path_prefix + '%s_%s.jpg' % (image_file_id, pattern)
    if pattern == 'normal':
        with Image.open(image_file) as img:
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
            with open(image_path, 'wb') as f:
                img.save(f, format='JPEG')
    elif pattern == 'small':
        with Image.open(image_file) as img:
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
            with open(image_path, 'wb') as f:
                img.save(f, format='JPEG')
    else:
        # origin 与未知格式
        with open(image_path, 'wb') as f:
            f.write(image_file.read())
    return image_path


def image_resize_to(image_file, size):
    img = Image.open(image_file)
    # 图片压缩增加抗锯齿效果,速度上慢8倍
    img = img.resize(size, Image.ANTIALIAS)
    image_buff = io.BytesIO()
    img.save(image_buff, format='JPEG')
    image_buff.seek(0)
    image_data = image_buff.read()
    return image_data


def default_image_handle():
    for data in define.config_images.values():
        for name, image_path in data.items():
            ident = image_path.rsplit('/', 1)[1].split('.', 1)[0]
            with open(image_path, 'rb') as img:
                if name == 'contact':
                    # 默认联系人头像放在用户文件夹中
                    name = 'user'

                with Image.open(img) as _img:
                    _img.thumbnail(normal_size, Image.ANTIALIAS)
                    _img.save('../cache/%s/%s_normal.jpg' % (name, ident), format='JPEG')

                img.seek(0)

                with Image.open(img) as _img:
                    _img.thumbnail(small_size, Image.ANTIALIAS)

                    # 圆角边缘 png 透明图层
                    # mask = Image.new('L', _img.size, color=0)
                    # draw = ImageDraw.Draw(mask)
                    # draw.ellipse(small_box_size, fill=255)
                    # _img.putalpha(mask)

                    _img.save('../cache/%s/%s_small.jpg' % (name, ident), format='JPEG')

                img.seek(0)

                with open('../cache/%s/%s_origin.jpg' % (name, ident), 'wb') as f:
                    f.write(img.read())


if conf.static['storage'] == 'file':

    from file_store import *

elif conf.static['storage'] == 'mongodb':

    from mongodb_store import *

else:
    raise RuntimeError('Unrecognized conf.static["storage"] variable')
