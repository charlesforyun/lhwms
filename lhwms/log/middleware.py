def log_middleware(get_response):
    # 这个中间件初始化的代码

    def middleware(request):
        # request到达view的执行代码

        response = get_response(request)

        # response到达浏览器的执行代码

        return response

    return middleware