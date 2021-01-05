import logging.handlers
from log import views
import datetime
from log.models import Errlog
"""
#####################
公共函数，
#####################
logger = logger
日志处理模块，分为时间file切割debug， 用户file:error
logger name='lhwms'
logger.setLever
handler name='handlerToFileAll'
handler class = logging.handlers.TimedRotatingFileHandler()
handler.setFormatter
handler.setLever
"""


def log_print(excepts=None, debug=None, info=None,
              waring=None, error=None, critical=None):
    """
   日志打印
    :param excepts:异常信息传值
    :param debug:
    :param info:
    :param waring:
    :param error:
    :param critical:
    :return: file
    """
    try:
        logger = views.logger
        logger.setLevel(logging.DEBUG)  # logger默认为全部输出

        handlerToFileAll = views.handlerToFileAll
        handlerToFileAll.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d]- %(message)s'
        ))  # 对管理器输出格式化

        handlerToFileError = views.handlerToFileError
        handlerToFileError.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d]- %(message)s'
        ))
        handlerToFileError.setLevel(logging.ERROR)  # 管理器级别为error

        # handlers添加到logger中，进行目的要求输出
        logger.addHandler(handlerToFileAll)
        logger.addHandler(handlerToFileError)

        if excepts is not None:
            logger.exception(excepts)  # 打印日志,error,tracback
        if debug is not None:
            logger.debug(debug)
        if info is not None:
            logger.info(info)
        if waring is not None:
            logger.warning(waring)
        if error is not None:
            logger.error(error)
        if critical is not None:
            logger.critical(critical)
    except:
        pass


def errlog_add(request, info):
    """
    系统异常日志保存到数据库
    :param request:
    :param info:
    :return: save to mysql
    """
    try:
        new_errlog = Errlog()
        new_errlog.user_id = request.session['user_info']['id']
        new_errlog.path = request.path
        new_errlog.error = info
        new_errlog.err_time = datetime.datetime.now()  # 系统时间datatime
        new_errlog.save()

    except:
        pass