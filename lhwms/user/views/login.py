import datetime
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from lhwms.settings import PROJECT_NAME
from lhwms.settings import COPYRIGHT

from user.models import User
from user.models import Group

from log.views import loginlog
from log.views import errlog

from user.errors import Login_err


def login(request):
    '''加载登录页面'''
    try:
        # 项目名，版权信息，提示信息
        context = {
            'PROJECT_NAME': PROJECT_NAME,
            'COPYRIGHT': COPYRIGHT,
        }
        return render(request, 'login.html', context)
    except Exception as e:
        errlog.errlog_add(request, str(e))
        return HttpResponse(str(e))


@require_POST
def do_login(request):
    '''执行登陆'''
    try:
        # 读取POST信息
        rp = request.POST
        user_name_post = rp['user_name']
        password_post = rp['password']

        # 查找用户和用户状态
        w = "user_name='%s'" % user_name_post
        user_model_list = User.objects.extra(
            where=[w, "is_visible=1", "is_enable=1"])
        if not (user_model_list):
            raise Login_err

        # 校验密码
        password_cur = user_model_list[0].password
        if (password_cur != password_post):
            raise Login_err

        # 检查角色状态
        gp = Group.objects.get(id=user_model_list[0].group_id)
        if not (gp.is_visible and gp.is_enable):
            raise Login_err

        # 加载用户信息到session
        user_info = user_model_list[0].todict()
        permission_moudle = gp.permission_moudle
        permission_account = gp.permission_account
        permission_edit_master = str(gp.permission_edit_master)

        # 转换成查询条件格式
        pers = permission_moudle.split(',')
        if type(pers) is list:
            permission_moudle = '; '.join(pers)
        pers = permission_account.split(',')
        if type(pers) is list:
            permission_account = '; '.join(pers)

        user_info.update({
            'permission_moudle': permission_moudle,
            'permission_account': permission_account,
            'permission_edit_master': permission_edit_master,
        })
        request.session['user_info'] = user_info

        # 写入登录日志
        loginlog.loginlog_add(request)
        info_back = {'state': 1}

    except Exception as e:
        info_back = {'state': 0, 'err': str(e)}
        errlog.errlog_add(request, str(e))

    finally:
        return HttpResponse(json.dumps(info_back))


def logout(request):
    '''重新登陆'''
    try:
        request.session.flush()
        return redirect(reverse('login'))
    except Exception as e:
        errlog.errlog_add(request, str(e))
        return HttpResponse(str(e))
