"""
数据库升级脚本 - 添加操作员和支付渠道功能
执行此脚本来升级现有数据库
"""

import sqlite3
import os
from config import Config


def upgrade_database():
    """升级数据库，添加操作员和支付渠道表"""
    
    print("=" * 60)
    print("数据库升级脚本 - 添加操作员和支付渠道功能")
    print("=" * 60)
    
    if not os.path.exists(Config.DATABASE_PATH):
        print(f"[ERROR] 数据库文件不存在: {Config.DATABASE_PATH}")
        return
    
    # 备份数据库
    print("\n[步骤1] 备份数据库...")
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'data/flow_backup_before_upgrade_{timestamp}.db'
    
    import shutil
    shutil.copy2(Config.DATABASE_PATH, backup_path)
    print(f"[成功] 数据库已备份到: {backup_path}")
    
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operators'")
        if cursor.fetchone():
            print("[警告] operators表已存在，跳过创建")
        else:
            # 创建操作员表
            print("\n[步骤2] 创建operators表...")
            cursor.execute('''
                CREATE TABLE operators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    customer_id INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES users(id)
                )
            ''')
            print("[成功] operators表创建完成")
        
        # 检查支付渠道表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payment_channels'")
        if cursor.fetchone():
            print("[警告] payment_channels表已存在，跳过创建")
        else:
            # 创建支付渠道表
            print("\n[步骤3] 创建payment_channels表...")
            cursor.execute('''
                CREATE TABLE payment_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    operator_id INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (operator_id) REFERENCES operators(id)
                )
            ''')
            print("[成功] payment_channels表创建完成")
        
        # 检查daily_records表是否有新字段
        cursor.execute("PRAGMA table_info(daily_records)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'operator_id' not in columns:
            print("\n[步骤4] 为daily_records表添加operator_id字段...")
            cursor.execute('ALTER TABLE daily_records ADD COLUMN operator_id INTEGER')
            print("[成功] operator_id字段添加完成")
        else:
            print("[警告] operator_id字段已存在，跳过添加")
        
        if 'channel_id' not in columns:
            print("\n[步骤5] 为daily_records表添加channel_id字段...")
            cursor.execute('ALTER TABLE daily_records ADD COLUMN channel_id INTEGER')
            print("[成功] channel_id字段添加完成")
        else:
            print("[警告] channel_id字段已存在，跳过添加")
        
        # 提交更改
        conn.commit()
        
        print("\n" + "=" * 60)
        print("[成功] 数据库升级完成！")
        print("=" * 60)
        print("\n数据库结构已更新为：")
        print("- operators表：存储操作员信息")
        print("- payment_channels表：存储支付渠道信息")
        print("- daily_records表：添加了operator_id和channel_id字段")
        print("\n下一步：")
        print("1. 在管理员界面添加操作员和支付渠道")
        print("2. 使用新的选择操作人对话框")
        
    except Exception as e:
        conn.rollback()
        print(f"\n[错误] 数据库升级失败: {e}")
        print(f"数据库已回滚，备份文件: {backup_path}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    upgrade_database()
