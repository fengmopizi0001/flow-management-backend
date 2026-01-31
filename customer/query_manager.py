"""
查询管理模块 - 客户功能
处理流水记录的多条件查询
"""

from flask import Blueprint, render_template, request, jsonify, session
from functools import wraps
from database import get_db, close_db

query_bp = Blueprint('query', __name__, url_prefix='/customer/query')


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        if session.get('role') != 'customer':
            return "权限不足", 403
        return f(*args, **kwargs)
    return decorated_function


@query_bp.route('/')
@login_required
def index():
    """查询页面"""
    customer_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取所有操作员列表（用于筛选）
        cursor.execute('''
            SELECT DISTINCT o.id, o.name
            FROM operators o
            WHERE (o.customer_id = ? OR o.customer_id IS NULL) AND o.is_active = 1
            ORDER BY o.name
        ''', (customer_id,))
        operators = cursor.fetchall()
        
        # 获取所有支付渠道列表（用于筛选）
        cursor.execute('''
            SELECT DISTINCT pc.id, pc.name
            FROM payment_channels pc
            JOIN operators o ON pc.operator_id = o.id
            WHERE (o.customer_id = ? OR o.customer_id IS NULL) AND pc.is_active = 1
            ORDER BY pc.name
        ''', (customer_id,))
        channels = cursor.fetchall()
        
        return render_template('customer/query.html', 
                             operators=operators, 
                             channels=channels)
    finally:
        close_db(conn)


@query_bp.route('/search', methods=['POST'])
@login_required
def search():
    """执行查询"""
    customer_id = session['user_id']
    data = request.get_json()
    
    # 获取筛选参数
    start_date = data.get('start_date', '')
    end_date = data.get('end_date', '')
    operator_id = data.get('operator_id', '')
    channel_id = data.get('channel_id', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 构建查询（默认只显示已刷流水）
        query = '''
            SELECT dr.*, o.name as operator_name, pc.name as channel_name
            FROM daily_records dr
            LEFT JOIN operators o ON dr.operator_id = o.id
            LEFT JOIN payment_channels pc ON dr.channel_id = pc.id
            WHERE dr.customer_id = ? AND dr.is_daily_summary = 0 AND dr.status = 'done'
        '''
        params = [customer_id]
        
        # 日期筛选
        if start_date:
            query += ' AND dr.date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND dr.date <= ?'
            params.append(end_date)
        
        # 操作员筛选
        if operator_id:
            if operator_id == 'self':
                # 查询"自己"的记录（operator_id = 999）
                query += ' AND dr.operator_id = ?'
                params.append(999)
            else:
                query += ' AND dr.operator_id = ?'
                params.append(operator_id)
        
        # 支付渠道筛选
        if channel_id and channel_id != '0':
            # 0表示不选择渠道，不添加筛选条件
            query += ' AND dr.channel_id = ?'
            params.append(channel_id)
        
        query += ' ORDER BY dr.date ASC'
        
        cursor.execute(query, params)
        records = cursor.fetchall()
        
        # 统计数据
        total_amount = sum(r['amount'] for r in records) if records else 0
        completed_amount = sum(r['amount'] for r in records if r['status'] == 'done') if records else 0
        pending_amount = sum(r['amount'] for r in records if r['status'] == 'pending') if records else 0
        
        # 格式化结果
        results = []
        for record in records:
            # 操作员显示逻辑
            operator_name = None
            if record['operator_id'] == 999:
                operator_name = '自己'
            elif record['operator_id'] is not None:
                operator_name = record['operator_name'] or None
            else:
                operator_name = None
            
            # 渠道显示逻辑（1=微信, 2=支付宝, 3=其他）
            channel_name = None
            if record['channel_id'] is not None:
                if record['channel_id'] == 0:
                    channel_name = None  # 0表示不选择
                elif record['channel_id'] == 1:
                    channel_name = '微信支付'
                elif record['channel_id'] == 2:
                    channel_name = '支付宝'
                elif record['channel_id'] == 3:
                    channel_name = '其他渠道'
                else:
                    channel_name = None
            else:
                channel_name = None
            
            results.append({
                'id': record['id'],
                'date': record['date'],
                'amount': record['amount'],
                'status': record['status'],
                'operator': operator_name,
                'channel': channel_name or '-',
                'daily_total': record['daily_total']
            })
        
        return jsonify({
            'success': True,
            'records': results,
            'stats': {
                'total_count': len(records),
                'total_amount': total_amount,
                'completed_amount': completed_amount,
                'pending_amount': pending_amount
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        close_db(conn)
