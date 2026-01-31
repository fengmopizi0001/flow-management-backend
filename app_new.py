"""
流水管理系统 - 主应用文件
模块化重构版本
"""

from flask import Flask, render_template, session
from flask_cors import CORS
from config import config
from database import init_db
import os
import logging
from logging.handlers import RotatingFileHandler

    # 创建Flask应用
def create_app(config_name='default'):
    """
    应用工厂函数
    :param config_name: 配置名称 ('development', 'production', 'testing')
    :return: Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化数据库
    with app.app_context():
        init_db()
    
    # 配置日志
    setup_logging(app)
    
    # 配置CORS（跨域支持）
    # 开发环境：允许所有来源
    # 生产环境：仅允许配置的来源
    if config_name == 'development':
        CORS(app, resources={
            r"/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            }
        })
    else:
        # 生产环境：从配置读取允许的来源
        allowed_origins = app.config.get('CORS_ORIGINS', [])
        CORS(app, resources={
            r"/*": {
                "origins": allowed_origins if allowed_origins else ["*"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            }
        })
    
    # 注册蓝图
    from auth import auth_bp
    from admin import admin_bp
    from customer import customer_bp
    from admin.operator_manager import operator_bp
    from customer.operator_manager import customer_operator_bp
    from customer.query_manager import query_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(operator_bp)
    app.register_blueprint(customer_operator_bp)
    app.register_blueprint(query_bp)
    
    # 注册错误处理器
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    # 注册上下文处理器
    @app.context_processor
    def inject_user():
        """注入用户信息到所有模板"""
        return dict(
            user=session.get('username'),
            role=session.get('role')
        )
    
    # 首页路由 - 重定向到登录页
    @app.route('/')
    def index():
        if 'user_id' in session:
            if session.get('role') == 'admin':
                from flask import redirect, url_for
                return redirect(url_for('admin.dashboard'))
            else:
                from flask import redirect, url_for
                return redirect(url_for('customer.dashboard'))
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    # API路由 - 获取操作人列表
    @app.route('/api/operators')
    def get_operators():
        """获取历史操作人列表"""
        from flask import jsonify
        from database import get_db, close_db
        
        # 检查登录状态
        if 'user_id' not in session:
            return jsonify({'operators': []})
            
        customer_id = session.get('user_id')
        role = session.get('role')
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # 从daily_records表中获取所有不重复的操作人
            if role == 'customer':
                cursor.execute('''
                    SELECT DISTINCT operator FROM daily_records 
                    WHERE operator IS NOT NULL AND operator != '' 
                    AND customer_id = ?
                    ORDER BY operator DESC
                    LIMIT 50
                ''', (customer_id,))
            else:
                # 管理员可以看到所有
                cursor.execute('''
                    SELECT DISTINCT operator FROM daily_records 
                    WHERE operator IS NOT NULL AND operator != ''
                    ORDER BY operator DESC
                    LIMIT 50
                ''')
                
            operators = [row['operator'] for row in cursor.fetchall()]
            
            return jsonify({'operators': operators})
        finally:
            close_db(conn)
    
    # API路由 - 更新操作人和状态（旧版，保留兼容）
    @app.route('/api/update_operator', methods=['POST'])
    def update_operator():
        """更新流水记录的操作人和状态"""
        from flask import request, jsonify
        from database import get_db, close_db
        
        data = request.get_json()
        record_id = data.get('record_id')
        operator = data.get('operator')
        status = data.get('status')
        
        if not record_id or not status:
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400
        
        # 如果operator为空字符串，转为None
        if operator == '':
            operator = None
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # 更新记录
            cursor.execute('''
                UPDATE daily_records 
                SET operator = ?, status = ?
                WHERE id = ?
            ''', (operator, status, record_id))
            
            conn.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            close_db(conn)
    
    # API路由 - 更新记录（新版，支持操作员和渠道）
    @app.route('/api/update_record', methods=['POST'])
    def update_record():
        """更新流水记录的操作员、渠道和状态"""
        from flask import request, jsonify, session
        from database import get_db, close_db
        
        data = request.get_json()
        record_id = data.get('record_id')
        status = data.get('status')
        operator_id = data.get('operator_id')
        channel_id = data.get('channel_id')
        
        if not record_id or not status:
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            if status == 'pending':
                # 取消标记，清空操作员和渠道
                cursor.execute('''
                    UPDATE daily_records 
                    SET operator_id = NULL, channel_id = NULL, status = ?
                    WHERE id = ?
                ''', (status, record_id))
            else:
                # 标记为已刷，保存操作员和渠道
                cursor.execute('''
                    UPDATE daily_records 
                    SET operator_id = ?, channel_id = ?, status = ?
                    WHERE id = ?
                ''', (operator_id, channel_id, status, record_id))
            
            conn.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            close_db(conn)
    
    # API路由 - 获取客户统计数据
    @app.route('/api/customer/<int:customer_id>/stats')
    def get_customer_stats(customer_id):
        """获取客户流水统计"""
        from flask import jsonify
        from database import get_db, close_db
        from datetime import datetime
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # 获取已完成流水
            cursor.execute('''
                SELECT SUM(amount) as completed FROM daily_records 
                WHERE customer_id = ? AND status = 'done' AND is_daily_summary = 0
            ''', (customer_id,))
            completed = cursor.fetchone()['completed'] or 0
            
            # 获取待刷流水
            cursor.execute('''
                SELECT SUM(amount) as pending FROM daily_records 
                WHERE customer_id = ? AND status = 'pending' AND is_daily_summary = 0
            ''', (customer_id,))
            pending = cursor.fetchone()['pending'] or 0
            
            # 获取总流水
            total_flow = completed + pending
            
            # 获取今日流水
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT SUM(amount) as daily FROM daily_records 
                WHERE customer_id = ? AND date = ? AND is_daily_summary = 0
            ''', (customer_id, today))
            daily_flow = cursor.fetchone()['daily'] or 0
            
            # 获取月度目标
            cursor.execute('''
                SELECT target_amount FROM monthly_targets 
                WHERE customer_id = ? ORDER BY year_month DESC LIMIT 1
            ''', (customer_id,))
            target_row = cursor.fetchone()
            target_amount = target_row['target_amount'] if target_row else 0
            
            # 计算当日完成度
            daily_completion_rate = (daily_flow / target_amount * 100) if target_amount > 0 else 0
            
            return jsonify({
                'completed_flow': completed,
                'pending_flow': pending,
                'total_flow': total_flow,
                'daily_flow': daily_flow,
                'target_amount': target_amount,
                'daily_completion_rate': daily_completion_rate
            })
        finally:
            close_db(conn)
    
    return app


def setup_logging(app):
    """
    配置应用日志
    """
    if not app.debug and not app.testing:
        # 确保日志目录存在
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # 配置文件日志处理器
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('流水管理系统启动')


# 创建应用实例
app = create_app(os.getenv('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    # 开发环境配置
    config_name = os.getenv('FLASK_CONFIG', 'development')
    print("=" * 60)
    print("流水管理系统 - 模块化版本")
    print("=" * 60)
    print(f"运行模式: {config_name}")
    print(f"数据库路径: {app.config['DATABASE_PATH']}")
    print(f"调试模式: {app.config['DEBUG']}")
    print(f"监听地址: 0.0.0.0:5000")
    print("=" * 60)
    
    if config_name == 'development':
        print("\n访问地址:")
        print("  - 本地: http://localhost:5000")
        print("  - 局域网: http://YOUR_IP:5000")
        print("\n默认管理员账户: admin / admin123")
        print("\n按 Ctrl+C 停止服务器\n")
    else:
        print("\n生产环境已启动")
        print("日志文件: logs/app.log\n")
    
    print("=" * 60)
    
    # 启动应用
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n启动失败: {str(e)}")
        import traceback
        traceback.print_exc()
