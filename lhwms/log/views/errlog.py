import datetime

from django.views.decorators.http import require_POST

from lhwms.utils import data_search, restful, attachment
from lhwms import utils

from log.views.publicLog import log_print, errlog_add
from log.models import Errlog

from django.utils import timezone
from django.db import connection
from django.http import HttpResponse

from .common import errorLog_values, errorLog_sheetHeadData

MASTER_MODEL = Errlog
MASTER_NAME = '系统异常日志'  # 作为rc定位key值、excel临时文件名称


def search_data(request):
    '''
    根据条件查询数据,并获取第一页数据
    example：terms={'id': 79},values=('id', 'path', 'error'))
    :return data=data_paginator()
    '''

    try:
        model = MASTER_MODEL
        query_mark = MASTER_NAME

        today_time = datetime.datetime.today()
        start_time = datetime.datetime(today_time.year, today_time.month, 1)
        time_range = (start_time, today_time)
        kwargs = {'err_time__range': time_range}  # 查询一个月内的数据

        check_acc = False
        fun_check = None
        # 默认查询所有数据， 使用时间从新到旧方式排序
        data_search.data_search(request, model, query_mark=query_mark,
                                values=errorLog_values, order=('-id',),
                                **kwargs)
        # 分页后第一页数据返回
        data = data_search.data_paginator(request, model, query_mark)
        return data

    except Exception as e:
        log_print(error=e.__str__())
        errlog_add(request, e.__str__())
        return restful.server_error(message=e.__str__())


def load_data(request):
    '''获取分页数据'''
    try:
        model = MASTER_MODEL
        query_mark = MASTER_NAME
        # 返回分页数据
        data = data_search.data_paginator(request, model=model,
                                          query_mark=query_mark)
        return data
    except Exception as e:
        log_print(error=e.__str__())
        errlog_add(request, e.__str__())
        return restful.server_error(message=e.__str__())


def export_excel(request):
    '''导出EXCEL'''
    try:
        model = MASTER_MODEL
        query_mark = MASTER_NAME
        filename = MASTER_NAME + '.xlsx'

        response = attachment.export_excel(
            request,
            model=model,
            query_mark=query_mark,
            filename=filename,
            sheet_name='2020',
            sheet_head_data=errorLog_sheetHeadData
        )
        return response

    except Exception as e:
        log_print(e.__str__())
        errlog_add(request, e.__str__())
        msg = '操作失败！错误：%s。' % e.__str__()
        return restful.server_error(message=msg)


@require_POST
def clean_querys(request):
    '''清理全部缓存'''
    try:
        model = MASTER_MODEL
        query_mark = MASTER_NAME
        utils.clean_querys(request, model, query_mark)
        msg = '操作成功！已成功执行缓存清理操作。'
        return restful.ok(message=msg)

    except Exception as e:
        log_print(error=e.__str__())  # 保存日志到文件
        errlog_add(request, e.__str__())  # 保存日志到数据库
        msg = '操作失败！错误：%s。' % e.__str__()
        return restful.server_error(message=msg)
