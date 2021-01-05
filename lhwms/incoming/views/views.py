from django.views import View
from incoming.models import IncomingApply
from user.models import User
from lhwms.utils import restful
from lhwms.utils import attachment, data_search
from django.views.decorators.http import require_POST
import json
from django.http import HttpResponse
from django.db import connection
from log.views.publicLog import log_print, errlog_add
from log.views import publicLog

INCOMING_MODEL = IncomingApply  # 全局模型用于定位查询和分页缓存
INCOMING_NAME = '入库查询'  # 全局query_mark定位


class IncomingApplyCreator(View):
    """
    创建录入表单
    """

    def get(self, request):
        """
        入库数据、分页展示
        :param filter: 查询条件
        :return: json
        """
        # terms = {'is_enable': True, 'supplyer': 'sdfsdf'}
        #
        # reader.search(request, IncomingApply, '入库查询', terms, )
        # data = reader.load(request, IncomingApply, '入库查询', 50, 10)
        # filter = request.GET.get('filter')
        terms = {'id': 1}  # 处理这个就行了,使用任意关键字实参完成条件查询
        if terms == {}:
            data = IncomingApply.objects.all().values('id').order_by('id')
        else:
            # 所有的方式：模糊查询like
            data = IncomingApply.objects.filter(
                mat_extend_mark__icontains='SD'). \
                values('id', 'user__user_name').order_by('id')
        print(type(data))
        print('*' * 30)
        print(connection.queries)
        # print(data2)
        return HttpResponse('ok')

    def post(self, request):
        """
        创建录入表单，
        :param request:
        :return: json
        """
        incoming_doc_mark = request.POST.get('incoming_doc_mark')  # 入库申请(单)编号
        stock_mark = request.POST.get('stock_mark')  # 存放编号
        # user =
        user_id = User.objects.get(pk=1)

        apply_cons_mark = request.POST.get('apply_cons_mark')  # 申请施工单位代码/入库申请单位
        asset_name = request.POST.get('asset_name')  # 资产名称
        proj_from = request.POST.get('proj_from')  # 物资来源
        proj_mark = request.POST.get('proj_mark')  # 工程编号(选填)
        proj_name = request.POST.get('proj_name')  # 项目名称
        ini_from = request.POST.get('ini_from')  # 详细来源(选填)(选填)

        mat_mark = request.POST.get('mat_mark')  # 物料编码
        mat_extend_mark = request.POST.get('mat_extend_mark')  # 物料扩展码(选填)
        mat_from = request.POST.get('mat_from')  # 物料描述(选填)
        pars = request.POST.get('pars')  # 规格型号
        mat_type = request.POST.get('mat_type')  # 物资类型

        dp = request.POST.get('dp')  # 生产日期(选填)
        supplyer = request.POST.get('supplyer')  # 厂家(选填)
        bp = request.POST.get('bp')  # 出厂编号(选填)
        use_date = request.POST.get('use_date')  # 投运日期
        remove_date = request.POST.get('remove_date')  # 拆除日期
        pms_status = request.POST.get('pms_status')  # PMS台账情况(选填)
        test_result = request.POST.get('test_result')  # 试验结果

        wh_mark = request.POST.get('wh_mark')  # 仓库代码(拟入仓库名称)
        num = request.POST.get('num')  # 入库数量

        is_approve_reason = request.POST.get('is_approve_reason')
        is_visible = request.POST.get('is_visible')

        incoming_apply_file = IncomingApply(
            user=user_id,
            incoming_doc_mark=incoming_doc_mark,
            stock_mark=stock_mark,
            apply_cons_mark=apply_cons_mark,
            asset_name=asset_name,
            proj_from=proj_from,
            proj_mark=proj_mark,
            proj_name=proj_name,
            ini_from=ini_from,
            mat_mark=mat_mark,
            mat_extend_mark=mat_extend_mark,
            mat_from=mat_from,
            mat_type=mat_type,
            pars=pars,
            dp=dp,
            supplyer=supplyer,
            bp=bp,
            use_date=use_date,
            remove_date=remove_date,
            pms_status=pms_status,
            test_result=test_result,
            wh_mark=wh_mark,
            num=num,
            is_approve_reason=is_approve_reason,
        )
        incoming_apply_file.save()
        return restful.ok(data='创建入库申请单成功！')


@require_POST
def incoming_search_data(request):
    try:
        # 条件查询数据，保存到缓存中，并实现page=1分页展示
        # {'mat_extend_mark': 'Sd'} <class 'dict'>
        values = ('id', 'user__user_name')  # 需要展示的值：.value(内容)
        # 查询数据并且缓存
        data_search.data_search(request, INCOMING_MODEL, INCOMING_NAME, values)
        # 首页分页
        data = data_search.data_paginator(request, INCOMING_MODEL, INCOMING_NAME,)
        return restful.ok(data=data)
    except Exception as e:
        log_print(excepts=e)
        errlog_add(request, e.__str__())
        return restful.server_error(message=e.__str__())


def incoming_paginator_data(request):
    # 条件查询数据，保存到缓存中，并实现分页展示, 关键参数，rc_key
    data = data_search.data_paginator(request, INCOMING_MODEL, INCOMING_NAME,)
    return data


@require_POST
def incoming_apply_delete(request):
    """删除入库申请单"""
    pk = request.POST.get('pk')  # 获取当前对象pk值
    try:
        delete_incoming_apply = IncomingApply.objects.get(pk=pk)  # 获取需要修改的表
    except:
        return restful.un_auth(data='数据不存在，或者查询错误！')
    permission_enable = delete_incoming_apply.is_enable
    permission_visible = delete_incoming_apply.is_visible
    if permission_enable is True or permission_visible is True:
        return restful.ok(data='您无权限执行此操作！该入库单已通过申请或者已提交')
    else:
        delete_incoming_apply.delete()
        return restful.ok(data='入库申请单已删除！')


@require_POST
def incoming_apply_update(request):
    """更新入库申请单（前端选中一条数据，返回pk值）"""
    pk = request.POST.get('pk')  # 获取当前对象pk值
    update_incoming_apply = IncomingApply.objects.filter(pk=pk)  # 获取需要修改的表

    incoming_doc_mark = request.POST.get('incoming_doc_mark')  # 入库申请(单)编号
    stock_mark = request.POST.get('stock_mark')  # 存放编号

    apply_cons_mark = request.POST.get('apply_cons_mark')  # 申请施工单位代码/入库申请单位
    asset_name = request.POST.get('asset_name')  # 资产名称
    proj_from = request.POST.get('proj_from')  # 物资来源
    proj_mark = request.POST.get('proj_mark')  # 工程编号(选填)
    proj_name = request.POST.get('proj_name')  # 项目名称
    ini_from = request.POST.get('ini_from')  # 详细来源(选填)(选填)

    mat_mark = request.POST.get('mat_mark')  # 物料编码
    mat_extend_mark = request.POST.get('mat_extend_mark')  # 物料扩展码(选填)
    mat_from = request.POST.get('mat_from')  # 物料描述(选填)
    pars = request.POST.get('pars')  # 规格型号
    mat_type = request.POST.get('mat_type')  # 物资类型

    dp = request.POST.get('dp')  # 生产日期(选填)
    supplyer = request.POST.get('supplyer')  # 厂家(选填)
    bp = request.POST.get('bp')  # 出厂编号(选填)
    use_date = request.POST.get('use_date')  # 投运日期
    remove_date = request.POST.get('remove_date')  # 拆除日期
    pms_status = request.POST.get('pms_status')  # PMS台账情况(选填)
    test_result = request.POST.get('test_result')  # 试验结果

    wh_mark = request.POST.get('wh_mark')  # 仓库代码(拟入仓库名称)
    num = request.POST.get('num')  # 入库数量

    update_incoming_apply.update(
        incoming_doc_mark=incoming_doc_mark,
        stock_mark=stock_mark,
        apply_cons_mark=apply_cons_mark,
        asset_name=asset_name,
        proj_from=proj_from,
        proj_mark=proj_mark,
        proj_name=proj_name,
        ini_from=ini_from,
        mat_mark=mat_mark,
        mat_extend_mark=mat_extend_mark,
        mat_from=mat_from,
        mat_type=mat_type,
        pars=pars,
        dp=dp,
        supplyer=supplyer,
        bp=bp,
        use_date=use_date,
        remove_date=remove_date,
        pms_status=pms_status,
        test_result=test_result,
        wh_mark=wh_mark,
        num=num
    )
    return restful.ok(data='入库申请单修改成功！')


@require_POST
def incoming_apply_submit(request):
    """提交申请"""
    pk = json.loads(request.POST['pk'])  # {'1': 'df', '2': 'ds'} <class 'dict'>
    pk1 = request.POST.get('pk')  # {"1": "df", "2": "ds"} <class 'str'>
    name = request.POST.get('name')

    print(pk, type(pk))
    print(pk1, type(pk1))
    print(type(name), type(request.POST), request.POST)

    submit_incoming_apply = IncomingApply.objects.filter(pk='1')
    submit_incoming_apply.update(is_visible=True, num='44.6')
    return restful.ok(data='提交成功！')


@require_POST
def incoming_apply_approve(request):
    """
    审批和驳回
    :param request: pk,approve,
    :return:
    """
    pk = request.POST.get('pk')
    approve_submit = request.POST.get('approve')
    reject_submit = request.POST.get('reject')
    submit_incoming_apply = IncomingApply.objects.filter(pk=pk)

    if approve_submit is True:
        submit_incoming_apply.update(is_enable=True)
        return restful.ok(data='审批通过')


@require_POST
def incoming_accessory_uploading(request):
    """附件上传操作"""
    data = attachment.attachment_uploading(request, model=IncomingApply)
    return restful.ok(data)


@require_POST
def incoming_accessory_delete(request):
    """附件删除操作 先删文件，在删数据库"""
    data = attachment.attachment_delete(request)
    return restful.ok(data)


@require_POST
def incoming_accessory_download(request):
    """B端附件下载"""
    response = attachment.attachment_download(request)
    return response



