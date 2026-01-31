"""
操作员管理模块 - 管理员功能
处理操作员和支付渠道的增删改查
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from database import get_db, close_db

operator_bp = Blueprint('operator', __name__, url_prefix='/admin/operators')


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            return "权限不足", 403
        return f(*args, **kwargs)
    return decorated_function


@operator_bp.route('/')
@login_required
def index():
    """操作员管理主页"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取所有操作员及其支付渠道
        cursor.execute('''
            SELECT o.*, 
                   GROUP_CONCAT(pc.name) as channels
            FROM operators o
            LEFT JOIN payment_channels pc ON o.id = pc.operator_id
            GROUP BY o.id
            ORDER BY o.created_at DESC
        ''')
        operators = cursor.fetchall()
        
        return render_template('admin/operators.html', operators=operators)
    finally:
        close_db(conn)


@operator_bp.route('/add', methods=['POST'])
@login_required
def add_operator():
    """添加操作员"""
    data = request.get_json()
    name = data.get('name', '').strip()
    customer_id = data.get('customer_id')  # 可选，为空表示全局操作员
    
    if not name:
        return jsonify({'success': False, 'error': '操作员名称不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查是否已存在同名操作员
        cursor.execute('SELECT id FROM operators WHERE name = ?', (name,))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': '操作员已存在'}), 400
        
        # 添加操作员
        cursor.execute(
            'INSERT INTO operators (name, customer_id) VALUES (?, ?)',
            (name, customer_id)
        )
        operator_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({
            'success': True,
            'operator_id': operator_id,
            'message': '操作员添加成功'
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        close_db(conn)


@operator_bp.route('/<int:operator_id>/delete', methods=['POST'])
@login_required
def delete_operator(operator_id):
    """删除操作员"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 先删除关联的支付渠道
        cursor.execute('DELETE FROM payment_channels WHERE operator_id = ?', (operator_id,))
        
        # 删除操作员
        cursor.execute('DELETE FROM operators WHERE id = ?', (operator_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': '操作员删除成功'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        close_db(conn)


@operator_bp.route('/<int:operator_id>/channels/add', methods=['POST'])
@login_required
def add_channel(operator_id):
    """为操作员添加支付渠道"""
    data = request.get_json()
    channel_name = data.get('name', '').strip()
    
    if not channel_name:
        return jsonify({'success': False, 'error': '渠道名称不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查该操作员是否已有同名渠道
        cursor.execute(
            'SELECT id FROM payment_channels WHERE operator_id = ? AND name = ?',
            (operator_id, channel_name)
        )
        if cursor.fetchone():
            return jsonify({'success': False, 'error': '该渠道已存在'}), 400
        
        # 添加支付渠道
        cursor.execute(
            'INSERT INTO payment_channels (name, operator_id) VALUES (?, ?)',
            (channel_name, operator_id)
        )
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '支付渠道添加成功'
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        close_db(conn)


@operator_bp.route('/channels/<int:channel_id>/delete', methods=['POST'])
@login_required
def delete_channel(channel_id):
    """删除支付渠道"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM payment_channels WHERE id = ?', (channel_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': '支付渠道删除成功'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        close_db(conn)


@operator_bp.route('/api/list/<int:customer_id>')
@login_required
def api_list_customer_operators(customer_id):
    """获取指定客户的操作员列表API"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT o.id, o.name, 
                   GROUP_CONCAT(pc.id || ':' || pc.name) as channels
            FROM operators o
            LEFT JOIN payment_channels pc ON o.id = pc.operator_id
            WHERE (o.customer_id = ? OR o.customer_id IS NULL) AND o.is_active = 1
            GROUP BY o.id
            ORDER BY o.name
        ''', (customer_id,))
        
        operators = []
        for row in cursor.fetchall():
            operator = {
                'id': row['id'],
                'name': row['name'],
                'channels': []
            }
            
            # 解析渠道
            if row['channels']:
                for channel_str in row['channels'].split(','):
                    parts = channel_str.split(':')
                    if len(parts) >= 2:
                        operator['channels'].append({
                            'id': int(parts[0]),
                            'name': parts[1]
                        })
            
            operators.append(operator)
            
        return jsonify({'operators': operators})
    finally:
        close_db(conn)


@operator_bp.route('/api/list')
@login_required
def api_list_operators():
    """获取操作员列表API"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT o.id, o.name, 
                   GROUP_CONCAT(pc.id || ':' || pc.name) as channels
            FROM operators o
            LEFT JOIN payment_channels pc ON o.id = pc.operator_id
            WHERE o.is_active = 1
            GROUP BY o.id
            ORDER BY o.name
        ''')
        
        operators = []
        for row in cursor.fetchall():
            operator = {
                'id': row['id'],
                'name': row['name']
            }
            
            # 解析渠道
            if row['channels']:
                channels = []
                for channel_str in row['channels'].split(','):
                    channel_id, channel_name = channel_str.split(':')
                    channels.append({
                        'id': int(channel_id),
                        'name': channel_name
                    })
                operator['channels'] = channels
            else:
                operator['channels'] = []
            
            operators.append(operator)
        
        return jsonify({'operators': operators})
    finally:
        close_db(conn)


@operator_bp.route('/stats')
@login_required
def stats():
    """操作员统计页面"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取每个操作员的统计信息
        cursor.execute('''
            SELECT 
                o.id,
                o.name,
                COUNT(dr.id) as total_records,
                SUM(CASE WHEN dr.status = 'done' THEN dr.amount ELSE 0 END) as completed_amount,
                SUM(CASE WHEN dr.status = 'pending' THEN dr.amount ELSE 0 END) as pending_amount,
                COUNT(CASE WHEN dr.status = 'done' THEN 1 END) as completed_count
            FROM operators o
            LEFT JOIN daily_records dr ON o.id = dr.operator_id
            WHERE o.is_active = 1
            GROUP BY o.id
            ORDER BY completed_amount DESC
        ''')
        
        stats = cursor.fetchall()
        
        return render_template('admin/operator_stats.html', stats=stats)
    finally:
        close_db(conn)




