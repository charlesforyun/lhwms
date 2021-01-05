from . import *


class ImportField(object):
    '''导入 字段类'''

    def __init__(self, name, unique, null, title, pattern, dtype='s'):
        '''初始化信息'''
        self.name = name  # 模型字段名
        self.unique = unique  # 字段是否是唯一索引
        self.null = null  # 允许空值
        self.title = title  # 导入模板里的表头
        self.pattern = pattern  # 导入内容格式正则
        self.dtype = dtype  # 数据类型 's':文本 'f':小数 'i':整数 'd':日期


def get_template(request, fields):
    '''
    获取数据导入模板
    fields: ImportField对象的列表
    return file response
    '''
    # 创建Excel工作簿
    book = openpyxl.Workbook()
    sheet = book.active  # worksheet对象建立
    sheet.cell(row=1, column=1).value = '序号'

    # 写入表头
    for c in range(len(fields)):
        cell = sheet.cell(row=1, column=c + 2)
        cell.value = fields[c].title
        cm = get_column_letter(c + 2)  # 生成列标号
        # 调整列宽
        sheet.column_dimensions[cm].width = 20
        # 调整背景色
        fp_yellow = PatternFill(fill_type='solid', fgColor="FFFF33")  # 黄色
        fp_gray = PatternFill(fill_type='solid', fgColor="AAAAAA")  # 灰色
        if not fields[c].null:
            cell.fill = fp_yellow
        else:
            cell.fill = fp_gray

    # 保存到临时文件夹
    file_name = get_ufn(request) + '.xlsx'
    file_path = os.path.join(TEMP_DIR, file_name)
    book.save(file_path)
    book.close()

    # 返回 FileResponse文件流
    file = open(file_path, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response[
        'Content-Disposition'] = 'attachment;filename="%s"' % 'template.xlsx'
    return response


def read_excel(request, model, query_mark, excel_file, fields, joins=[]):
    '''
    读入EXCEL数据并进行数据校验和缓存
    model: model对象
    query_mark: 缓存标识符
    excel_file: 读入excel文件名
    fields: ImportField对象的列表  field.name是什么？
    joins: 关联字段
    '''
    max_row_num = 5000  # 最大导入行数
    # 接收上传EXCEL表并读取数据
    excel_file.name = get_ufn(request) + '.xlsx'
    file_path = os.path.join(MEDIA_ROOT, excel_file.name)

    with open(file_path, 'wb+') as f:
        for chunk in excel_file.chunks():
            f.write(chunk)

    # 读取数据到列表
    book = openpyxl.load_workbook(file_path)
    sheet = book[book.get_sheet_names()[0]]

    # 逐行读取到rows
    rows = []
    r = 2
    text = ''
    while True:
        # 逐行读取数据
        row = {}
        for c in range(len(fields)):
            cell = sheet.cell(row=r, column=c + 2)
            # 去空格 转义
            value = str(cell.value)
            value = value.strip()
            value = escape_string(value)
            # 逐字段读取数据
            row[fields[c].name] = value
            text += str(value)
        # 空行停止
        if text.replace('None', '') == '':
            break
        # 超过最大行数 停止
        if r > (max_row_num + 1):
            break
        text = ''
        rows.append(copy.copy(row))
        r += 1
    book.close()
    # os.remove(file_path)

    # 检查读取的数据
    if not rows:
        return '未找到数据，请检查表格。'

    msgs_tip = []  # 重复条目信息
    msgs_err = []  # 无效条目信息
    rows_update = []  # 更新数据条目
    rows_insert = []  # 新写入数据条目
    field_values = {}  # 导入数据字段值集合

    tb_main = model._meta.db_table  # 主表名
    cursor = connection.cursor()  # mysql游标

    # 按字段取出所有数据值列表
    for field in fields:
        cur_field_values = [r[field.name] for r in rows]
        cur_field_values = list(set(cur_field_values))
        if 'None' in cur_field_values:
            cur_field_values.remove('None')
        field_values.update({field.name: cur_field_values})

    # 数据有效性检查
    for i in range(len(rows)):
        msg = ''
        wheres = []
        sql_wheres = ''
        uf_name_values = {}
        sql_select = 'SELECT id FROM %s WHERE %s'

        # 逐字段
        for field in fields:
            value = str(rows[i][field.name])
            # 非空检验
            if not field.null:
                if value == '':
                    context = (i + 1, field.title)
                    msg = '第 %d 行：字段"%s"的值不能为空。' % context
                    msgs_err.append(msg)
                    break

            # 正则检验
            if field.pattern:
                if not re.match(field.pattern, value):
                    context = (i + 1, field.title, value, field.pattern)
                    msg = '第 %d 行：字段"%s"的值"%s"不符合格式"%s"。' % context
                    msgs_err.append(msg)
                    break

            # 导入数据内唯一性检验
            if field.unique:
                values_temp = copy.copy(field_values[field.name])
                values_temp.remove(value)
                if value in values_temp:
                    context = (i + 1, field.title, value)
                    msg = '第 %d 行：字段"%s"的值"%s"不能与其它条目重复。' % context
                    msgs_err.append(msg)
                    break

            # 拼接用于索引检查的字段
            if field.unique:
                where = "%s = '%s'"
                where = where % (field.name, value)
                wheres.append(where)
                uf_name_values.update({field.title: value})

        # 检测关联索引是否存在
        for j in joins:
            # 读取关联表和字段信息
            join_tb = j['join_model']._meta.db_table  # 关联表名
            join_tb_name = j['join_model_name']
            # 生成关联条件语句
            sql_select = 'SELECT id FROM %s'
            sql_where = 'WHERE %s'
            wheres_dic = {}
            wheres_sql = []
            for f in j['fields']:
                wheres_dic.update({f['to']: rows[i][f['from']]})
            for w in wheres_dic:
                where = "%s = '%s'"
                value = str(wheres_dic[w])
                if value != '':
                    wheres_sql.append(where % (w, value))
            sql_select = sql_select % (join_tb)
            if wheres_sql:
                sql_where = sql_where % (' AND '.join(wheres_sql))
                sql_select = sql_select + ' ' + sql_where
            # 执行查询
            cursor.execute(sql_select)
            finds = cursor.fetchall()
            if not finds:
                context = (
                    i + 1,
                    j['join_model_name'] + str(list(wheres_dic.values())))
                msg = '第 %d 行：%s不存在。' % context
                msgs_err.append(msg)

        # 如果以上检验全部通过
        if not msg:
            if wheres:
                # 查找是否已有重复索引的记录
                sql_wheres = ' AND '.join(wheres)
                sql_select = 'SELECT id FROM %s WHERE %s'
                sql_select = sql_select % (tb_main, sql_wheres)
                cursor.execute(sql_select)
                finds = cursor.fetchall()
                # 索引存在的更新，不存在的增加
                if finds:
                    context = (i + 1, str(uf_name_values))
                    msg = '第 %d 行：%s已存在，导入后将更新原有数据。' % context
                    msgs_tip.append(msg)
                    rows[i].update({'id': finds[0][0]})  # 记录下id加速更新
                    rows_update.append(rows[i])
                else:
                    rows_insert.append(rows[i])
            else:
                rows_insert.append(rows[i])

    # 缓存数据并返回检查结果文本
    # 可导入条目加载到缓存
    key = get_key(request, model, query_mark)
    rc = redis.Redis(connection_pool=pool_import)
    rows = {'rows_insert': rows_insert, 'rows_update': rows_update}
    rc.set(key, json.dumps(rows), ex=60 * 30)

    # 生成检查结果文本
    snum = len(rows['rows_insert']) + len(rows['rows_update'])
    result = '有效数据：%s 条；' % snum + '\n'
    result = result + '无效数据：%s 条；' % len(msgs_err) + '\n\n'
    if len(msgs_err):
        result = result + '无效数据详情：' + '\n' + '\n'.join(msgs_err) + '\n\n'
    if len(msgs_tip):
        result = result + '数据导入提示：' + '\n' + '\n'.join(msgs_tip)
    return result

    # 返回检查结果文本
    result = get_result_msg(rows, msgs_tip, msgs_err)
    return result


def import_rows(request, model, query_mark, fields):
    '''
    将缓存数据写入数据库
    model: model对象
    query_mark: 缓存标识符
    fields: ImportField对象的列表
    '''
    # 获取缓存的可导入数据
    key = get_key(request, model, query_mark)
    rc = redis.Redis(connection_pool=pool_import)
    rows = json.loads(rc.get(key))
    rows_update = rows['rows_update']  # 覆盖数据
    rows_insert = rows['rows_insert']  # 新增数据
    tb_main = model._meta.db_table  # 主表名

    # 获取字段名
    field_names = []  # 所有字段名
    unique_names = []  # 索引字段名
    for field in fields:
        field_names.append(field.name)
        if field.unique:
            unique_names.append(field.name)
    field_names.append('is_visible')
    field_names.append('is_enable')

    # 生成 insert语句
    sql_insert = 'INSERT INTO %s (%s) VALUES %s'
    sql_values = []
    sql_all_field = []
    sql_all_value = ''

    for row in rows_insert:
        cur_values = []  # vslues字符串
        # 逐字段获取值
        for field in fields:
            value = row[field.name]
            # 适应数据格式
            if field.dtype not in ['f', 'i']:
                value = "'%s'" % value
            elif field.dtype == 'f':
                value = float(value)
            elif field.dtype == 'i':
                value = int(value)
            cur_values.append(str(value))
        cur_values.append('1')  # is_visible
        cur_values.append('1')  # is_enable
        # 拼接此行values
        sql_values.append('(%s)' % ','.join(cur_values))

    sql_all_field = ','.join(field_names)
    sql_all_value = ','.join(sql_values)
    sql_insert = sql_insert % (tb_main, sql_all_field, sql_all_value)

    # 生成update语句
    updates = []
    for row in rows_update:
        cur_values = []
        update = 'UPDATE %s SET %s'
        # 逐字段获取值
        for field in fields:
            value = row[field.name]
            # 适应数据格式
            if field.dtype not in ['f', 'i']:
                value = "'%s'" % value
            elif field.dtype == 'f':
                value = float(value)
            elif field.dtype == 'i':
                value = int(value)
            # 非索引字段加入赋值语句
            if not field.unique:
                cur_value = '%s = %s' % (field.name, value)
                cur_values.append(cur_value)
            # 如果之前被删除（隐藏）的则重新显示
            cur_values.append('is_visible = 1')
        # 生成update语句
        update = update % (tb_main, ','.join(cur_values))
        update = update + ' WHERE id = %s' % row['id']
        updates.append(update)

    # 执行写入
    try:
        cursor = connection.cursor()
        if rows_insert:
            cursor.execute(sql_insert)
        if rows_update:
            for u in updates:
                cursor.execute(u)

    except Exception as e:
        connection.rollback()
        return {'insert': 0, 'update': 0}

    else:
        connection.commit()
        innum = len(rows_insert)
        upnum = len(rows_update)
        return {'insert': innum, 'update': upnum}

    finally:
        rc.delete(key)
