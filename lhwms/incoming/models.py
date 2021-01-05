from django.db import models


class Basic(models.Model):
    '''表父类'''

    def todict(self):
        dic = self.__dict__
        for key in dic:
            dic[key] = str(dic[key])
        del dic['_state']
        return dic

    def __str__(self):
        return str(self.todict)

    class Meta:
        abstract = True


class IncomingApply(models.Model):
    '''入库申请明细表'''
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey("user.User", on_delete=models.SET_NULL, null=True)
    incoming_doc_mark = models.CharField(max_length=16, null=True)  # 入库申请(单)编号
    stock_mark = models.CharField(max_length=16, null=True)  # 存放编号

    apply_cons_mark = models.CharField(max_length=16, db_index=True)  # 申请施工单位代码/入库申请单位
    asset_name = models.CharField(max_length=64, null=True)  # 资产名称
    proj_from = models.CharField(max_length=16, null=True)  # 物资来源
    proj_mark = models.CharField(max_length=64, null=True)  # 工程编号(选填)
    proj_name = models.CharField(max_length=64, null=True)  # 项目名称
    ini_from = models.CharField(max_length=64, null=True)  # 详细来源(选填)

    mat_mark = models.CharField(max_length=16)  # 物料编码
    mat_extend_mark = models.CharField(max_length=16, null=True)  # 物料扩展码(选填)
    mat_from = models.CharField(max_length=64, null=True)  # 物料描述(选填)
    pars = models.CharField(max_length=32)  # 规格型号
    mat_type = models.CharField(max_length=32)  # 物资类型

    dp = models.DateField(null=True)  # 生产日期(选填)
    supplyer = models.CharField(max_length=32, null=True)  # 厂家(选填)
    bp = models.CharField(max_length=32, null=True)  # 出厂编号(选填)
    use_date = models.DateField()  # 投运日期
    remove_date = models.DateField()  # 拆除日期
    pms_status = models.CharField(max_length=32, null=True)  # PMS台账情况(选填)
    test_result = models.CharField(max_length=16)  # 试验结果

    wh_mark = models.CharField(max_length=16)  # 仓库代码(拟入仓库名称)
    num = models.DecimalField(max_digits=12, decimal_places=3)  # 入库数量

    is_visible = models.BooleanField(default=False)  # 提交后可见
    is_enable = models.BooleanField(default=False)  # 申请通过
    is_approve_reason = models.CharField(max_length=32, null=True)  # 驳回理由

    create_time = models.DateTimeField(auto_now_add=True)  # 申请单创建时间
    # update_time = models.DateTimeField(auto_now=True)  # 修改时间


class Accessory(models.Model):
    """附件存储路径表，针对每个需要存储文件的给个外键链接"""
    accessory = models.FileField(null=True)
    table_id = models.ForeignKey("IncomingApply", on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'Accessory'


class IncomingIds(Basic):
    '''入库流水号记录表'''
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    incoming_id = models.IntegerField(default=1)  # 入库日期流水号(单)
    stock_id = models.IntegerField(default=1)  # 存放编号日期流水号
