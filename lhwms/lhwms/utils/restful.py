from django.http import JsonResponse
"""
###############
restful api
return JsonResponse({"code": 200, "message": string, "data": obj})
json_dumps_params={'ensure_ascii': False}:编码取消默认ascics
################
"""


class HttpCode:
    ok = 200
    params_error = 400  # 黑名单
    un_auth = 401  # 请求头错误，验证失败
    method_error = 405
    server_error = 500


def result(code=HttpCode.ok, message=None, data=None, kwargs=None):
    # 重构JsonResponse
    json_data = {"code": code, "message": message, "data": data}
    if kwargs and isinstance(kwargs, dict) and kwargs.keys():
        json_data.update(kwargs)
    return JsonResponse(json_data, json_dumps_params={'ensure_ascii': False})


def ok(message=None, data=None):
    return result(message=message, data=data)


def params_error(message=None, data=None):
    return result(code=HttpCode.params_error, message=message, data=data, kwargs=None)


def un_auth(message=None, data=None):
    return result(code=HttpCode.un_auth, message=message, data=data, kwargs=None)


def method_error(message=None, data=None):
    return result(code=HttpCode.method_error, message=message, data=data, kwargs=None)


def server_error(message=None, data=None):
    return result(code=HttpCode.server_error, message=message, data=data, kwargs=None)
