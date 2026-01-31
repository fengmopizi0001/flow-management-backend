"""
客户模块 - 流水管理系统
处理客户相关功能
"""

from flask import Blueprint
from .routes import dashboard, records

# 创建蓝图
customer_bp = Blueprint('customer', __name__)

# 注册路由
customer_bp.add_url_rule('/', view_func=dashboard)
customer_bp.add_url_rule('/dashboard', view_func=dashboard)
customer_bp.add_url_rule('/records', view_func=records)
