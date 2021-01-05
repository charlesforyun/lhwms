from . import *
from datetime import datetime, date
import json
import traceback
import redis

from lhwms.utils import restful
from log.views.publicLog import log_print, errlog_add

from django.core.paginator import Paginator, Page
from django.core.serializers.json import DjangoJSONEncoder

'''
==================================================
公用函数：数据ORM条件查询
==================================================
'''


def data_search(request, model, query_mark, values=(), order=('id',),
                check_acc=True, fun_check=None, **kwargs):
    """:前端传递值:'terms'-->dict(), if 'terms'=None，全部查询。
    (根据orm模型转化条件查询,缓存到redis中一天)
    核心语句：redis.set(model + query_mark) = model. /
    objects.filter(**(terms+kwargs)).values(*values).order_by(*order)
    :param model: 被查询模型名称
    :param query_mark:-->str: 模块名称 + model = rc_key(是缓存后的数据)
    :param values: -->tuple of model's keys
    :param order:-->tuple: 排列顺序order_by() model's key
    :param check_acc:
    :param fun_check:
    :param kwargs:其他查询条件。 {'mat_extend_mark': 'Sd'}
    :return: Return the True if redis.set() is ok
    """
    rc_search_result = redis.Redis(connection_pool=pool_result)  # 连接redis池
    rc_key = get_key(request, model, query_mark)  # 生成redis key值
    # terms = {'mat_extend_mark': 'Sd'},使用任意关键字实参完成条件查询
    if request.POST.get('terms'):  # 判断前端传递条件与否？
        terms = json.loads(request.POST.get('terms'))
    else:
        terms = {}

    new_terms = {}
    # 建立id__icontains拼接
    for key, value in terms.items():
        new_terms[key + '__icontains'] = value

    if kwargs:  # 判断是否有其他条件语句
        new_terms.update(kwargs)

    # 默认是模糊查询icontains
    data = model.objects.filter(**new_terms).values(*values). \
        order_by(*order)
    rc_search_result.set(rc_key, json.dumps(list(data), cls=DjangoJSONEncoder),
                         ex=60 * 60 * 12)  # 结果缓存1天到redis中
    return True  # 对查询到的数据分页


def data_paginator(request, model, query_mark, paginator_page=2, num=2):
    """:前端传递值: 'page'-->int:页码数; 默认page=1
    (json数据分页接口)
    :param model:-->model :被分页数据原始模型名称
    :param query_mark:-->str : 模块名称
    :param paginator_page：每页需要展示的数据个数;
    :param num：int-->页码两边需要展示的页码数量;
    :return: Return JsonResponse of paginator data, or message of str
    if redis.key is None
    """
    try:
        # 判断前端是否传值，没有默认为page=1
        if request.GET.get('page'):
            page = int(request.GET.get('page'))
        else:
            page = 1

        rc_search_result = redis.Redis(connection_pool=pool_result)  # 连接redis池
        rc_key = get_key(request, model, query_mark)  # 获取redis key
        if rc_search_result.get(rc_key) is None:  # 判断是否有key值
            return restful.ok(message='缓存过期，请重新查询！')
        else:
            data = json.loads(rc_search_result.get(rc_key))
            paginator_page = paginator_page  # 每页需要展示的数据个数
            num = num  # 需要两边展示的页码数量

            paginator = Paginator(data, paginator_page)  # 数据分组

            data_sum = paginator.count  # 所有数据个数
            page_sum = paginator.num_pages  # 所有数据页数

            current_page_data = paginator.page(page)  # 获取当前页数据对象
            has_next_page = current_page_data.has_next()  # 是否有下一页
            has_previous_page = current_page_data.has_previous()  # 是否有上一页

            if page <= page_sum - num - 2:
                """判断左右两边存在合并情况"""
                right_has_more = True  # 1...234..
                right_pages = list(range(page + 1, page + num + 1))
            else:
                """89, 789格式"""
                right_has_more = False
                right_pages = list(range(page + 1, page_sum + 1))

            if page >= num + 3:
                """...234...12"""
                left_has_more = True
                left_pages = list((page - num, page))
            else:
                left_has_more = False
                left_pages = list(range(1, page))

            if page != 1:
                previous_page_number = current_page_data.previous_page_number()
            else:
                previous_page_number = 1

            if page != page_sum:
                next_page_number = current_page_data.next_page_number()
            else:
                next_page_number = page_sum

            pa_data = {
                # 获取当前页数据(queryset)
                'current_page_data': list(current_page_data.object_list),
                'current_page': page,  # 选中页码
                'data_sum': data_sum,  # 所有数据个数
                'page_sum': page_sum,  # 所有数据页数
                'has_next': has_next_page,  # 是否存在下一页
                'has_previous': has_previous_page,
                'right_pages': right_pages,  # 右边额外展示的页码list
                'left_pages': left_pages,
                'previous_page_number': previous_page_number,  # 点击上一页返回页面id
                'next_page_number': next_page_number,  # 点击下一页返回页面id
                'right_has_more': right_has_more,
                'left_has_more': left_has_more,
            }
            return restful.ok(message='读取成功！', data=pa_data)
    except Exception as e:
        log_print(waring=traceback.format_exc())  # 返回异常堆栈信息到日志中,e是异常类
        errlog_add(request, e.__str__())  # 异常保存到数据库
        return restful.server_error(message=e.__str__())


class JsonToDatetime(json.JSONEncoder):
    """
    str,int,list,tuple,dict,bool,None这些数据类型都支撑json序列化操作。
    但是datetime类型不支持json序列化，我们可以自定义datetime的序列化。
    JSONEncoder不知道怎么去把这个数据转换成json字符串的时候，
    它就会调用default()函数，default()函数默认会抛出异常。
    所以，重写default()函数来处理datetime类型的数据。
    json.dumps(list(data), cls=DjangoJSONEncoder)django自带了
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H: %M: %S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)