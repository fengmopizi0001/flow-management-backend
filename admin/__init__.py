"""
管理员模块 - 流水管理系统
处理所有管理员相关功能
"""

from flask import Blueprint
from .routes import (
    dashboard, 
    import_excel,
    add_target,
    edit_target,
    delete_target,
    add_record,
    view_records,
    reconciliation,
    customer_query_select,
    customer_query_view,
    customer_query_search
)
from .customer_manager import (
    add_customer,
    delete_user,
    reset_password
)

# 创建蓝图
admin_bp = Blueprint('admin', __name__)

# 注册主路由
admin_bp.add_url_rule('/', view_func=dashboard)
admin_bp.add_url_rule('/dashboard', view_func=dashboard)
admin_bp.add_url_rule('/import_excel', view_func=import_excel, methods=['GET', 'POST'])
admin_bp.add_url_rule('/add_target', view_func=add_target, methods=['GET', 'POST'])
admin_bp.add_url_rule('/edit_target/<int:target_id>', view_func=edit_target, methods=['GET', 'POST'])
admin_bp.add_url_rule('/delete_target/<int:target_id>', view_func=delete_target, methods=['POST'])
admin_bp.add_url_rule('/add_record', view_func=add_record, methods=['GET', 'POST'])
admin_bp.add_url_rule('/view_records', view_func=view_records)
admin_bp.add_url_rule('/reconciliation', view_func=reconciliation)
admin_bp.add_url_rule('/customer_query', view_func=customer_query_select)
admin_bp.add_url_rule('/customer_query/<int:customer_id>', view_func=customer_query_view)
admin_bp.add_url_rule('/customer_query/search/<int:customer_id>', view_func=customer_query_search, methods=['POST'])

# 注册客户管理路由
admin_bp.add_url_rule('/api/add_customer', view_func=add_customer, methods=['POST'])
admin_bp.add_url_rule('/delete_user/<int:user_id>', view_func=delete_user, methods=['POST'])
admin_bp.add_url_rule('/reset_password/<int:user_id>', view_func=reset_password, methods=['POST'])
