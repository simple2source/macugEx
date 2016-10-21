# -*- coding: utf-8 -*-
"""
便于进入app目录对业务进行操作的文件
usage:
    from tools import *
"""
import sys

sys.path.append('..')
import logging

logging.basicConfig()

from api.tools import *
from api.errno import *
from core.db import *
from static.define import *

from IPython import embed

embed()
