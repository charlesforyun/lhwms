import json
import datetime
import re
import os
import hashlib
import copy
import math

import redis
from pymysql import escape_string

import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill

from django.http import HttpResponse
from django.http import FileResponse

from django.db import connection
from django.db import transaction
from lhwms.settings import DATABASES

from lhwms.settings import MEDIA_ROOT
from lhwms.settings import TEMP_DIR
from lhwms.settings import REDIS_HOST
from lhwms.settings import REDIS_PORT

from user.models import *
from master.models import *
from log.models import *

# redis用户查询条件库 连接池
pool_terms = redis.ConnectionPool(host=REDIS_HOST,
                                  port=REDIS_PORT, db=3, decode_responses=True)

# redis用户查询结果 连接池
pool_querys = redis.ConnectionPool(host=REDIS_HOST,
                                   port=REDIS_PORT, db=4, decode_responses=True)

# redis用户导入数据缓存库 连接池
pool_import = redis.ConnectionPool(host=REDIS_HOST,
                                   port=REDIS_PORT, db=5, decode_responses=True)


def get_ufn(request):
    '''生成唯一文件名'''
    tk = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    m = hashlib.md5()
    m.update(bytes(tk, encoding='utf8'))
    return m.hexdigest()


def get_key(request, model, query_mark):
    '''生成redis中的key值'''
    mname = model.__name__
    query_mark = str(query_mark)
    return ','.join([mname, query_mark])  # 序列拼接


def clean_querys(request, model, query_mark):
    '''清理用户查询条件、查询结果和导入数据缓存'''
    key = get_key(request, model, query_mark)
    rc_terms = redis.Redis(connection_pool=pool_terms)  # redis对象，操作redis
    rc_querys = redis.Redis(connection_pool=pool_querys)
    rc_import = redis.Redis(connection_pool=pool_import)
    rc_terms.delete(key)
    rc_querys.delete(key)
    rc_import.delete(key)
    return True
