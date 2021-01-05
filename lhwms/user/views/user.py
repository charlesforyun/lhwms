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

from user.models import User
from user.models import Group

from lhwms import operator
from lhwms.operator import reader
from lhwms.operator import importer

from lhwms.settings import PASSWORD_FIRST

from .common import export_fields
from .common import import_fields
from .common import change
from .common import join_fields

from user.errors import *
from log.views import errlog

from django.db import connection
from django.db import transaction

MASTER_MODEL = User
MASTER_NAME = '用户'


#@cache_page(12 * 3600)
def user(request): 
    '''加载用户管理页面'''
    try: 
        return render(request, 'user.html')

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
def upload_excel(request): 
    '''上传EXCEL导入用户数据'''
    try: 
        model = MASTER_MODEL
        query_mark = MASTER_NAME
        file = request.FILES.get('file_upload')
        fields_import = import_fields[MASTER_MODEL.__name__]
        joins = join_fields[MASTER_MODEL.__name__]

        result = importer.read_excel(request, model, query_mark, 
            file, fields_import, joins)
        return HttpResponse(result)

    except Exception as e: 
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}
        return HttpResponse(json.dumps(info_back))


@require_POST
def import_data(request): 
    '''执行工厂数据导入'''
    try: 
        model = MASTER_MODEL
        query_mark = MASTER_NAME
        fields_import = import_fields[MASTER_MODEL.__name__]

        res = importer.import_rows(request, model, query_mark, fields_import)
        
        context = (MASTER_NAME, res['insert'], MASTER_NAME, res['update'])
        msg = '操作成功！新增%s %d 个，更新%s %d 个。' % context
        info_back = {'type': 1, 'msg': msg}

    except Exception as e: 
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}

    finally: 
        return HttpResponse(json.dumps(info_back))


def down_excel_template(request): 
    '''下载EXCEL数据导入模板'''
    try: 
        fields_import = import_fields[MASTER_MODEL.__name__]
        response = importer.get_template(request, fields_import)
        return response

    except Exception as e: 
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}
        return HttpResponse(json.dumps(info_back))


@require_POST
def delete(request): 
    '''删除用户'''
    response = change(request, MASTER_MODEL, 'is_visible', False, '删除', MASTER_NAME)
    return response


@require_POST
def allow(request): 
    '''启用用户'''
    response = change(request, MASTER_MODEL, 'is_enable', True, '启用', MASTER_NAME)
    return response


@require_POST
def forbid(request): 
    '''禁用用户'''
    response = change(request, MASTER_MODEL, 'is_enable', False, '禁用', MASTER_NAME)
    return response


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




@require_POST
def add(request):
    '''新增用户'''
    try:
        rp = request.POST
        # 检查用户名是否重复
        mods = MASTER_MODEL.objects.filter(user_name=rp['user_name'], is_visible=True)
        if len(mods):
            raise User_exist_err
        
        # 写入用户信息
        new_user = MASTER_MODEL()
        new_user.user_name = rp['user_name']
        new_user.real_name = rp['real_name']
        group = Group.objects.get(group_name=rp['group_name'])
        new_user.group = group
        new_user.department = rp.get('department','')
        new_user.tel = rp.get('tel','')
        new_user.password = PASSWORD_FIRST
        new_user.save()

        # 成功信息
        msg = '操作成功！已成功添加用户"%s"。' % new_user.user_name
        info_back = {'type':1, 'msg':msg}
        return HttpResponse(json.dumps(info_back))

    except Exception as e:
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}
        return HttpResponse(json.dumps(info_back))


@require_POST
def edit(request):
    '''修改用户'''
    try:
        rp = request.POST
        # 检查用户名是否重复
        mods = MASTER_MODEL.objects.filter(user_name=rp['user_name'], is_visible=True)
        if len(mods) and mods[0].id != int(rp['id']):
            raise User_exist_err

        # 写入用户信息
        new_user = MASTER_MODEL.objects.get(id=rp['id'])
        old_user_name = new_user.user_name
        new_user.user_name = rp['user_name']
        new_user.real_name = rp['real_name']
        group = Group.objects.get(group_name=rp['group_name'])
        new_user.group = group
        new_user.department = rp.get('department', '')
        new_user.tel = rp.get('tel', '')
        new_user.save()

        # 关联修改凭证用户名
        cursor = connection.cursor()
        sql = '''UPDATE cashier_cer SET creater_user_name="%s" 
        WHERE creater_user_name="%s"''' % (rp['user_name'], old_user_name)
        cursor.execute(sql)
        connection.commit()
        cursor.close()

        # 成功信息
        msg = '操作成功！已成功修改用户"%s"。' % new_user.user_name
        info_back = {'type':1, 'msg':msg}
        return HttpResponse(json.dumps(info_back))
        
    except Exception as e:
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}
        return HttpResponse(json.dumps(info_back))


@require_POST
def set_password(request):
    '''修改用户密码'''
    try:
        rp = request.POST
        ui = request.session['user_info']
        pwd_old_h = rp['pwd_old_h']
        pwd_new_h = rp['pwd_new_h']

        user = User.objects.get(id=ui['id'])
        if pwd_old_h != user.password:
            raise Old_password_err
        user.password = pwd_new_h
        user.save()

        msg = '操作成功！已成功修改用户 %s 的密码。' % user.user_name
        info_back = {'type':1, 'msg':msg}

    except Exception as e:
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type':3, 'msg':msg}

    finally:
        return HttpResponse(json.dumps(info_back))


@require_POST
def reset_password(request):
    '''重置用户密码'''
    response = change(request, MASTER_MODEL, 'password', PASSWORD_FIRST, '重置', MASTER_NAME)
    return response