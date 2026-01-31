"""
工具函数模块 - 流水管理系统
提供通用的辅助函数
"""

from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, flash


def require_login(f):
    """
    登录验证装饰器
    检查用户是否已登录
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """
    管理员权限验证装饰器
    检查用户是否为管理员
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('此功能需要管理员权限', 'error')
            return redirect(url_for('customer.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def require_customer(f):
    """
    客户权限验证装饰器
    检查用户是否为客户
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') != 'customer':
            flash('此功能仅客户可用', 'error')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def parse_date_from_form(year, month, day):
    """
    从表单的年月日字段解析日期
    :param year: 年
    :param month: 月
    :param day: 日
    :return: 日期字符串 YYYY-MM-DD 或 None
    """
    if year and month and day:
        return f"{year}-{month}-{day}"
    return None


def parse_date_range_from_request(request):
    """
    从请求中解析日期范围
    :param request: Flask request对象
    :return: (start_date, end_date) 元组
    """
    start_year = request.args.get('start_year') or request.form.get('start_year')
    start_month = request.args.get('start_month') or request.form.get('start_month')
    start_day = request.args.get('start_day') or request.form.get('start_day')
    end_year = request.args.get('end_year') or request.form.get('end_year')
    end_month = request.args.get('end_month') or request.form.get('end_month')
    end_day = request.args.get('end_day') or request.form.get('end_day')
    
    start_date = parse_date_from_form(start_year, start_month, start_day)
    end_date = parse_date_from_form(end_year, end_month, end_day)
    
    return start_date, end_date


def calculate_percentage(part, total):
    """
    计算百分比
    :param part: 部分
    :param total: 总数
    :return: 百分比值（0-100）
    """
    if total and total > 0:
        return round((part / total) * 100, 2)
    return 0


def format_currency(amount):
    """
    格式化金额显示
    :param amount: 金额
    :return: 格式化后的字符串
    """
    if amount is None:
        return '0.00'
    return f"{amount:,.2f}"


def format_date(date_str):
    """
    格式化日期显示
    :param date_str: 日期字符串
    :return: 格式化后的日期
    """
    if not date_str:
        return ''
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%Y年%m月%d日')
    except:
        return date_str


def get_today():
    """
    获取今天的日期字符串
    :return: YYYY-MM-DD格式的日期字符串
    """
    return datetime.now().strftime('%Y-%m-%d')


def get_current_month():
    """
    获取当前年月
    :return: YYYY-MM格式的年月字符串
    """
    return datetime.now().strftime('%Y-%m')


def generate_date_range(start_date, end_date):
    """
    生成日期范围
    :param start_date: 开始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :return: 日期列表
    """
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    delta = end - start
    return [(start + timedelta(days=i)).strftime('%Y-%m-%d') 
            for i in range(delta.days + 1)]


def validate_file_upload(file):
    """
    验证上传的文件
    :param file: 上传的文件对象
    :return: (is_valid, error_message) 元组
    """
    if not file:
        return False, '请选择文件'
    
    if file.filename == '':
        return False, '文件名为空'
    
    # 检查文件扩展名
    allowed_extensions = {'xlsx', 'xls'}
    if not ('.' in file.filename and 
            file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return False, '只支持Excel文件（.xlsx, .xls）'
    
    return True, None


def safe_float(value, default=0.0):
    """
    安全地将值转换为浮点数
    :param value: 要转换的值
    :param default: 默认值
    :return: 浮点数
    """
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    """
    安全地将值转换为整数
    :param value: 要转换的值
    :param default: 默认值
    :return: 整数
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def get_client_ip():
    """
    获取客户端IP地址
    :return: IP地址字符串
    """
    from flask import request
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr


def log_action(action, user_id=None, details=None):
    """
    记录用户操作日志
    :param action: 操作类型
    :param user_id: 用户ID
    :param details: 详细信息
    """
    import os
    from datetime import datetime
    
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] "
    
    if user_id:
        log_entry += f"User ID: {user_id} "
    
    log_entry += f"- Action: {action}"
    
    if details:
        log_entry += f" - Details: {details}"
    
    log_entry += "\n"
    
    # 写入日志文件
    log_file = f"logs/action_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)


class Pagination:
    """
    简单的分页类
    """
    
    def __init__(self, page, per_page=20, total_count=0):
        """
        初始化分页
        :param page: 当前页码
        :param per_page: 每页数量
        :param total_count: 总记录数
        """
        self.page = safe_int(page, 1)
        self.per_page = per_page
        self.total_count = total_count
        
        # 计算总页数
        self.total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        
        # 限制页码范围
        if self.page < 1:
            self.page = 1
        elif self.page > self.total_pages:
            self.page = self.total_pages
    
    @property
    def offset(self):
        """计算偏移量"""
        return (self.page - 1) * self.per_page
    
    @property
    def has_prev(self):
        """是否有上一页"""
        return self.page > 1
    
    @property
    def has_next(self):
        """是否有下一页"""
        return self.page < self.total_pages
    
    @property
    def prev_num(self):
        """上一页页码"""
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_num(self):
        """下一页页码"""
        return self.page + 1 if self.has_next else None
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
        """
        生成页码迭代器
        :param left_edge: 左侧边缘页码数
        :param left_current: 当前页左侧页码数
        :param right_current: 当前页右侧页码数
        :param right_edge: 右侧边缘页码数
        """
        last = self.total_pages
        for num in range(1, last + 1):
            if num <= left_edge or \
               (self.page - left_current - 1 < num < self.page + right_current) or \
               num > last - right_edge:
                yield num
