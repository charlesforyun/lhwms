import datetime
import hashlib

import redis

from lhwms.settings import REDIS_HOST
from lhwms.settings import REDIS_PORT

'''
==========================================================
redis连接池，redis key值生成，用于数据缓存 和数据分页key值
==========================================================
'''
# 单例连接池对象, 通过模块导入，第一次会生成pyc文件，第二次导入直接引用pyc文件
# redis用户查询条件库 连接池
pool_terms = redis.ConnectionPool(host=REDIS_HOST,
                                  port=REDIS_PORT, db=3, decode_responses=True)

# redis用户查询结果 连接池
pool_result = redis.ConnectionPool(host=REDIS_HOST,
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
    '''清理用户查询结果和导入数据缓存'''
    rc_key = get_key(request, model, query_mark)
    rc_terms = redis.Redis(connection_pool=pool_terms)  # redis对象，操作redis
    rc_result = redis.Redis(connection_pool=pool_result)
    rc_import = redis.Redis(connection_pool=pool_import)
    rc_terms.delete(rc_key)
    rc_result.delete(rc_key)
    rc_import.delete(rc_key)
    return True
