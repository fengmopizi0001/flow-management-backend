"""
数据库日期修复脚本
修复 monthly_targets 表中日期为空的记录
"""

from database import get_db, close_db
from datetime import datetime

def fix_empty_dates():
    """修复空日期的月度目标记录"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 先显示所有月度目标记录
        print("[INFO] 查看所有月度目标记录:")
        cursor.execute('''
            SELECT mt.id, u.username, mt.year_month, mt.start_date, mt.end_date, mt.target_amount
            FROM monthly_targets mt
            JOIN users u ON mt.customer_id = u.id
            ORDER BY mt.id DESC
        ''')
        
        all_targets = cursor.fetchall()
        for t in all_targets:
            start_repr = repr(t['start_date'])
            end_repr = repr(t['end_date'])
            print(f"  ID={t['id']}: {t['username']} | {t['year_month']} | start={start_repr}, end={end_repr} | ¥{t['target_amount']:,.0f}")
        
        # 查询所有日期为空的月度目标
        cursor.execute('''
            SELECT id, customer_id, year_month, target_amount 
            FROM monthly_targets 
            WHERE start_date IS NULL OR start_date = '' OR end_date IS NULL OR end_date = '' OR start_date = '日期' OR end_date = '日期'
        ''')
        
        empty_targets = cursor.fetchall()
        
        if not empty_targets:
            print("[INFO] 没有发现日期为空的记录，无需修复")
            return
        
        print(f"[INFO] 发现 {len(empty_targets)} 条日期为空的记录")
        
        for target in empty_targets:
            target_id = target['id']
            customer_id = target['customer_id']
            year_month = target['year_month']
            target_amount = target['target_amount']
            
            print(f"\n[INFO] 处理目标ID: {target_id}, 客户ID: {customer_id}, 年月: {year_month}")
            
            # 查询该客户的实际流水日期
            cursor.execute('''
                SELECT MIN(date) as min_date, MAX(date) as max_date, COUNT(*) as count
                FROM daily_records 
                WHERE customer_id = ? AND is_daily_summary = 0
            ''', (customer_id,))
            
            date_info = cursor.fetchone()
            
            if date_info and date_info['count'] > 0:
                # 使用实际流水日期
                actual_start_date = date_info['min_date']
                actual_end_date = date_info['max_date']
                record_count = date_info['count']
                
                print(f"[INFO]  从流水记录计算: {actual_start_date} 至 {actual_end_date} (共 {record_count} 条记录)")
            else:
                # 没有流水记录，使用当前日期
                current_date = datetime.now().strftime('%Y-%m-%d')
                actual_start_date = current_date
                actual_end_date = current_date
                print(f"[WARN]  没有流水记录，使用当前日期: {current_date}")
            
            # 更新月度目标
            cursor.execute('''
                UPDATE monthly_targets 
                SET start_date = ?, end_date = ?
                WHERE id = ?
            ''', (actual_start_date, actual_end_date, target_id))
            
            print(f"[INFO]  已更新: start_date={actual_start_date}, end_date={actual_end_date}")
        
        conn.commit()
        print(f"\n[SUCCESS] 成功修复 {len(empty_targets)} 条记录")
        
        # 显示修复后的所有月度目标
        print("\n[INFO] 修复后的月度目标列表:")
        cursor.execute('''
            SELECT mt.id, u.username, mt.year_month, mt.start_date, mt.end_date, mt.target_amount
            FROM monthly_targets mt
            JOIN users u ON mt.customer_id = u.id
            ORDER BY mt.id DESC
        ''')
        
        all_targets = cursor.fetchall()
        for t in all_targets:
            print(f"  ID={t['id']}: {t['username']} | {t['year_month']} | {t['start_date']} 至 {t['end_date']} | ¥{t['target_amount']:,.0f}")
    
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 修复失败: {e}")
        raise
    finally:
        close_db(conn)


if __name__ == '__main__':
    print("=" * 60)
    print("数据库日期修复脚本")
    print("=" * 60)
    print()
    
    fix_empty_dates()
    
    print()
    print("=" * 60)
    print("修复完成！")
    print("=" * 60)
