from flask import abort
from flask_login import current_user
from functools import wraps
from simpledu.models import User

def role_required(role):
    """ 带参数的装饰器，可以使用它保护一个路由处理函数只能被特定
    角色的用户访问：

        @role_required(User.ADMIN)
        def admin():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwrargs):
            if not current_user.is_authenticated or current_user.role < role:
                abort(404)
            return func(*args, **kwrargs)
        return wrapper
    return decorator

staff_required = role_required(User.ROLE_STAFF)
admin_required = role_required(User.ROLE_ADMIN)
