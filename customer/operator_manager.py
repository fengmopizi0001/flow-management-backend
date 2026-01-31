"""
操作员管理模块 - 客户功能
处理客户自己的操作员和支付渠道管理
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from database import get_db, close_db

operator_bp = Blueprint('customer_operator', __name__, url_prefix='/customer/operators')


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') != 'customer':
            return "权限不足", 403
        return f(*args, **kwargs)
    return decorated_function


@operator_bp.route('/')
@login_required
def index():
    """操作员管理主页"""
    customer_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取当前客户的所有操作员及其支付渠道
        cursor.execute('''
            SELECT o.*, 
                   GROUP_CONCAT(pc.id || ':' || pc.name) as channels
            FROM operators o
            LEFT JOIN payment_channels pc ON o.id = pc.operator_id
            WHERE o.customer_id = ? OR o.customer_id IS NULL
            GROUP BY o.id
            ORDER BY o.created_at DESC
        ''', (customer_id,))
        
        operators = cursor.fetchall()
        
        return render_template('customer/operators.html', operators=operators)
    finally:
        close_db(conn)


@operator_bp.route('/add', methods=['POST'])
@login_required
def add_operator():
    """添加操作员"""
    customer_id = session['user_id']
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'success': False, 'error': '操作员名称不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查该客户是否已有同名操作员
        cursor.execute(
            'SELECT id FROM operators WHERE customer_id = ? AND name = ?',
            (customer_id, name)
        )
        if cursor.fetchone():
            return jsonify({'success': False, 'error': '操作员已存在'}), 400
        
        # 添加操作员（归属当前客户）
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
    customer_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 验证操作员是否属于当前客户
        cursor.execute(
            'SELECT customer_id FROM operators WHERE id = ?',
            (operator_id,)
        )
        operator = cursor.fetchone()
        
        if not operator or operator['customer_id'] != customer_id:
            return jsonify({'success': False, 'error': '无权删除此操作员'}), 403
        
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
    customer_id = session['user_id']
    data = request.get_json()
    channel_name = data.get('name', '').strip()
    
    if not channel_name:
        return jsonify({'success': False, 'error': '渠道名称不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 验证操作员是否属于当前客户
        cursor.execute(
            'SELECT customer_id FROM operators WHERE id = ?',
            (operator_id,)
        )
        operator = cursor.fetchone()
        
        if not operator or operator['customer_id'] != customer_id:
            return jsonify({'success': False, 'error': '无权操作此操作员'}), 403
        
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
    customer_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 验证渠道是否属于当前客户的操作员
        cursor.execute('''
            SELECT o.customer_id 
            FROM payment_channels pc
            JOIN operators o ON pc.operator_id = o.id
            WHERE pc.id = ?
        ''', (channel_id,))
        
        channel = cursor.fetchone()
        if not channel or channel['customer_id'] != customer_id:
            return jsonify({'success': False, 'error': '无权删除此渠道'}), 403
        
        cursor.execute('DELETE FROM payment_channels WHERE id = ?', (channel_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': '支付渠道删除成功'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        close_db(conn)


@operator_bp.route('/api/list')
@login_required
def api_list_operators():
    """获取当前客户的操作员列表API"""
    customer_id = session['user_id']
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


# 导出蓝图
customer_operator_bp = operator_bp
