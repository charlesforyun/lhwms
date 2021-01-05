import json
from lhwms.utils import restful

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from user.models import *

from lhwms import operator
from lhwms.operator import reader
from lhwms.operator import importer

from .common import export_fields
from .common import import_fields
from .common import change
from .common import join_fields

from user.errors import *
from log.views import errlog

MASTER_MODEL = Group
MASTER_NAME = '角色'


# @cache_page(12 * 3600)
def group(request):
    '''加载角色管理页面'''
    try:
        return render(request, 'group.html')

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

        response = reader.export_excel(request, model, query_mark,
                                       fields_export, joins)
        return response

    except Exception as e:
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}
        return HttpResponse(json.dumps(info_back))


@require_POST
def upload_excel(request):
    '''上传EXCEL导入角色数据'''
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
        message = '操作成功！新增%s %d 个，更新%s %d 个。' % context
        code = 1

    except Exception as e:
        errlog.errlog_add(request, str(e))
        message = '操作失败！错误：%s。' % str(e)
        code = 3

    finally:
        return restful.result(code=code, message=message)


def down_excel_template(request):
    '''下载EXCEL数据导入模板'''
    try:
        fields_import = import_fields[MASTER_MODEL.__name__]
        response = importer.get_template(request, fields_import)
        return response

    except Exception as e:
        errlog.errlog_add(request, str(e))
        message = '操作失败！错误：%s。' % str(e)
        code = 3
        return restful.result(code=code, message=message)


@require_POST
def delete(request):
    '''删除角色'''
    response = change(request, MASTER_MODEL, 'is_visible', False, '删除',
                      MASTER_NAME)
    return response


@require_POST
def allow(request):
    '''启用角色'''
    response = change(request, MASTER_MODEL, 'is_enable', True, '启用',
                      MASTER_NAME)
    return response


@require_POST
def forbid(request):
    '''禁用角色'''
    response = change(request, MASTER_MODEL, 'is_enable', False, '禁用',
                      MASTER_NAME)
    return response


@require_POST
def clean_querys(request):
    '''清理缓存'''
    try:
        model = MASTER_MODEL
        query_mark = MASTER_NAME
        operator.clean_querys(request, model, query_mark)
        message = '操作成功！已成功执行缓存清理操作。'
        code = 1
        return restful.result(code=code, message=message)

    except Exception as e:
        errlog.errlog_add(request, str(e))
        message = '操作失败！错误：%s。' % str(e)
        code = 3
        return restful.result(code=code, message=message)


@require_POST
def add(request):
    '''新增角色'''
    try:
        rp = request.POST
        # 检查角色名是否重复
        mods = MASTER_MODEL.objects.filter(group_name=rp['group_name'],
                                           is_visible=True)
        if len(mods):
            raise Group_exist_err
        # 写入角色信息
        new_group = MASTER_MODEL()
        new_group.group_name = rp['group_name']
        new_group.permission_account = str(rp['permission_account'])
        new_group.permission_moudle = str(rp['permission_moudle'])
        if int(rp.get('permission_edit_master', 0)):
            new_group.permission_edit_master = True
        else:
            new_group.permission_edit_master = False
        new_group.save()

        # 成功信息
        msg = '操作成功！已成功添加角色"%s"。' % new_group.group_name
        info_back = {'type': 1, 'msg': msg}
        return HttpResponse(json.dumps(info_back))

    except Exception as e:
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}
        return HttpResponse(json.dumps(info_back))


@require_POST
def edit(request):
    '''修改角色'''
    try:
        rp = request.POST
        # 检查角色名是否重复
        mods = MASTER_MODEL.objects.filter(id=rp['id'], is_visible=True)
        if len(mods) and mods[0].id != int(rp['id']):
            raise Group_exist_err

        # 写入角色信息
        new_group = MASTER_MODEL.objects.get(id=rp['id'])
        new_group.group_name = rp['group_name']
        new_group.permission_account = str(rp['permission_account'])
        new_group.permission_moudle = str(rp['permission_moudle'])
        if int(rp.get('permission_edit_master', 0)):
            new_group.permission_edit_master = True
        else:
            new_group.permission_edit_master = False
        new_group.save()

        # 成功信息
        msg = '操作成功！已成功修改角色"%s"。' % new_group.group_name
        info_back = {'type': 1, 'msg': msg}
        return HttpResponse(json.dumps(info_back))

    except Exception as e:
        errlog.errlog_add(request, str(e))
        msg = '操作失败！错误：%s。' % str(e)
        info_back = {'type': 3, 'msg': msg}
        return HttpResponse(json.dumps(info_back))


def lists(request):
    '''获得分组列表'''
    try:
        groups = Group.objects.filter(is_visible=True)
        li = []
        for g in groups:
            li.append({'id': g.id, 'text': g.group_name})
        return HttpResponse(json.dumps(li))

    except Exception as e:
        errlog.errlog_add(request, str(e))
        return HttpResponse(str(e))
