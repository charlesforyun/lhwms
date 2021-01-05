from . import *


def search(request, model, query_mark, terms, check_acc=True,
           fun_check=None, where='', joins=[]):
    '''
    设置查询条件
    model: model对象
    query_mark: 缓存标识符
    terms: 查询条件列表
    check_acc: 根据账套权限过滤数据
    fun_check: 自定义数据检查函数
    where: 自定义查询where子句
    joins: 关联字段
    '''
    rc_terms = redis.Redis(connection_pool=pool_terms)  # 查询条件池
    rc_querys = redis.Redis(connection_pool=pool_querys)  # 查询结果池
    terms = copy.copy(terms)
    # 删除CSRF信息 
    if 'csrfmiddlewaretoken' in terms:
        terms.pop('csrfmiddlewaretoken')
    # 查询条件写入redis
    key = get_key(request, model, query_mark)
    rc_terms.set(key, json.dumps(terms), ex=60 * 60 * 12)
    # 按条件查询所有符合条件的记录id并缓存
    rows = fill(request, model, check_acc, where, joins)
    rows_ids = filter(rows, terms, fun_check)
    rc_querys.set(key, json.dumps(rows_ids), ex=60 * 60 * 12)
    return True


def load(request, model, query_mark, page_num, row_num, joins=[]):
    '''
    根据查询条件执行查询返回数据（分页数据）
    model: model对象
    query_mark: 缓存标识符
    page_num: 页数
    row_num: 行数
    joins: 关联字段
    '''
    # 创建条件和结果缓存redis连接
    rc_terms = redis.Redis(connection_pool=pool_terms)
    rc_querys = redis.Redis(connection_pool=pool_querys)
    key = get_key(request, model, query_mark)
    # 未命中缓存返回空值,需要重新查询
    if not rc_querys.get(key):
        return '{"total": 0, "rows": []}'
    rows_ids = json.loads(rc_querys.get(key))

    # 数据分页,总条目数小于每页条目数不分页
    if page_num and row_num:
        if len(rows_ids) > row_num:
            pnum = math.ceil(len(rows_ids) / row_num)
            if page_num > pnum:
                page_num = pnum
            p_start = int((page_num - 1) * row_num)
            p_end = int(page_num * row_num)
            if p_end > len(rows_ids):
                p_end = len(rows_ids)
            ids_cur_page = rows_ids[p_start: p_end]
        else:
            ids_cur_page = rows_ids
    else:
        ids_cur_page = rows_ids

    # 根据分页id查询完整数据

    tb_main = model._meta.db_table
    sql_idin = '%s.id IN (%s)' % (tb_main, ','.join(ids_cur_page))
    rows_cur_page = fill(request, model, False, sql_idin, joins)

    # 返回json数据
    rows_page_json = str(json.dumps(rows_cur_page))
    rows_page_json = rows_page_json.replace('"None"', '""')
    context = '{"total": %d, "rows": %s}'
    context = context % (len(rows_ids), rows_page_json)
    return context


def fill(request, model, check_acc=False, where='', joins=[]):
    '''
    JOIN填充完整数据，《多条件查询语句转化！》
    model: model对象
    check_acc: 根据账套权限过滤数据
    where: 自定义查询where子句
    joins: 关联字段
    :return: 条件list
    '''
    tb_main = model._meta.db_table  # 主表名

    # 获取用户账套权限
    if check_acc:
        accper = request.session['user_info']['permission_account']
        accs = accper.split('; ')
        if type(accs) is not list:
            accs = [accs]
        ins = str(tuple(accs))

        # 获取模型所有字段
        mfields = [str(m.verbose_name) for m in model._meta.fields]
        wheres_acc = []
        # 获取用户可访问的施工单位和周转库
        if 'cons_mark' in mfields:
            sql = '(%s.cons_mark IN %s OR %s.cons_mark IS NULL)' % (
                tb_main, ins, tb_main)
            wheres_acc.append(sql)
        if 'wh_mark' in mfields:
            sql = '(%s.wh_mark IN %s OR %s.wh_mark IS NULL)' % (
                tb_main, ins, tb_main)
            wheres_acc.append(sql)
        # 账套权限过滤条件
        sql_acc = ' AND '.join(wheres_acc)

    # 可见过滤条件
    wheres = ['%s.is_visible = 1' % tb_main]
    if check_acc:
        wheres.append(sql_acc)
    # 自定义where条件
    if where:
        wheres.append(where)
    # 所有预筛选条件
    sql_where = '(SELECT * FROM %s WHERE %s)' % (tb_main, ' AND '.join(wheres))

    # 左连接查询加载关联表数据
    join_sqls = []
    if joins:
        for j in joins:
            sql_join = 'LEFT JOIN %s ON %s'
            join_tb = j['join_model']._meta.db_table  # 关联表名
            on_sqls = []
            # 生成关联条件语句
            for f in j['fields']:
                sql_on = '%s.%s = %s.%s'
                params = ('a', f['from'], join_tb, f['to'])
                sql_on = sql_on % params
                on_sqls.append(sql_on)
            sql_join = sql_join % (join_tb, ' AND '.join(on_sqls))
            join_sqls.append(sql_join)

    # 执行查询
    try:
        sql = 'SELECT * FROM %s a %s' % (sql_where, ' '.join(join_sqls))
        querys = model.objects.raw(sql)
        rows_filled = [q.todict() for q in querys]
        return rows_filled
    except Exception as e:
        return []


def filter(rows, terms, fun_check=None):
    '''
    根据查询条件过滤数据
    1. 可接受多个查询条件(json格式)，每个条件对应一个字段
       每个查询条件又可包含多个关键字keyword
    2. 关键字是纯文本字符串时，执行正则匹配
    3. 关键字是以['>','>=','<','<=','=','!=']之一开头的时候
       视作关系表达式，支持将字段值转换为数值或日期进行比较运算，
       每个关键字之间为and关系，关键字各个条件之间都是or关系
    rows: 要筛选的数据 fill()返回值
    terms: 查询条件列表
    fun_check: 自定义数据检查函数
    :return list
    '''

    def is_number(s):
        '''判断是否为数值'''
        try:
            a = float(s)
            return True
        except Exception as e:
            return False

    def if_match(value, term):
        '''判断字段值是否匹配某个条件'''
        # 转换条件格式
        keywords = None
        try:
            keywords = json.loads(term)
        except Exception as e:
            pass
        finally:
            if type(keywords) is not list:
                keywords = [str(term)]

        # 逐个检查条件关键词
        for i in range(len(keywords)):
            keyword = str(keywords[i])
            # 首先查找关系运算符
            # 以['>','>=','<','<=','=','!=']之一开头的视为条件表达式
            ops = ['>', '>=', '<', '<=', '=', '!=']
            cur_op = ''
            for op in ops:
                if keyword.startswith(op):
                    cur_op = op
            # 条件表达式执行数值或日期数值比较
            if cur_op:
                keyword = keyword.replace(' ', '')
                v = keyword[len(cur_op):]
                # 浮点数执行数值运算
                if is_number(v) and is_number(value):
                    exp = 'float(value) %s float(v)' % cur_op
                    return eval(exp)
                else:
                    # 日期执行日期运算
                    try:
                        v_date = datetime.datetime.strptime(v,
                                                            '%Y-%m-%d')  # 条件日期
                        f_date = datetime.datetime.strptime(value[:10],
                                                            '%Y-%m-%d')  # 字段值日期
                        delta = f_date - v_date
                        exp = 'delta.days %s 0' % cur_op
                        return eval(exp)
                    except Exception as e:
                        pass
            else:
                # 空值跳过
                if keyword == '':
                    return True
                # 正则匹配
                keyword = '%s' % keyword  # .replace('*', '(.+?)')
                if re.search(keyword, value):
                    return True
        return False

    # 按条件过滤
    rows_filted_ids = []  # 符合条件的记录

    for row in rows:
        matched_num = 0  # 满足的条件个数
        for field in terms:
            keyword = str(terms.get(field, ''))
            # 如果条件为空则直接跳过
            if not keyword:
                matched_num += 1
                continue
            # 检测字段值是否匹配查询条件
            if if_match(row.get(field, ''), keyword):
                matched_num += 1
        # 自定义函数过滤
        if fun_check:
            if not fun_check(row):
                continue
        # 全部匹配则添加到符合记录列表
        if matched_num == len(terms):
            rows_filted_ids.append(row['id'])

    return rows_filted_ids


class ExportField(object):
    '''导出 字段类'''

    def __init__(self, name, title, cwidth=15):
        '''初始化信息'''
        self.name = name  # 字段名
        self.title = title  # 表头
        self.cwidth = cwidth  # 列宽


def export_excel(request, model, query_mark, fields_export, joins=[]):
    '''
    导出查询数据到excel文件
    model: model对象
    query_mark: 缓存标识符
    fields_export: ExportField对象列表
    joins: 关联字段
    '''
    max_row_num = 100000  # 最大导出行数

    # 从缓存加载数据
    rc = redis.Redis(connection_pool=pool_querys)
    key = get_key(request, model, query_mark)
    ids = json.loads(rc.get(key))
    # 填充数据
    tb_main = model._meta.db_table  # 获取数据表名
    sql_idin = '%s.id IN (%s)' % (tb_main, ','.join(ids))
    rows = fill(request, model, False, sql_idin, joins)
    # 限制最大导出行数
    if len(rows) > max_row_num:
        rows = rows[: max_row_num]

    # 写入表头
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.cell(row=1, column=1).value = '序号'
    # 设置表头背景色
    fp = PatternFill(fill_type='solid', fgColor="77DDFF")  # 浅蓝色
    sheet.cell(row=1, column=1).fill = fp
    c = 2

    for field in fields_export:
        # 写入表头
        cell = sheet.cell(row=1, column=c)
        cell.value = field.title
        # 设置背景色和列宽
        cell.fill = fp
        cm = get_column_letter(c)  # 生成列标号
        sheet.column_dimensions[cm].width = field.cwidth
        c += 1

    # 写入数据
    r = 2
    c = 2
    for item in rows:
        # 生成序号
        sheet.cell(row=r, column=1).value = r - 1
        # 逐行,逐字段写入数据
        for field in fields_export:
            cell = sheet.cell(row=r, column=c)
            # 写入数据
            value = item.get(field.name, '')
            value = value.replace('None', '')
            cell.value = value
            c += 1
        c = 2
        r += 1

    # 保存到临时文件夹
    file_name = get_ufn(request) + '.xlsx'
    file_path = os.path.join(TEMP_DIR, file_name)
    book.save(file_path)
    book.close()

    # 返回 FileResponse
    file = open(file_path, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % 'export.xlsx'
    return response
