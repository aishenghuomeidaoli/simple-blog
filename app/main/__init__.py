#-*- coding:UTF-8 -*-
from ..models import Permission
from flask import Blueprint

main=Blueprint('main',__name__)#创建蓝本实例

from . import views, errors#导入main包中的路由模块：views，错误处理模块：errors

#上下文处理器，使Permission定义的常量全局可访问，不必每次调用render_template()时为模版添加变量
@main.app_context_processor
def inject_permission():
	return dict(Permission=Permission)