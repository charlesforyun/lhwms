import json
import datetime
import re

from django.http import HttpResponse
from django.http import FileResponse
from django.shortcuts import render
from django.contrib.sessions.models import Session
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST

from log.models import Loginlog

from lhwms import operator
from lhwms.operator import reader

from .common import export_fields
from .common import join_fields

from log.views import errlog


MASTER_MODEL = Loginlog
MASTER_NAME = '系统登录日志'


@cache_page(12 * 3600) 
def loginlog(request): 
    '''加载系统登录日志管理页面'''
    try: 
        return render(request, 'loginlog.html')

    except Exception as e: 
        errlog.errlog_add(request, str(e))
        return HttpResponse(str(e))


def search_data(request): 
    '''根据条件查询数据'''
    try: 
        model = MASTER_MODEL
        query_mark = MASTER_NAME
        check_acc = False
        fun_check = None
        where = None
        joins = join_fields[MASTER_MODEL.__name__]

        reader.search(request, model, query_mark, request.POST, 
            check_acc, fun_check, where, joins)
        
        msg = '操作成功！已成功执行数据查询操作。'
        info_back = {'type': 1, 'msg': msg}

    except Exception as e: 
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}

    finally: 
        return HttpResponse(json.dumps(info_back))


def load_data(request): 
    '''获取分页数据'''
    try: 
        model = MASTER_MODEL
        query_mark = MASTER_NAME
        page_num = int(request.GET['page'])
        row_num = int(request.GET['rows'])
        joins = join_fields[MASTER_MODEL.__name__]

        data = reader.load(request, model, query_mark, page_num, row_num, joins)
        return HttpResponse(data)

    except Exception as e: 
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}
        return HttpResponse(json.dumps(info_back))


def export_excel(request): 
    '''导出EXCEL'''
    try: 
        model = MASTER_MODEL
        query_mark = MASTER_NAME
        fields_export = export_fields[MASTER_MODEL.__name__]
        joins = join_fields[MASTER_MODEL.__name__]

        response = reader.export_excel(request, model, query_mark, fields_export, joins)
        return response
        
    except Exception as e: 
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}
        return HttpResponse(json.dumps(info_back))


@require_POST
def clean_querys(request): 
    '''清理缓存'''
    try:
        model = MASTER_MODEL
        query_mark = MASTER_NAME
        operator.clean_querys(request, model, query_mark)
        msg = '操作成功！已成功执行缓存清理操作。'
        info_back = {'type': 1, 'msg': msg}

    except Exception as e:
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}
        return HttpResponse(json.dumps(info_back))


def loginlog_add(request):
    '''添加登陆日志'''
    try:
        log = Loginlog()
        log.user_id = request.session['user_info']['id']
        rip = request.META.get('HTTP_X_FORWARDED_FOR')
        if not rip:
            rip = request.META.get("REMOTE_ADDR")
        log.login_ip = rip
        log.login_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.save()
    except Exception as e:
        errlog.errlog_add(request, str(e))