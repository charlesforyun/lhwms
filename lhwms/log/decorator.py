from functools import wraps


def catch_exception(func, code=500, *args, **kwargs):
    @wraps(func, *args, **kwargs)
    def wrapper(request, *args, **kwargs):
        try:
            back = func(request, *args, **kwargs)
            return back
        except Exception as e:
            return 1

    return wrapper
