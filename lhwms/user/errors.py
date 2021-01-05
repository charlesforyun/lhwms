class Login_err(Exception):
    def __str__(self):
        return '用户名或密码错误，请重试'


class Old_password_err(Exception):
    def __str__(self):
        return '原密码错误，请重试'


class Group_exist_err(Exception):
    def __str__(self):
        return '分组名已存在，请更换分组名或编辑已有分组'


class User_exist_err(Exception):
    def __str__(self):
        return '用户名已存在，请更换用户名或编辑已有用户'


class No_import_data_err(Exception):
    def __str__(self):
        return '无有效数据可导入'
