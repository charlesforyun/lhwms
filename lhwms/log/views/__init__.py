import logging.handlers
import datetime
import os
from lhwms.settings import MEDIA_ROOT

"""
#####################
日志使用单例模式下logger对象，handler对象
#####################
"""
dirname = os.path.join(MEDIA_ROOT + '/logs')
dirname1 = os.path.join(dirname + '/all.log')
dirname2 = os.path.join(dirname + '/error.log')

if not os.path.exists(dirname):
    os.mkdir(dirname)

logger = logging.getLogger('lhwms')  # 获取logger对象,建立日志器,全局放入即可输出

handlerToFileAll = logging.handlers.TimedRotatingFileHandler(
    # 按照时间切割日志消息
    filename=dirname1,  # 输出位置
    when='midnight',
    interval=1,
    backupCount=7,
    atTime=datetime.time(),
    encoding='utf-8'
)

handlerToFileError = logging.FileHandler(
    filename=dirname2,
    encoding='utf-8'
)
