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


class Group(Basic):
    '''用户组表'''
    id = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=16, null=True)
    permission_moudle = models.CharField(max_length=512,
                                         default='["*",]')  # 模块权限
    permission_account = models.CharField(max_length=512,
                                          default='["*",]')  # 账套权限
    permission_edit_master = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)
    is_enable = models.BooleanField(default=True)


class User(Basic):
    '''用户表'''
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=16, db_index=True)  # 用户名
    real_name = models.CharField(max_length=16)  # 真实姓名
    department = models.CharField(max_length=32, null=True)  # 所属部门
    tel = models.CharField(max_length=32, null=True)  # 联系电话
    password = models.CharField(max_length=32)  # 用户密码(md5)
    group = models.ForeignKey('Group', on_delete=models.DO_NOTHING,
                              null=True)  # 所属分组
    is_visible = models.BooleanField(default=True)
    is_enable = models.BooleanField(default=True)


class Moudle(Basic):
    '''功能模块表'''
    id = models.AutoField(primary_key=True)
    class_big = models.CharField(max_length=16)
    class_small = models.CharField(max_length=16)
    name = models.CharField(max_length=16)
    url = models.CharField(max_length=64)
    state = models.SmallIntegerField(default=1)
