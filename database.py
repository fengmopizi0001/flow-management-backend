"""
数据库管理模块 - 流水管理系统
处理所有数据库连接和操作
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from config import Config


def get_db():
    """
    获取数据库连接
    使用Row工厂，使结果可以像字典一样访问
    """
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def close_db(conn):
    """关闭数据库连接"""
    if conn:
        conn.close()


def init_db():
    """
    初始化数据库
    创建所有必要的表和默认数据
    """
    # 确保数据目录存在
    if not os.path.exists('data'):
        os.makedirs('data')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'customer')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建月度目标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                year_month TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                target_amount REAL NOT NULL,
                period_number INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES users(id)
            )
        ''')
        
        # 检查是否需要迁移period_number字段
        try:
            cursor.execute('SELECT period_number FROM monthly_targets LIMIT 1')
        except sqlite3.OperationalError:
            print("Running migration: adding period_number to monthly_targets")
            cursor.execute('ALTER TABLE monthly_targets ADD COLUMN period_number INTEGER DEFAULT 1')
            conn.commit()
        
        # 创建流水记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                daily_total REAL,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'done')),
                operator TEXT,
                operator_id INTEGER,
                channel_id INTEGER,
                is_daily_summary INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES users(id),
                FOREIGN KEY (operator_id) REFERENCES operators(id),
                FOREIGN KEY (channel_id) REFERENCES payment_channels(id)
            )
        ''')
        
        # 创建操作员表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                customer_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES users(id)
            )
        ''')
        
        # 创建支付渠道表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                operator_id INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (operator_id) REFERENCES operators(id)
            )
        ''')
        
        # 创建索引以提高查询性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_records_customer_date 
            ON daily_records(customer_id, date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_records_status 
            ON daily_records(status)
        ''')
        
        # 创建默认管理员账户
        try:
            admin_hash = generate_password_hash('admin123')
            cursor.execute(
                'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                ('admin', admin_hash, 'admin')
            )
            print("[INFO] 默认管理员账户已创建: admin / admin123")
        except sqlite3.IntegrityError:
            print("[INFO] 管理员账户已存在，跳过创建")
        
        conn.commit()
        print("[INFO] 数据库初始化完成")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 数据库初始化失败: {e}")
        raise
    finally:
        conn.close()


def backup_database(backup_path=None):
    """
    备份数据库
    :param backup_path: 备份文件路径，如果为None则自动生成
    :return: 备份文件路径
    """
    import shutil
    from datetime import datetime
    
    if backup_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'data/flow_backup_{timestamp}.db'
    
    # 确保备份目录存在
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    
    # 复制数据库文件
    shutil.copy2(Config.DATABASE_PATH, backup_path)
    print(f"[INFO] 数据库已备份到: {backup_path}")
    
    return backup_path


class DatabaseManager:
    """
    数据库管理器类
    提供更高级的数据库操作接口
    """
    
    def __init__(self):
        self.conn = None
    
    def __enter__(self):
        """上下文管理器入口"""
        self.conn = get_db()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        close_db(self.conn)
    
    def execute(self, query, params=None):
        """
        执行SQL查询
        :param query: SQL查询语句
        :param params: 查询参数
        :return: cursor对象
        """
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    def fetchone(self, query, params=None):
        """获取单条记录"""
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def fetchall(self, query, params=None):
        """获取所有记录"""
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def insert(self, table, data):
        """
        插入数据
        :param table: 表名
        :param data: 字典形式的数据
        :return: 插入的记录ID
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
        
        cursor = self.execute(query, tuple(data.values()))
        return cursor.lastrowid
    
    def update(self, table, data, where_clause, where_params=None):
        """
        更新数据
        :param table: 表名
        :param data: 字典形式的数据
        :param where_clause: WHERE子句
        :param where_params: WHERE参数
        :return: 影响的行数
        """
        set_clause = ', '.join([f'{k} = ?' for k in data.keys()])
        query = f'UPDATE {table} SET {set_clause} WHERE {where_clause}'
        
        params = list(data.values())
        if where_params:
            params.extend(where_params)
        
        cursor = self.execute(query, params)
        return cursor.rowcount
    
    def delete(self, table, where_clause, where_params=None):
        """
        删除数据
        :param table: 表名
        :param where_clause: WHERE子句
        :param where_params: WHERE参数
        :return: 影响的行数
        """
        query = f'DELETE FROM {table} WHERE {where_clause}'
        cursor = self.execute(query, where_params)
        return cursor.rowcount
