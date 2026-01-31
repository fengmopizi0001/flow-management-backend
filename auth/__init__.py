"""
认证模块 - 流水管理系统
处理用户登录、登出和会话管理
"""

from flask import Blueprint, jsonify, session
from .routes import login, logout, change_password, change_username

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

# 注册路由
auth_bp.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
auth_bp.add_url_rule('/logout', view_func=logout)
auth_bp.add_url_rule('/change_password', view_func=change_password, methods=['POST'])
auth_bp.add_url_rule('/change_username', view_func=change_username, methods=['POST'])


# 添加检查登录状态的路由（用于前后端分离）
@auth_bp.route('/status', methods=['GET'])
def check_status():
    """
    检查登录状态
    返回当前用户的登录状态
    """
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'username': session.get('username'),
            'user_id': session.get('user_id'),
            'role': session.get('role')
        })
    else:
        return jsonify({'logged_in': False})
