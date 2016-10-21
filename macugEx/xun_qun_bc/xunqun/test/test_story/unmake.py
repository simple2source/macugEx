#!/usr/bin/env python
# -*- coding: utf-8 -*-
from types import StringTypes
import struct
import sys
import os


def is_chinese(uchar):
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return True
    else:
        return False


def pretty(string, width, fillchar=' '):
    if not isinstance(string, StringTypes):
        string = string.encode('utf-8')
    count = 0
    for c in string:
        if is_chinese(c):
            count += 2
        else:
            count += 1
    string = ''.join([string, fillchar * (width * 2 - count)])
    return string


def main(path):
    for filename in os.listdir(path):
        if filename.endswith('.data'):
            break
    else:
        raise RuntimeError('*.data file not find')
    
    with open(os.path.join(path, filename), 'rb') as f:
        block = f.read()

    FIX_HEAD_LEN = 16  # 封面区域固定头部长

    front_head = block[:FIX_HEAD_LEN]
    ident, front_len, f_text_len, f_img_len = struct.unpack('>4sIII', front_head)
    print(u"文件标识:%s" % ident)
    print(u'封面区文字大小:%9d' % f_text_len)
    print(u'封面区图片大小:%9d' % f_img_len)
    print(u'封面区总共大小:%9d' % front_len)
    print(u'封面标题:%s' % block[FIX_HEAD_LEN:FIX_HEAD_LEN + f_text_len].decode('utf-16-be'))
    print('')

    with open(os.path.join(path, 'ssss.jpg'), 'wb') as f:
        f.write(block[FIX_HEAD_LEN + f_text_len:front_len])

    FRONT_HEAD_LEN = FIX_HEAD_LEN + f_text_len + f_img_len  # FRONT_HEAD_LEN = front_len

    HEAD_LEN = 20  # 头部区域固定长

    content = block[FRONT_HEAD_LEN:]
    head = content[:HEAD_LEN]

    index_total, text_offset, image_offset, audio_type, audio_offset = struct.unpack('>IIIII', head)
    print(u'索引总数目:%9d' % index_total)
    print(u'文字区偏移:%9d' % text_offset)
    print(u'图片区偏移:%9d' % image_offset)
    print(u'语音区类型:%9d' % audio_type)
    print(u'语音区偏移:%9d' % audio_offset)
    print('')

    print(u'索引  时间 %s 图片偏移 图片大小' % pretty(u'字幕', 17))
    index_block = content[HEAD_LEN:text_offset]

    INDEX_LEN = 20  # 一个索引块长度
    image_offset_list = []
    for i in range(len(index_block) / INDEX_LEN):
        index = index_block[i * INDEX_LEN:(i + 1) * INDEX_LEN]
        a, b, c, d, e = struct.unpack('>IIIII', index)
        text = content[text_offset + b:text_offset + b + c]
        print(u'(%02d) %5d %s %5d %5d' % ((i + 1), a, pretty(text.decode('utf-16-be'), 18), d, e))
        
        if d not in image_offset_list:
            with open(os.path.join(path, 'ssss_img_%s.jpg' % len(image_offset_list)), 'wb') as f:
                f.write(content[image_offset + d: image_offset + d + e])
            image_offset_list.append(d)

    if audio_type == 0:
        audio_suffix = 'amr'
    elif audio_type == 1:
        audio_suffix = 'mp3'
    else:
        raise RuntimeError('Unrecognized audio type')

    with open(os.path.join(path, 'ssss.%s' % audio_suffix), 'wb') as f:
        f.write(content[audio_offset:])


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main('./')
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('unsupport directory: More than one parameter')
