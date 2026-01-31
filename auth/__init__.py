"""
认证模块 - 流水管理系统
处理用户登录、登出和会话管理
"""

from flask import Blueprint
from .routes import login, logout, change_password, change_username

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

# 注册路由
auth_bp.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
auth_bp.add_url_rule('/logout', view_func=logout)
auth_bp.add_url_rule('/change_password', view_func=change_password, methods=['POST'])
auth_bp.add_url_rule('/change_username', view_func=change_username, methods=['POST'])
