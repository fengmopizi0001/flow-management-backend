"""
客户管理模块 - 管理员功能
处理客户的添加、删除、密码重置等操作
"""

from flask import session, jsonify, request
from werkzeug.security import generate_password_hash
from database import get_db, close_db
from utils import require_admin, log_action


def add_customer():
    """
    添加新客户
    API接口，返回JSON
    """
    # 权限检查
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json() if request.is_json else request.form.to_dict()
    username = data.get('username')
    password = data.get('password', '123456')
    
    print(f"[DEBUG] 添加新用户: 用户名={username}, 密码={'已设置' if password and password != '123456' else '默认123456'}")
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查用户名是否已存在
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        existing = cursor.fetchone()
        
        if existing:
            log_action('ADD_CUSTOMER_FAILED', session['user_id'], 
                      f'用户名 {username} 已存在')
            return jsonify({'success': False, 'error': '用户名已存在'})
        
        # 创建新用户
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        ''', (username, password_hash, 'customer'))
        customer_id = cursor.lastrowid
        
        conn.commit()
        
        # 验证添加是否成功
        cursor.execute('SELECT * FROM users WHERE id = ?', (customer_id,))
        new_user = cursor.fetchone()
        
        if new_user:
            print(f"[DEBUG] 用户添加成功: ID={customer_id}")
            log_action('ADD_CUSTOMER', session['user_id'], 
                      f'添加新客户: {username}, ID: {customer_id}')
            return jsonify({'success': True, 'id': customer_id, 'username': username})
        else:
            print("[DEBUG] 警告: 无法找到刚添加的用户!")
            return jsonify({'success': False, 'error': '用户创建失败'})
    
    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        print(f"[DEBUG] 错误: {error_msg}")
        log_action('ADD_CUSTOMER_ERROR', session['user_id'], 
                  f'添加客户出错: {error_msg}')
        return jsonify({'success': False, 'error': error_msg})
    
    finally:
        close_db(conn)


def delete_user(user_id):
    """
    删除用户
    删除用户及其所有相关数据
    """
    # 权限检查
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    # 防止删除自己
    if user_id == session['user_id']:
        return jsonify({'success': False, 'error': '不能删除自己的账户'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取用户信息
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'})
        
        username = user['username']
        
        # 先删除相关流水记录
        cursor.execute('DELETE FROM daily_records WHERE customer_id = ?', (user_id,))
        records_deleted = cursor.rowcount
        
        # 删除月度目标
        cursor.execute('DELETE FROM monthly_targets WHERE customer_id = ?', (user_id,))
        targets_deleted = cursor.rowcount
        
        # 删除用户
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        
        log_action('DELETE_USER', session['user_id'], 
                  f'删除用户: {username}, ID: {user_id}, 删除记录: {records_deleted}, 删除目标: {targets_deleted}')
        
        return jsonify({
            'success': True, 
            'message': f'已删除用户 {username}，同时删除了 {records_deleted} 条流水记录和 {targets_deleted} 个目标'
        })
    
    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        log_action('DELETE_USER_ERROR', session['user_id'], 
                  f'删除用户出错: {error_msg}')
        return jsonify({'success': False, 'error': error_msg})
    
    finally:
        close_db(conn)


def reset_password(user_id):
    """
    重置客户密码
    管理员可以重置任何客户的密码
    """
    # 权限检查
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json() if request.is_json else request.form.to_dict()
    new_password = data.get('password', '123456')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取用户信息
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'})
        
        username = user['username']
        
        # 生成新密码哈希
        password_hash = generate_password_hash(new_password)
        
        # 更新密码
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                      (password_hash, user_id))
        
        conn.commit()
        
        log_action('RESET_PASSWORD', session['user_id'], 
                  f'重置用户 {username} 密码为: {new_password}')
        
        return jsonify({
            'success': True, 
            'message': f'用户 {username} 的密码已重置为 {new_password}'
        })
    
    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        log_action('RESET_PASSWORD_ERROR', session['user_id'], 
                  f'重置密码出错: {error_msg}')
        return jsonify({'success': False, 'error': error_msg})
    
    finally:
        close_db(conn)
