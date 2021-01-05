import json

from django.http import HttpResponse
from django.shortcuts import render

from lhwms.settings import PROJECT_NAME
from lhwms.settings import COPYRIGHT

from user.models import Moudle
from user.models import Group

from log.views import errlog


def index(request):
    '''加载主页'''
    try:
        # 加载用户信息到session
        context = {
            'PROJECT_NAME': PROJECT_NAME,
            'COPYRIGHT': COPYRIGHT,
            'user_info': request.session['user_info'],
        }
        return render(request, 'index.html', context)
    except Exception as e:
        errlog.errlog_add(request, str(e))
        return HttpResponse(str(e))


def menu_all(request):
    '''获取菜单树（全部）'''
    try:
        return get_menu(request, True)
    except Exception as e:
        errlog.errlog_add(request, str(e))
        return HttpResponse(str(e))


def menu_per(request):
    '''获取菜单树（当前权限范围）'''
    try:
        return get_menu(request, False)
    except Exception as e:
        errlog.errlog_add(request, str(e))
        return HttpResponse(str(e))


def get_menu(request, getall=True):
    '''获取菜单tree数据字符串'''
    try:
        root_nodes = []
        middle_nodes = []
        leaf_nodes = []
        root_names = []
        middle_names = []
        leaf_names = []
        mods = Moudle.objects.all()
        per = request.session['user_info']['permission_moudle']

        # 读取各级节点信息
        for m in mods:
            # 一级分类，根节点
            if m.class_big not in root_names:
                root_names.append(m.class_big)
                root_node = {
                    # 'id': m.class_big,
                    'text': m.class_big,
                    'attributes': {'url': ''},
                    'children': [],
                }
                root_nodes.append(root_node)

            # 二级分类，中间节点
            if m.class_small not in middle_names:
                middle_names.append(m.class_small)
                middle_node = {
                    'class_big': m.class_big,
                    # 'id': m.class_small,
                    'text': m.class_small,
                    'state': 'closed',
                    'attributes': {'url': ''},
                    'children': [],
                }
                middle_nodes.append(middle_node)

            # 三级分类，叶节点
            if m.name not in leaf_names:
                leaf_names.append(m.name)
                leaf_node = {
                    'class_small': m.class_small,
                    'id': m.name,
                    'text': m.name,
                    'attributes': {'url': m.url},
                    'children': [],
                }
                leaf_nodes.append(leaf_node)

        for i in root_nodes:
            for j in middle_nodes:
                for k in leaf_nodes:
                    # 节点挂靠，模块权限过滤
                    per_allow = True
                    if not getall:
                        per_allow = (per.find(k['text']) >= 0)
                    if k['class_small'] == j['text'] and per_allow:
                        if not k.get('used', ''):
                            j['children'].append(k)
                            k.update({'used': '1'})
                # 没子节点的不挂靠大类
                if j['class_big'] == i['text'] and j['children']:
                    i['children'].append(j)

        # 删除没有子项目的根节点
        i = len(root_nodes) - 1
        while i >= 0:
            if not root_nodes[i]['children']:
                del root_nodes[i]
            i -= 1

        return HttpResponse(json.dumps(root_nodes))

    except Exception as e:
        errlog.errlog_add(request, str(e))
        return HttpResponse(str(e))
