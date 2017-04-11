from  functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission



#访问权限限制
def permisson_require(permisson):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not current_user.can(permisson):
                abort(403)
            return f(*args,**kwargs)
        return decorated_function
    return decorator

#管理员权限访问
def admin_require(f):
    return permisson_require(Permission.ADMINSTER)(f)

