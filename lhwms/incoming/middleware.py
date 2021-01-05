from incoming.models import IncomingApply


def front_user_middleware(get_response):
    # 初始化
    def middleware(request):
        # request-> views
        # session有pk_id并且数据库存在该用户，绑定front_user属性到request上,
        # return; User对象；class 'apps.logistics_auth.models.User'> 15720618047
        user_id = request.session.get('_auth_user_id')
        if user_id:
            try:
                request.front_user = User.objects.get(pk=user_id)
            except:
                request.front_user = None
        else:
            request.front_user = None
        response = get_response(request)
        # views-> response

        return response
    return middleware
