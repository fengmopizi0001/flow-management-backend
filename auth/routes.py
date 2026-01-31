"""
认证路由 - 流水管理系统
处理用户登录、登出、密码修改等功能
"""

from flask import render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db, close_db
from utils import log_action


def login():
    """
    用户登录
    GET: 显示登录页面
    POST: 处理登录请求
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # 查询用户
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            # 验证密码
            if user and check_password_hash(user['password_hash'], password):
                # 设置会话
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                
                # 记录登录日志
                log_action('LOGIN', user['id'], f'用户 {username} 登录成功')
                
                # 根据角色重定向
                if user['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('customer.dashboard'))
            else:
                # 登录失败
                log_action('LOGIN_FAILED', details=f'用户 {username} 登录失败')
                return render_template('login.html', error='用户名或密码错误')
        
        finally:
            close_db(conn)
    
    return render_template('login.html')


def logout():
    """
    用户登出
    清除会话并重定向到登录页
    """
    user_id = session.get('user_id')
    username = session.get('username')
    
    # 记录登出日志
    log_action('LOGOUT', user_id, f'用户 {username} 登出')
    
    # 清除会话
    session.clear()
    
    return redirect(url_for('auth.login'))


def change_password():
    """
    修改密码
    用户可以修改自己的密码
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    # 验证输入
    if not old_password or not new_password:
        return jsonify({'success': False, 'error': '请输入旧密码和新密码'})
    
    # 验证新密码长度
    if len(new_password) < 6:
        return jsonify({'success': False, 'error': '新密码长度至少为6位'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取用户信息
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'})
        
        # 验证旧密码
        if not check_password_hash(user['password_hash'], old_password):
            log_action('PASSWORD_CHANGE_FAILED', session['user_id'], 
                      f'用户 {session.get("username")} 修改密码失败：旧密码错误')
            return jsonify({'success': False, 'error': '旧密码错误'})
        
        # 生成新密码哈希
        new_password_hash = generate_password_hash(new_password)
        
        # 更新密码
        cursor.execute(
            'UPDATE users SET password_hash = ? WHERE id = ?', 
            (new_password_hash, session['user_id'])
        )
        
        conn.commit()
        
        # 记录成功日志
        log_action('PASSWORD_CHANGED', session['user_id'], 
                  f'用户 {session.get("username")} 修改密码成功')
        
        return jsonify({'success': True, 'message': '密码修改成功'})
    
    except Exception as e:
        conn.rollback()
        log_action('PASSWORD_CHANGE_ERROR', session['user_id'], 
                  f'用户 {session.get("username")} 修改密码出错：{str(e)}')
        return jsonify({'success': False, 'error': str(e)})
    
    finally:
        close_db(conn)


def change_username():
    """
    修改用户名
    仅管理员可以修改自己的用户名
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    # 只有管理员可以修改用户名
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'error': '只有管理员可以修改用户名'})
    
    data = request.get_json()
    new_username = data.get('new_username')
    password = data.get('password')
    
    # 验证输入
    if not new_username or not password:
        return jsonify({'success': False, 'error': '请输入新用户名和密码'})
    
    # 验证用户名格式
    if len(new_username) < 3 or len(new_username) > 20:
        return jsonify({'success': False, 'error': '用户名长度应为3-20位'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取当前用户信息
        cursor.execute(
            'SELECT username, password_hash FROM users WHERE id = ?', 
            (session['user_id'],)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'})
        
        # 验证密码
        if not check_password_hash(user['password_hash'], password):
            log_action('USERNAME_CHANGE_FAILED', session['user_id'], 
                      f'用户 {session.get("username")} 修改用户名失败：密码错误')
            return jsonify({'success': False, 'error': '密码错误'})
        
        # 检查新用户名是否已存在
        cursor.execute('SELECT id FROM users WHERE username = ?', (new_username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return jsonify({'success': False, 'error': '该用户名已被使用'})
        
        old_username = session.get('username')
        
        # 更新用户名
        cursor.execute(
            'UPDATE users SET username = ? WHERE id = ?', 
            (new_username, session['user_id'])
        )
        
        conn.commit()
        
        # 更新session中的用户名
        session['username'] = new_username
        
        # 记录成功日志
        log_action('USERNAME_CHANGED', session['user_id'], 
                  f'用户 {old_username} 修改用户名为 {new_username}')
        
        return jsonify({'success': True, 'message': f'用户名已修改为 {new_username}'})
    
    except Exception as e:
        conn.rollback()
        log_action('USERNAME_CHANGE_ERROR', session['user_id'], 
                  f'用户 {session.get("username")} 修改用户名出错：{str(e)}')
        return jsonify({'success': False, 'error': str(e)})
    
    finally:
        close_db(conn)
