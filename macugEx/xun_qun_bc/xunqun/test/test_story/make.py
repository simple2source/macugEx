#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import struct
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../admin'))
from tools import make_story_content


def main(path, format):
    if format not in ['amr', 'mp3']:
        raise RuntimeError('Bad format support: %s' % format)

    dir_file = os.listdir(path)
    text_length = []  # 文字长度
    text_list = []
    time_detal_list = []  # 时间索引
    image_index = []  # 图片索引

    for i in dir_file:
        if i.endswith('.%s' % format):
            with open(os.path.join(path, i), 'rb') as f:
                audio_block = f.read()  # 语音区

            file_name = i.rsplit('.', 1)[0]
            break
    else:
        raise RuntimeError('*.%s file not find' % format)

    if not audio_block:
        raise RuntimeError('%s is empty file' % i)

    try:
        with open(os.path.join(path, '%s.jpg' % file_name), 'rb') as f:
            front_image = f.read()
    except IOError:
        raise RuntimeError('Front cover %s.jpg not find' % file_name)

    front_text = file_name.decode('utf-8').encode('utf-16-be')

    with open(os.path.join(path, '%s.txt' % file_name)) as f:
        print(u'解析故事索引')
        for i, l in enumerate(f):
            if l[-1] == '\n':
                l = l[:-1]
            print('(%2d) %s' % (i, l))
            img_index, time_detal, text = l.split(',', 2)
            text = text.strip().decode('utf-8').encode('utf-16-be')
            text_length.append(len(text))
            text_list.append(text)
            time_detal_list.append(int(time_detal))
            image_index.append(int(img_index) - 1)

    images = os.listdir(os.path.join(path, 'img'))
    image_length = []  # 图片长度
    image_list = []
    for i in images:
        if i.endswith('.jpg'):
            with open(os.path.join(path, 'img', i), 'rb') as f:
                img = f.read()
            image_length.append(len(img))
            image_list.append(img)

    print('')
    print(u'生成故事索引')
    for i, time_detal in enumerate(time_detal_list):
        if i == 0:
            text_offset = 0
        else:
            text_offset = sum(text_length[:i])

        image_offset = sum(image_length[:image_index[i]])
        print('%5d %3d %2d %5d' % (time_detal, text_offset, text_length[i], image_offset))

    with open(os.path.join(path, file_name + '.data'), 'wb') as f:
        f.write(make_story_content(
            front_image, front_text, image_index, time_detal_list, text_list, image_list, format, audio_block
        ))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main('./', 'amr')
    elif len(sys.argv) == 2:
        main(sys.argv[1], 'amr')
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print('usage: ./make.py directory format')
