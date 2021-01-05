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


class Loginlog(Basic):
    '''用户登录日志,中间件'''
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user.User', on_delete=models.DO_NOTHING)
    login_ip = models.CharField(max_length=32)  # 登陆IP
    login_time = models.DateTimeField()  # 登陆时间
    is_visible = models.BooleanField(default=True)
    is_enable = models.BooleanField(default=True)


class Syslog(Basic):
    '''系统管理日志，中间件？'''
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user.User', on_delete=models.DO_NOTHING)
    moudle_name = models.CharField(max_length=16, null=True)  # 模块名
    action = models.CharField(max_length=16)  # 操作
    do_time = models.DateTimeField()  # 时间
    is_visible = models.BooleanField(default=True)
    is_enable = models.BooleanField(default=True)


class Errlog(models.Model):
    '''系统异常日志'''
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user.User', on_delete=models.DO_NOTHING)
    path = models.CharField(max_length=128, null=True)  # URL
    error = models.CharField(max_length=256)  # 异常信息
    err_time = models.DateTimeField(null=True)  # 时间
    is_visible = models.BooleanField(default=True)
    is_enable = models.BooleanField(default=True)
