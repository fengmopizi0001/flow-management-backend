"""
客户路由 - 流水管理系统
处理客户仪表盘、流水记录查看等功能
"""

from flask import render_template, request, session, Blueprint
from database import get_db, close_db
from utils import require_customer, parse_date_range_from_request

# 创建客户蓝图
customer_bp = Blueprint('customer', __name__)

# 装饰器
def login_required(f):
    """登录验证装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        if session.get('role') != 'customer':
            return "权限不足", 403
        return f(*args, **kwargs)
    return decorated_function


@customer_bp.route('/')
@customer_bp.route('/dashboard')
@login_required
def dashboard():
    """
    客户仪表盘
    显示客户自己的流水统计和目标完成情况
    """
    user_id = session.get('user_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取用户基本信息
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        # 获取最近的月度目标
        cursor.execute('''
            SELECT * FROM monthly_targets 
            WHERE customer_id = ? 
            ORDER BY period_number DESC LIMIT 1
        ''', (user_id,))
        latest_target = cursor.fetchone()
        
        stats = None
        progress = 0
        
        if latest_target:
            # 获取目标期间的流水统计（限制日期范围）
            cursor.execute('''
                SELECT SUM(CASE WHEN status = 'done' THEN amount ELSE 0 END) as completed,
                       COUNT(CASE WHEN status = 'done' THEN 1 END) as completed_count,
                       SUM(amount) as total,
                       COUNT(*) as total_count
                FROM daily_records 
                WHERE customer_id = ? 
                AND date >= ? AND date <= ?
                AND is_daily_summary = 0
            ''', (user_id, latest_target['start_date'], latest_target['end_date']))
            
            stats = cursor.fetchone()
            
            # 调试信息
            print(f"[DEBUG] 客户ID: {user_id}")
            print(f"[DEBUG] 最新目标: {latest_target}")
            print(f"[DEBUG] 统计结果: {stats}")
            
            if stats and latest_target['target_amount'] and latest_target['target_amount'] > 0:
                completed_amount = stats['completed'] or 0
                target_amount = latest_target['target_amount']
                progress = round((completed_amount / target_amount) * 100, 2)
                print(f"[DEBUG] 已刷流水: {completed_amount}, 目标金额: {target_amount}, 进度: {progress}%")
            else:
                print(f"[DEBUG] 无法计算进度: stats={stats}, target_amount={latest_target['target_amount']}")
        
        # 获取最近的流水记录（限制显示最新20条）
        cursor.execute('''
            SELECT * FROM daily_records 
            WHERE customer_id = ? 
            AND is_daily_summary = 0
            ORDER BY date DESC 
            LIMIT 20
        ''', (user_id,))
        recent_records = cursor.fetchall()
        
        return render_template('customer/dashboard.html',
                             user=user,
                             latest_target=latest_target,
                             stats=stats,
                             progress=progress,
                             recent_records=recent_records)
    
    finally:
        close_db(conn)


@customer_bp.route('/records')
@login_required
def records():
    """
    客户流水记录查看
    显示客户自己的所有流水记录，支持筛选
    """
    user_id = session.get('user_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取筛选参数
        start_date, end_date = parse_date_range_from_request(request)
        status_filter = request.args.get('status', '')
        
        # 获取最近的月度目标
        cursor.execute('''
            SELECT * FROM monthly_targets 
            WHERE customer_id = ? 
            ORDER BY year_month DESC LIMIT 1
        ''', (user_id,))
        target = cursor.fetchone()
        
        # 构建查询
        query = '''
            SELECT * FROM daily_records 
            WHERE customer_id = ? AND is_daily_summary = 0
        '''
        params = [user_id]
        
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
            
        if status_filter:
            query += ' AND status = ?'
            params.append(status_filter)
        
        query += ' ORDER BY date ASC'
        
        # 调试信息
        print(f"[DEBUG] SQL查询: {query}")
        print(f"[DEBUG] 参数: {params}")
        print(f"[DEBUG] start_date={start_date}, end_date={end_date}, status_filter={status_filter}")
        
        cursor.execute(query, params)
        records = cursor.fetchall()
        
        # 为每条记录添加操作员和渠道信息
        records_with_info = []
        for record in records:
            record_dict = dict(record)
            
            # 操作员显示逻辑
            if record['operator_id'] == 999:
                record_dict['operator_name'] = '自己'
            elif record['operator_id'] is not None:
                cursor.execute('SELECT name FROM operators WHERE id = ?', (record['operator_id'],))
                op = cursor.fetchone()
                record_dict['operator_name'] = op['name'] if op else None
            else:
                record_dict['operator_name'] = None
            
            # 渠道显示逻辑（1=微信, 2=支付宝, 3=其他）
            if record['channel_id'] is not None:
                if record['channel_id'] == 0:
                    record_dict['channel_name'] = None  # 0表示不选择
                elif record['channel_id'] == 1:
                    record_dict['channel_name'] = '微信支付'
                elif record['channel_id'] == 2:
                    record_dict['channel_name'] = '支付宝'
                elif record['channel_id'] == 3:
                    record_dict['channel_name'] = '其他渠道'
                else:
                    record_dict['channel_name'] = None
            else:
                record_dict['channel_name'] = None
            
            records_with_info.append(record_dict)
        
        records = records_with_info
        
        # 调试：打印前5条和后5条记录的日期
        print(f"[DEBUG] 查询结果数量: {len(records)}")
        print(f"[DEBUG] 前5条记录:")
        for i, record in enumerate(records[:5]):
            print(f"[DEBUG]   记录{i+1}: 日期={record['date']}, 金额={record['amount']}")
        if len(records) > 5:
            print(f"[DEBUG] 后5条记录:")
            for i, record in enumerate(records[-5:]):
                print(f"[DEBUG]   记录{len(records)-4+i}: 日期={record['date']}, 金额={record['amount']}")
        
        return render_template('customer/records.html',
                             records=records,
                             target=target,
                             status_filter=status_filter,
                             start_date=start_date,
                             end_date=end_date)
    
    finally:
        close_db(conn)


@customer_bp.route('/operators')
@login_required
def operators():
    """
    操作员管理页面
    """
    # 这个函数会自动调用customer/operator_manager.py中的路由
    from flask import redirect, url_for
    return redirect(url_for('customer_operator.index'))


@customer_bp.route('/query')
@login_required
def query():
    """
    查询流水页面
    """
    # 这个函数会自动调用customer/query_manager.py中的路由
    from flask import redirect, url_for
    return redirect(url_for('query.index'))
