from lhwms.operator import *
from lhwms.operator.reader import ExportField

# =======================================================
# Loginlog 供应计划字段，sheetHeadData列表数据
# =======================================================
fields_export_loginlog = [
    ExportField('user_name', '用户名'),
    ExportField('login_ip', '登录IP', 30),
    ExportField('login_time', '登陆时间', 20),
]

fields_import_loginlog = []

fields_join_loginlog = [{'join_model': User, 'join_model_name': '用户',
                         'fields': [{'from': 'user_id', 'to': 'id'}]}, ]

# =======================================================
# Syslog 物料字段，sheetHeadData等数据
# =======================================================

fields_export_syslog = [
    ExportField('user_name', '用户名'),
    ExportField('moudle_name', '功能模块'),
    ExportField('action', '操作'),
    ExportField('do_time', '执行时间', 20),
]

fields_import_syslog = []

fields_join_syslog = [{'join_model': User, 'join_model_name': '用户',
                       'fields': [{'from': 'user_id', 'to': 'id'}]}, ]

# =======================================================
# ErrLog 库区字段 ,sheetHeadData等数据
# author: Charles
# =======================================================
errorLog_sheetHeadData = {
    # sheet第一行head名、列宽值
    '序号': 6,  # 单独设置
    '产生路径': 20,  # 与errorLog_values对应上path
    '异常描述': 20,
    '产生时间': 20,
    '使用者': 20
}
# 数据查询显示值，对应sheetHeadData
errorLog_values = ('path', 'error', 'err_time', 'user__user_name')

# 默认展示一周数据

# ==================================================================
fields_export_errlog = [
    ExportField('user_name', '用户名'),
    ExportField('path', '路径', 40),
    ExportField('error', '异常描述', 40),
    ExportField('err_time', '产生时间', 20),
]

fields_import_errlog = []

fields_join_errlog = [{'join_model': User, 'join_model_name': '用户',
                       'fields': [{'from': 'user_id', 'to': 'id'}]}, ]

export_fields = {
    'Loginlog': fields_export_loginlog,
    'Syslog': fields_export_syslog,
    'Errlog': fields_export_errlog,
}

import_fields = {
    'Loginlog': fields_import_loginlog,
    'Syslog': fields_import_syslog,
    'Errlog': fields_import_errlog,
}

join_fields = {
    'Loginlog': fields_join_loginlog,
    'Syslog': fields_join_syslog,
    'Errlog': fields_join_errlog,
}
