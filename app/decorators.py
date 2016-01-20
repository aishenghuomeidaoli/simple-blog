#-*- coding:UTF-8 -*-
#检查用户权限的自定义修饰器

from functools import wraps
from flask import abort
from flask.ext.login import current_user
from .models import Permission

def permission_required(permission):#用于检查常规权限
	def decorator(f):
		@wraps(f)
		def decorated_function(*args,**kwargs):
			if not current_user.can(permission):
				abort (403)#返回403错误代码，HTTP"Forbidden“错误
			return f(*args,**kwargs)
		return decorated_function
	return decorator

def admin_required(f):#专门用于检查管理员权限
	return permission_required(Permission.ADMINISTER)(f)