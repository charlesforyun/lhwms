'''
六合测试样例
'''
import requests
import json
import os
import datetime
import sys

# from log.models import Errlog
# from log.views.publicLog import log_print
sys.setrecursionlimit(1000000)

root = 'http://127.0.0.1:8000/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def datagrid_search_load_test():
    '''页面数据列表查询和加载测试'''
    url_search = root + 'master/constructor/search_data'
    url_load = root + 'master/constructor/load_data'

    params = {'cons_name': '聚联'}
    r = requests.post(url_search, data=params)
    # print(r.status_code, r.text)
    params = {'page': '1', 'rows': '50'}
    r = requests.get(url_load, params=params)
    # jr = json.loads(r.text)
    print(r.status_code, r.json())


def allow_forbid_test():
    '''启用/禁用接口测试'''
    url = root + 'master/constructor/allow'

    params = {'ids': '[1, 2]'}
    r = requests.post(url, data=params)
    jr = json.loads(r.text)
    print(r.status_code, jr)


def download_excel_test():
    '''导出数据接口测试'''
    url_search = root + 'master/constructor/search_data'
    url_export = root + 'master/constructor/export_excel'

    params = {'cons_name': ''}
    requests.post(url_search, data=params)

    r = requests.get(url_export)
    filename = os.path.abspath('.') + r'\book.xlsx'
    with open(filename, 'wb') as code:
        code.write(r.content)


def apply_crate_test():
    # (.*?):(.*)   '$1': '$2',
    '''创建申请单测试'''
    url_search = root + 'incoming/apply/creator/'
    data1 = {
        'incoming_doc_mark': '入库申请单编号11',
        'stock_mark': '存放编号',
        'apply_cons_mark': '申请施工单位代码/入库申请单位',
        'asset_name': '资产名称',
        'proj_from': '物资来源',
        'proj_mark': '工程编号(选填)',
        'proj_name': '工程名称',
        'ini_from': '详细来源(选填)',

        'mat_mark': '物料编码',
        'mat_extend_mark': '物料扩展码(选填)',
        'mat_from': '物料描述(选填)',
        'pars': '规格型号',
        'mat_type': '物资类型',

        'dp': datetime.date(2020, 2, 3),  # 生产日期(选填)
        'supplyer': '厂家(选填)',
        'bp': '出厂编号(选填)',
        'use_date': datetime.date(2020, 4, 3),  # 投运日期
        'remove_date': datetime.date(2021, 1, 1),  # 拆除日期
        'pms_status': 'PMS台账情况(选填)',
        'test_result': '试验结果',
        'wh_mark': '仓库代码(拟入仓库名称)',
        'num': 23,  # 入库数量
        'accessory': '1',
    }
    url = BASE_DIR + '/lhwms/media/1.txt'
    r = requests.post(url=url_search, data=data1).json()
    # r = requests.get(url=url_search).json()
    print(r)


def apply_update():
    url_search = root + 'incoming/apply/delete/'
    date = {
        'pk': '15',
        'incoming_doc_mark': '2',
        'stock_mark': '14',
        'apply_cons_mark': '14',
        'asset_name': '14',
        'proj_from': '',
        'proj_mark': '1',
        'proj_name': '1',
        'ini_from': '1',
        'mat_mark': 'sdfsdf',
        'mat_type': '1',
        'pars': '1',
        'dp': None,
        'supplyer': 'sdfsdf',
        'bp': 'sdfsdfs',
        'use_date': datetime.date(2021, 2, 3),
        'remove_date': datetime.date(2021, 2, 3),
        'pms_status': 'sdfsdfs',
        'test_result': 'sdfsdf',
        'wh_mark': 'sdfsdf',
        'num': 23,
        'mat_extend_mark': 'sdfsdf',
        'mat_from': '345',
    }
    r = requests.post(url=url_search, data=date).json()
    print(r)


def apply_submit():
    url_search = root + 'incoming/apply/submit/'
    datas = json.dumps({1: 'df', 2: 'ds'})
    date = {
        'pk': datas,
        'name': 'sdf'

    }
    r = requests.post(url=url_search, data=date).json()
    print(r, type(r))


def apply_show():
    # 数据是分页展示
    url_serach = root + 'incoming/apply/creator/'
    r = requests.get(url=url_serach, params={
        'page': '1'
    }).json()
    print(r)


def apply_search():
    # 数据条件查询
    # url_serach = root + '/incoming/apply/search/'
    url_serach = root + '/log/errlog/search_data'
    data = {
        'terms': json.dumps({'id': 79}),
        'page': 2
    }
    r = requests.post(url=url_serach, data=data).json()
    print(r)


def apply_paginator():
    # 数据条件查询
    url_serach = root + 'incoming/apply/paginator/'
    data = {
        'page': 2
    }
    r = requests.get(url=url_serach, params=data).json()
    print(r)


if __name__ == '__main__':
    pass
    # apply_show()
    # apply_search()
    # apply_paginator()
    # log_print('cuowu')
    apply_crate_test()
