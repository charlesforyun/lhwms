import datetime

import redis

from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from user.models import *
from log.models import Syslog

from lhwms.settings import STATIC_URL
from lhwms.settings import REDIS_HOST
from lhwms.settings import REDIS_PORT


class MoudleMiddleware(object):
    '''登录和模块权限检测中间件'''
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.moudle_url = {m.url: m.name for m in Moudle.objects.all()}
        
    def __call__(self, request):  # 重载（），实例对象（）执行该方法
        '''响应'''
        try: 
            path = request.path  # /login/home/不包括域名和参数
            public_urls = ['/login', '/do_login']
            if path not in public_urls and not path.startswith(STATIC_URL):
                # 没登录跳转到登录页面
                if 'user_info' not in request.session:
                    return redirect(reverse('login'))
                # 检查模块访问权限
                if path in self.moudle_url:
                    group_id = request.session['user_info']['group_id']
                    group = Group.objects.get(id=group_id)
                    pers = str(group.permission_moudle).split(',')
                    if type(pers) is not list:
                        pers = [pers]
                    if self.moudle_url[path] not in pers:
                        return HttpResponse(status=403, content='用户权限不足')
            return self.get_response(request)
            
        except Exception as e:
            return HttpResponse(str(e))


class SyslogMiddleware(object):
    '''系统管理日志中间件'''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        '''响应'''
        try:
            path = request.path[1:]
            if path.startswith('master') or path.startswith('user'):
                # 拆分路径
                p = path.split('/')[1]
                if '_' in p:
                    p = p[:p.find('_')]
                # 确定操作名
                cur_action = ''
                operate_urls = {
                    'add': '添加条目',
                    'del': '删除条目',
                    'edit': '编辑条目',
                    'allow': '启用条目',
                    'forbid': '禁用条目',
                    'upload_excel': '导入数据',
                    'import_data': '执行导入',
                    'export_excel': '导出数据',
                    'reset_password': '重置密码',
                    }
                for u in operate_urls:
                    if path.find(u) >= 0:
                        cur_action = operate_urls[u]
                        break
                # 根据URL表查找模块名
                cur_moudle = ''
                mods = Moudle.objects.filter(class_big='系统管理')
                for m in mods:
                    if str(m.url).find(p) >= 0:
                        cur_moudle = m.name
                        break
                # 写入日志
                if cur_action:
                    new_syslog = Syslog()
                    new_syslog.user_id = request.session['user_info']['id']
                    new_syslog.moudle_name = cur_moudle
                    new_syslog.action = cur_action
                    new_syslog.do_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    new_syslog.save()

        except Exception as e:
            pass

        finally:
            return self.get_response(request)


class TestlogMiddleware(object):
    '''测试用自动登录中间件'''

    def __init__(self, get_response):
        self.get_response = get_response
        self.gp = Group.objects.all()[0]
        self.user = User.objects.all()[0]

    def __call__(self, request):
        '''响应'''
        # 加载用户信息到session
        if 'user_info' not in request.session:
            permission_moudle = self.gp.permission_moudle
            permission_account = self.gp.permission_account
            permission_edit_master = str(self.gp.permission_edit_master)

            # 转换成查询条件格式
            pers = permission_moudle.split(',')
            if type(pers) is list:
                permission_moudle = '; '.join(pers)
            pers = permission_account.split(',')
            if type(pers) is list:
                permission_account = '; '.join(pers)

            user_info = self.user.__dict__
            user_info.update({
                'permission_moudle': permission_moudle, 
                'permission_account': permission_account,
                'permission_edit_master': permission_edit_master,
            })
            request.session['user_info'] = user_info
        return self.get_response(request)