class FormMixin(object):
    """
    错误处理模块，格式化form.get_json_data()
    返回dict，通过JsonResponse（不是dict类型需要改参数）传给前端，
    form.errors 包含了html标签错误的信息
    form.as_json(),将form.get_json_data()返回的字典dump成json格式的字符串，方便传输
    """
    def get_errors(self):
        """
        *api:json:{"code": 200, "message": "", "data": {}}
        form.get_json_data(): errors{
            "telephone": [{"message": " 号码过长，请重新输入！", "code": " ax_length"}],
            "password": [{"message": " 密码过长，请重新输入", "code": " max_length"},
                        {"message": " 密码过短，请重新输入", "code": " min_length"}
                ]
            }
        --->>
        {"telephone": ["号码过长，请重新输入！"], "password": ["密码过长，请重新输入！", "密码果短，请重新输入！"]}
        :return: new_errors
        """
        if hasattr(self, 'errors'):
            errors_old = self.errors.get_json_data()
            errors = {}  # 对应message
            for error_key, error_list in errors_old.items():
                value = []
                for value_dict in error_list:
                    value.append(value_dict['message'])
                errors.update({error_key: value})
            return errors
        else:
            return {}




