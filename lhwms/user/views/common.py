from lhwms.utils import restful

from lhwms.operator import *
from lhwms.operator.reader import ExportField
from lhwms.operator.importer import ImportField

from log.views import errlog


# =======================================================
# 公用函数
# =======================================================

def change(request, model, field, value, opname, mname):
    '''修改条目状态通用方法
    change(request, MASTER_MODEL, 'is_enable', True, '启用', MASTER_NAME)
    '''
    try:
        # 解析并去重上传的id
        data = json.loads(request.POST['ids'])
        ids = set(data)  # 无序不重复集合

        # 修改条目
        for n in ids:
            g = model.objects.get(id=int(n))
            if g is not None:
                setattr(g, field, value)
                g.save()

        # 成功信息
        message = '操作成功！已成功%s %s 个%s。' % (opname, len(ids), mname)
        code = 1

    except Exception as e:
        errlog.errlog_add(request, str(e))
        message = '操作失败！错误：%s。' % str(e)
        code = 3

    finally:
        return restful.result(code=code, message=message)


# =======================================================
# Group 供应计划字段
# =======================================================

fields_export_supplyplan = [
    ExportField('group_name', '角色名'),
    ExportField('permission_account', '账套权限', 50),
    ExportField('permission_moudle', '模块权限', 50),
    ExportField('permission_edit_master', '主数据编辑'),
    ExportField('is_enable', '启用', 10),
]

fields_import_supplyplan = [
    ImportField('group_name', True, False, '角色名', '^(.*){1,16}$', 's'),
    ImportField('permission_account', False, False, '账套权限', '^(.*){1,512}$',
                's'),
    ImportField('permission_moudle', False, False, '模块权限', '^(.*){1,512}$',
                's'),
    ImportField('permission_edit_master', False, False, '主数据编辑', '^(.*){0,5}$',
                's'),
]

fields_join_supplyplan = []

# =======================================================
# User 物料字段
# =======================================================

fields_export_material = [
    ExportField('user_name', '用户名'),
    ExportField('real_name', '真实姓名'),
    ExportField('group_name', '用户角色'),
    ExportField('department', '所属部门'),
    ExportField('tel', '联系方式', 40),
    ExportField('is_enable', '启用', 10),
]

fields_import_material = [
    ImportField('user_name', True, False, '用户名', '^(.*){1,16}$', 's'),
    ImportField('real_name', True, False, '真实姓名', '^(.*){1,16}$', 's'),
    ImportField('group_name', False, True, '用户角色', '^(.*){1,16}$', 's'),
    ImportField('department', False, True, '所属部门', '^(.*){0,32}$', 's'),
    ImportField('tel', False, False, '联系方式', '^(.*){0,32}$', 's'),
]

fields_join_material = [
    {'join_model': Group, 'join_model_name': '角色',
     'fields': [{'from': 'group_id', 'to': 'id'}]},
]

export_fields = {
    'Group': fields_export_supplyplan,
    'User': fields_export_material,
}

import_fields = {
    'Group': fields_import_supplyplan,
    'User': fields_import_material,
}

join_fields = {
    'Group': fields_join_supplyplan,
    'User': fields_join_material,
}
