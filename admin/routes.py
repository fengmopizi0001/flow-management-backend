"""
管理员路由 - 流水管理系统
处理管理员仪表盘、Excel导入、目标管理、记录查看等功能
"""

from flask import render_template, request, redirect, url_for, session, jsonify, flash
import pandas as pd
from datetime import datetime, timedelta
from database import get_db, close_db
from utils import (
    require_admin,
    parse_date_from_form,
    parse_date_range_from_request,
    log_action
)
from werkzeug.security import generate_password_hash


@require_admin
def dashboard():
    """
    管理员仪表盘
    显示系统统计信息和客户列表
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取统计信息
        # 1. 客户总数（从users表获取，确保实时准确）
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "customer"')
        customer_count = cursor.fetchone()[0]

        # 2. 流水统计（从daily_records表获取）
        cursor.execute('''
            SELECT 
                   SUM(CASE WHEN status = 'done' THEN amount ELSE 0 END) as completed,
                   SUM(amount) as total
            FROM daily_records WHERE is_daily_summary = 0
        ''')
        flow_stats = cursor.fetchone()
        
        # 合并统计数据
        stats = {
            'customer_count': customer_count,
            'completed': flow_stats['completed'] if flow_stats else 0,
            'total': flow_stats['total'] if flow_stats else 0
        }
        
        # 获取所有客户
        cursor.execute('SELECT * FROM users WHERE role = "customer" ORDER BY created_at DESC')
        customers = cursor.fetchall()

        # 获取所有目标列表（带统计）
        cursor.execute('''
            SELECT mt.*, u.username,
                   (SELECT SUM(amount) FROM daily_records dr 
                    WHERE dr.customer_id = mt.customer_id 
                    AND dr.date >= mt.start_date 
                    AND dr.date <= mt.end_date 
                    AND dr.status = 'done'
                    AND dr.is_daily_summary = 0) as completed_amount
            FROM monthly_targets mt
            JOIN users u ON mt.customer_id = u.id
            ORDER BY u.username, mt.period_number
        ''')
        targets = cursor.fetchall()
        
        # 调试信息
        print(f"[DEBUG] 客户数量: {len(customers)}")
        for customer in customers:
            print(f"[DEBUG] 客户: ID={customer['id']}, 用户名={customer['username']}, 创建时间={customer['created_at']}")
        
        return render_template('admin/dashboard.html', 
                             stats=stats, 
                             customers=customers,
                             targets=targets)
    
    finally:
        close_db(conn)


@require_admin
def import_excel():
    """
    导入Excel文件
    解析Excel并批量导入流水数据
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取所有客户列表
        cursor.execute('SELECT * FROM users WHERE role = "customer"')
        customers = cursor.fetchall()
        
        if request.method == 'POST':
            # 验证文件
            if 'file' not in request.files:
                return render_template('admin/import_excel.html', 
                                     customers=customers,
                                     error='请选择文件')
            
            file = request.files['file']
            if file.filename == '':
                return render_template('admin/import_excel.html', 
                                     customers=customers,
                                     error='请选择文件')
            
            # 获取用户选择模式
            user_mode = request.form.get('user_mode', 'new')
            existing_customer_id = request.form.get('existing_customer_id')
            
            if file and file.filename.endswith(('.xlsx', '.xls')):
                try:
                    # 先读取前几行判断Excel格式
                    df_raw = pd.read_excel(file, sheet_name=0, header=None, nrows=3)
                    first_row = str(df_raw.iloc[0, 0]) if len(df_raw) > 0 else ''
                    
                    # 判断Excel格式
                    if '至' in first_row and len(first_row.split()) >= 2:
                        # 格式B：有标题行（如"2026-01-27至2026-02-27 李先生流水表"）
                        df = pd.read_excel(file, sheet_name=0, header=1)  # 从第2行作为表头
                        first_cell = first_row  # 使用第0行提取信息
                        print(f"[DEBUG] 检测到格式B（带标题行），从第2行开始读取数据")
                    else:
                        # 格式A：无标题行（如"50万流水1.xlsx"），第一行就是表头
                        df = pd.read_excel(file, sheet_name=0)  # 从第1行作为表头
                        first_cell = 'Unknown'  # 无法提取标题信息
                        print(f"[DEBUG] 检测到格式A（无标题行），从第1行开始读取数据")
                    
                    # 解析日期范围和客户名（仅格式B可以提取）
                    date_range = ''
                    excel_customer_name = 'Unknown'
                    
                    if first_cell != 'Unknown':
                        parts = first_cell.split()
                        date_range = parts[0] if len(parts) > 0 else ''
                        excel_customer_name = ' '.join(parts[1:]) if len(parts) > 1 else 'Unknown'
                        # 清理客户名
                        excel_customer_name = excel_customer_name.replace('流水表', '').strip()
                    
                    # 格式A：使用统一提取方式从数据中获取日期范围和目标金额
                    if date_range == '' and len(df) > 0:
                        # 起始日期：第一行第一列
                        first_date = str(df.iloc[0, 0])
                        
                        # 结束日期：倒数第二行第一列（排除总计行）
                        if len(df) >= 2:
                            last_date = str(df.iloc[-2, 0])
                        else:
                            last_date = first_date
                        
                        # 目标金额：最后一行最后一列
                        if len(df) >= 1:
                            last_row = df.iloc[-1]
                            last_column_value = last_row.iloc[-1]
                            try:
                                total_amount = float(last_column_value) if pd.notna(last_column_value) else 0
                                print(f"[DEBUG] 格式A：从最后一行最后一列提取目标金额: {total_amount}")
                            except (ValueError, TypeError):
                                total_amount = 0
                        
                        date_range = f'{first_date}至{last_date}'
                        print(f"[DEBUG] 格式A：从数据推断日期范围: {date_range}")
                    
                    # 解析日期
                    if '至' in date_range:
                        start_date, end_date = date_range.split('至')
                    else:
                        start_date = end_date = date_range
                    
                    # 验证日期不为空
                    if not start_date or not end_date:
                        start_date = end_date = datetime.now().strftime('%Y-%m-%d')
                        print(f"[DEBUG] Excel日期为空，使用当前日期: {start_date}")
                    
                    # 生成年月
                    year_month = start_date[:7] if start_date else datetime.now().strftime('%Y-%m')
                    
                    # 格式B：从最后一行最后一列获取目标金额（如果格式A还没获取）
                    if total_amount == 0 and len(df) > 0:
                        last_row = df.iloc[-1]
                        last_column_value = last_row.iloc[-1]
                        try:
                            total_amount = float(last_column_value) if pd.notna(last_column_value) else 0
                            print(f"[DEBUG] 格式B：从最后一行最后一列提取目标金额: {total_amount}")
                        except (ValueError, TypeError):
                            total_amount = 0
                    
                    # 处理客户账户
                    if user_mode == 'new':
                        custom_username = request.form.get('custom_username', '').strip()
                        customer_name = custom_username if custom_username else excel_customer_name
                        
                        cursor.execute('SELECT id FROM users WHERE username = ?', (customer_name,))
                        customer = cursor.fetchone()
                        
                        if not customer:
                            password_hash = generate_password_hash('123456')
                            cursor.execute('''
                                INSERT INTO users (username, password_hash, role)
                                VALUES (?, ?, ?)
                            ''', (customer_name, password_hash, 'customer'))
                            customer_id = cursor.lastrowid
                            is_new_user = True
                        else:
                            customer_id = customer['id']
                            is_new_user = False
                    else:
                        if not existing_customer_id:
                            return render_template('admin/import_excel.html', 
                                                 customers=customers,
                                                 error='请选择已有用户')
                        
                        customer_id = int(existing_customer_id)
                        cursor.execute('SELECT username FROM users WHERE id = ?', (customer_id,))
                        user = cursor.fetchone()
                        customer_name = user['username']
                        is_new_user = False
                    
                    # 1. 预扫描日期范围 (用于验证和冲突检查)
                    import_dates = []
                    for idx, row in df.iterrows():
                        date_str = str(row.iloc[0]) if len(row) > 0 else ''
                        if date_str and date_str != '总计' and date_str != 'nan':
                            import_dates.append(date_str)
                    
                    if not import_dates:
                        actual_start_date = start_date or datetime.now().strftime('%Y-%m-%d')
                        actual_end_date = end_date or datetime.now().strftime('%Y-%m-%d')
                    else:
                        import_dates.sort()
                        actual_start_date = import_dates[0]
                        actual_end_date = import_dates[-1]

                    # 2. 获取期数
                    period_number = request.form.get('period_number', 1)
                    
                    # 3. 验证日期冲突 (检查与其他期数是否重叠)
                    cursor.execute('''
                        SELECT period_number, start_date, end_date 
                        FROM monthly_targets 
                        WHERE customer_id = ? AND period_number != ?
                    ''', (customer_id, period_number))
                    existing_targets = cursor.fetchall()

                    for target in existing_targets:
                        # 检查重叠: max(start1, start2) <= min(end1, end2)
                        if max(actual_start_date, target['start_date']) <= min(actual_end_date, target['end_date']):
                             raise ValueError(f"日期范围冲突：导入的数据 ({actual_start_date} 至 {actual_end_date}) 与第 {target['period_number']} 期 ({target['start_date']} 至 {target['end_date']}) 重叠")

                    # 4. 清理旧数据 (仅清理当前期数的数据)
                    # 获取当前期数旧的日期范围，以便删除对应的流水记录
                    cursor.execute('SELECT start_date, end_date FROM monthly_targets WHERE customer_id = ? AND period_number = ?', (customer_id, period_number))
                    current_target = cursor.fetchone()
                    
                    if current_target:
                        # 删除旧范围内的流水记录
                        cursor.execute('DELETE FROM daily_records WHERE customer_id = ? AND date >= ? AND date <= ?', (customer_id, current_target['start_date'], current_target['end_date']))
                        # 删除旧目标
                        cursor.execute('DELETE FROM monthly_targets WHERE customer_id = ? AND period_number = ?', (customer_id, period_number))
                    
                    # 5. 插入每日流水
                    record_count = 0
                    for idx, row in df.iterrows():
                        date_str = str(row.iloc[0]) if len(row) > 0 else ''
                        
                        if date_str and date_str != '总计' and date_str != 'nan':
                            # 解析交易1-20
                            daily_records = []
                            for i in range(1, 21):
                                try:
                                    amount = float(row.iloc[i]) if len(row) > i and pd.notna(row.iloc[i]) else 0
                                    if amount > 0:
                                        cursor.execute('''
                                            INSERT INTO daily_records 
                                            (customer_id, date, amount, status)
                                            VALUES (?, ?, ?, ?)
                                        ''', (customer_id, date_str, amount, 'pending'))
                                        daily_records.append(amount)
                                        record_count += 1
                                except (ValueError, IndexError):
                                    pass
                            
                            # 创建当日汇总记录
                            if daily_records:
                                daily_total = sum(daily_records)
                                cursor.execute('''
                                    INSERT INTO daily_records 
                                    (customer_id, date, amount, daily_total, status, is_daily_summary)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', (customer_id, date_str, daily_total, daily_total, 'pending', 1))

                    # 6. 插入月度目标
                    print(f"[DEBUG] 插入月度目标: start_date={actual_start_date}, end_date={actual_end_date}, amount={total_amount}, period={period_number}")
                    cursor.execute('''
                        INSERT INTO monthly_targets 
                        (customer_id, year_month, start_date, end_date, target_amount, period_number)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (customer_id, year_month, actual_start_date, actual_end_date, total_amount, period_number))
                    
                    conn.commit()
                    
                    # 记录日志
                    log_action('EXCEL_IMPORT', session['user_id'], 
                              f'导入Excel: 客户ID {customer_id}, 期数 {period_number}, 日期 {actual_start_date} 至 {actual_end_date}, 总额 {total_amount}')
                    
                    return render_template('admin/import_excel.html', 
                                         success=True,
                                         customer_name=customer_name,
                                         start_date=start_date,
                                         end_date=end_date,
                                         total_amount=total_amount,
                                         record_count=record_count,
                                         is_new_user=is_new_user)
                
                except Exception as e:
                    conn.rollback()
                    log_action('EXCEL_IMPORT_ERROR', session['user_id'], 
                              f'导入Excel失败: {str(e)}')
                    return render_template('admin/import_excel.html', 
                                         customers=customers,
                                         error=f'导入失败: {str(e)}')
        
        return render_template('admin/import_excel.html', customers=customers)
    
    finally:
        close_db(conn)


@require_admin
def add_target():
    """
    手动添加月度目标
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM users WHERE role = "customer"')
        customers = cursor.fetchall()
        
        if request.method == 'POST':
            try:
                # 优先通过用户名查找ID（更稳健）
                customer_name = request.form.get('customer_name')
                cursor.execute('SELECT id FROM users WHERE username = ?', (customer_name,))
                user_row = cursor.fetchone()
                if not user_row:
                    raise ValueError(f'未找到用户: {customer_name}')
                customer_id = user_row['id']

                period_number = request.form.get('period_number', 1)
                
                # 直接获取日期字符串 (YYYY-MM-DD)
                start_date = request.form.get('start_date')
                end_date = request.form.get('end_date')
                
                if not start_date or not end_date:
                    raise ValueError('必须选择起始和结束日期')

                # 自动生成 year_month
                year_month = start_date[:7]
                
                target_amount = float(request.form.get('target_amount'))

                # 校验：检查该用户是否已存在相同的期数
                cursor.execute('''
                    SELECT id FROM monthly_targets 
                    WHERE customer_id = ? AND period_number = ?
                ''', (customer_id, period_number))
                if cursor.fetchone():
                    raise ValueError(f'该用户的第 {period_number} 期目标已存在')
                
                # 补齐历史流水选项
                fill_history = request.form.get('fill_history') == '1'
                fill_operator = request.form.get('fill_operator', '补录').strip()
                
                # 插入月度目标
                cursor.execute('''
                    INSERT INTO monthly_targets 
                    (customer_id, year_month, start_date, end_date, target_amount, period_number)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (customer_id, year_month, start_date, end_date, target_amount, period_number))
                
                # 如果需要补齐历史流水
                if fill_history:
                    today = datetime.now().strftime('%Y-%m-%d')
                    start = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end = datetime.strptime(today, '%Y-%m-%d').date()
                    
                    delta = end - start
                    days_to_fill = delta.days + 1
                    
                    if days_to_fill > 0:
                        daily_amount = target_amount / days_to_fill
                        
                        for i in range(days_to_fill):
                            fill_date = (start + timedelta(days=i)).strftime('%Y-%m-%d')
                            
                            cursor.execute('''
                                INSERT INTO daily_records 
                                (customer_id, date, amount, daily_total, status, operator, is_daily_summary)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (customer_id, fill_date, daily_amount, daily_amount, 'done', fill_operator, 1))
                
                conn.commit()
                
                log_action('ADD_TARGET', session['user_id'], 
                          f'客户ID: {customer_id}, 年月: {year_month}, 期数: {period_number}, 金额: {target_amount}')
                
                return redirect(url_for('admin.dashboard'))
            
            except Exception as e:
                conn.rollback()
                return render_template('admin/add_target.html', 
                                     customers=customers, 
                                     error=str(e))
        
        return render_template('admin/add_target.html', customers=customers)
    
    finally:
        close_db(conn)


@require_admin
def edit_target(target_id):
    """
    编辑月度目标
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 查找目标
        cursor.execute('''
            SELECT mt.*, u.username 
            FROM monthly_targets mt
            JOIN users u ON mt.customer_id = u.id
            WHERE mt.id = ?
        ''', (target_id,))
        target = cursor.fetchone()
        
        if not target:
            return redirect(url_for('admin.dashboard'))
            
        if request.method == 'POST':
            try:
                start_date = request.form['start_date']
                end_date = request.form['end_date']
                target_amount = float(request.form['target_amount'])
                
                # 自动生成 year_month
                year_month = start_date[:7]
                
                # 验证日期冲突
                cursor.execute('''
                    SELECT period_number, start_date, end_date 
                    FROM monthly_targets 
                    WHERE customer_id = ? AND id != ?
                ''', (target['customer_id'], target_id))
                other_targets = cursor.fetchall()

                for other in other_targets:
                     if max(start_date, other['start_date']) <= min(end_date, other['end_date']):
                         raise ValueError(f"日期范围冲突：与第 {other['period_number']} 期 ({other['start_date']} 至 {other['end_date']}) 重叠")

                cursor.execute('''
                    UPDATE monthly_targets
                    SET start_date = ?, end_date = ?, target_amount = ?, year_month = ?
                    WHERE id = ?
                ''', (start_date, end_date, target_amount, year_month, target_id))
                
                conn.commit()
                
                log_action('EDIT_TARGET', session['user_id'], 
                          f'修改目标ID: {target_id}, 金额: {target_amount}')
                
                return redirect(url_for('admin.dashboard'))
                
            except Exception as e:
                conn.rollback()
                return render_template('admin/edit_target.html', target=target, error=str(e))
            
        return render_template('admin/edit_target.html', target=target)
        
    finally:
        close_db(conn)


@require_admin
def delete_target(target_id):
    """
    删除月度目标
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查是否存在
        cursor.execute('SELECT id FROM monthly_targets WHERE id = ?', (target_id,))
        if not cursor.fetchone():
            flash('未找到该目标', 'error')
            return redirect(url_for('admin.dashboard'))
            
        cursor.execute('DELETE FROM monthly_targets WHERE id = ?', (target_id,))
        conn.commit()
        
        log_action('DELETE_TARGET', session['user_id'], f'删除目标ID: {target_id}')
        flash('目标已删除', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'删除失败: {str(e)}', 'error')
        
    finally:
        close_db(conn)
        
    return redirect(url_for('admin.dashboard'))


@require_admin
def add_record():
    """
    添加流水记录
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM users WHERE role = "customer"')
        customers = cursor.fetchall()
        
        if request.method == 'POST':
            try:
                customer_id = request.form.get('customer_id')
                
                # 解析日期
                date = parse_date_from_form(
                    request.form.get('record_year'),
                    request.form.get('record_month'),
                    request.form.get('record_day')
                )
                
                amount_str = request.form.get('amount')
                if not amount_str:
                    return render_template('admin/add_record.html', 
                                         customers=customers, 
                                         error='请输入流水金额')
                
                amount = float(amount_str)
                status = request.form.get('status', 'done')
                
                # 处理操作员关联
                operator_id = request.form.get('operator_id')
                operator_name = ''
                
                if operator_id:
                    try:
                        operator_id = int(operator_id)
                        if operator_id == 999999:
                            operator_name = '管理员'
                        else:
                            # 获取操作员名称用于冗余存储
                            cursor.execute('SELECT name FROM operators WHERE id = ?', (operator_id,))
                            op_row = cursor.fetchone()
                            if op_row:
                                operator_name = op_row['name']
                            else:
                                operator_id = None
                    except (ValueError, TypeError):
                        operator_id = None
                
                # 插入流水记录
                cursor.execute('''
                    INSERT INTO daily_records (customer_id, date, amount, status, operator, operator_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (customer_id, date, amount, status, operator_name, operator_id))
                
                # 更新或创建当日汇总
                cursor.execute('''
                    SELECT SUM(amount) as total FROM daily_records 
                    WHERE customer_id = ? AND date = ? AND is_daily_summary = 0
                ''', (customer_id, date))
                result = cursor.fetchone()
                
                if result and result['total']:
                    daily_total = result['total']
                    cursor.execute('''
                        SELECT id FROM daily_records 
                        WHERE customer_id = ? AND date = ? AND is_daily_summary = 1
                    ''', (customer_id, date))
                    summary = cursor.fetchone()
                    
                    if summary:
                        cursor.execute('''
                            UPDATE daily_records 
                            SET amount = ?, daily_total = ?
                            WHERE id = ?
                        ''', (daily_total, daily_total, summary['id']))
                    else:
                        cursor.execute('''
                            INSERT INTO daily_records 
                            (customer_id, date, amount, daily_total, status, is_daily_summary)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (customer_id, date, daily_total, daily_total, 'pending', 1))
                
                conn.commit()
                
                log_action('ADD_RECORD', session['user_id'], 
                          f'客户ID: {customer_id}, 日期: {date}, 金额: {amount}')
                
                return redirect(url_for('admin.view_records'))
            
            except Exception as e:
                conn.rollback()
                return render_template('admin/add_record.html', 
                                     customers=customers, 
                                     error=str(e))
        
        return render_template('admin/add_record.html', customers=customers)
    
    finally:
        close_db(conn)


@require_admin
def view_records():
    """
    查看所有流水记录
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取参数
        customer_id = request.args.get('customer_id', type=int)
        start_date, end_date = parse_date_range_from_request(request)
        
        # 获取客户列表
        cursor.execute('SELECT * FROM users WHERE role = "customer"')
        customers = cursor.fetchall()
        
        # 构建查询
        query = '''
            SELECT dr.*, u.username as customer_name, 
                   CASE 
                       WHEN dr.operator_id = 999 THEN '自己'
                       WHEN dr.operator_id = 999999 THEN '管理员'
                       ELSE o.name 
                   END as operator_final_name
            FROM daily_records dr
            JOIN users u ON dr.customer_id = u.id
            LEFT JOIN operators o ON dr.operator_id = o.id
            WHERE dr.is_daily_summary = 0
        '''
        params = []
        
        if customer_id:
            query += ' AND dr.customer_id = ?'
            params.append(customer_id)
        
        if start_date:
            query += ' AND dr.date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND dr.date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY dr.date ASC, dr.id DESC'
        
        cursor.execute(query, params)
        records = cursor.fetchall()
        
        # 获取选中客户的目标列表（用于期数筛选）
        customer_targets = []
        if customer_id:
            cursor.execute('SELECT * FROM monthly_targets WHERE customer_id = ? ORDER BY period_number', (customer_id,))
            customer_targets = cursor.fetchall()
        
        return render_template('admin/view_records.html', 
                             records=records, 
                             customers=customers,
                             selected_customer=customer_id,
                             start_date=start_date,
                             end_date=end_date,
                             customer_targets=customer_targets)
    
    finally:
        close_db(conn)


@require_admin
def reconciliation():
    """
    管理员对账报表
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        start_date, end_date = parse_date_range_from_request(request)
        customer_id = request.args.get('customer_id', type=int)
        
        # 获取所有客户列表用于下拉筛选
        cursor.execute('SELECT id, username FROM users WHERE role = "customer"')
        customers = cursor.fetchall()
        
        # 按客户统计查询
        customer_query = '''
            SELECT u.username, 
                   COUNT(CASE WHEN dr.status = 'done' THEN 1 END) as completed_count,
                   SUM(CASE WHEN dr.status = 'done' THEN dr.amount ELSE 0 END) as completed,
                   COUNT(*) as total_count,
                   SUM(dr.amount) as total
            FROM users u
            LEFT JOIN daily_records dr ON u.id = dr.customer_id AND dr.is_daily_summary = 0
            WHERE u.role = 'customer'
        '''
        
        params = []
        
        if customer_id:
            customer_query += ' AND u.id = ?'
            params.append(customer_id)
        
        if start_date:
            customer_query += ' AND (dr.date >= ? OR dr.date IS NULL)'
            params.append(start_date)
        
        if end_date:
            customer_query += ' AND (dr.date <= ? OR dr.date IS NULL)'
            params.append(end_date)
        
        customer_query += ' GROUP BY u.id, u.username ORDER BY completed DESC'
        
        cursor.execute(customer_query, params)
        customer_stats = cursor.fetchall()
        
        return render_template('admin/reconciliation.html',
                             customer_stats=customer_stats,
                             customers=customers,
                             selected_customer=customer_id,
                             start_date=start_date,
                             end_date=end_date)
    
    finally:
        close_db(conn)


@require_admin
def customer_query_select():
    """选择要查询的客户"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, username FROM users WHERE role = "customer" ORDER BY username')
        customers = cursor.fetchall()
        return render_template('admin/customer_query_select.html', customers=customers)
    finally:
        close_db(conn)


@require_admin
def customer_query_view(customer_id):
    """显示指定客户的查询界面"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 获取客户信息
        cursor.execute('SELECT * FROM users WHERE id = ? AND role = "customer"', (customer_id,))
        customer = cursor.fetchone()
        
        if not customer:
            return "客户不存在", 404
            
        # 获取该客户的操作员
        cursor.execute('''
            SELECT DISTINCT o.id, o.name
            FROM operators o
            WHERE (o.customer_id = ? OR o.customer_id IS NULL) AND o.is_active = 1
            ORDER BY o.name
        ''', (customer_id,))
        operators = cursor.fetchall()
        
        # 获取支付渠道
        cursor.execute('''
            SELECT DISTINCT pc.id, pc.name
            FROM payment_channels pc
            JOIN operators o ON pc.operator_id = o.id
            WHERE (o.customer_id = ? OR o.customer_id IS NULL) AND pc.is_active = 1
            ORDER BY pc.name
        ''', (customer_id,))
        channels = cursor.fetchall()
        
        return render_template('admin/customer_query_view.html', 
                             customer=customer,
                             operators=operators, 
                             channels=channels)
    finally:
        close_db(conn)


@require_admin
def customer_query_search(customer_id):
    """执行客户流水查询（管理员版）"""
    data = request.get_json()
    print(f"DEBUG: customer_query_search called for customer_id={customer_id}")
    print(f"DEBUG: data={data}")
    
    start_date = data.get('start_date', '')
    end_date = data.get('end_date', '')
    operator_id = data.get('operator_id', '')
    channel_id = data.get('channel_id', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 构建查询
        query = '''
            SELECT dr.date, dr.amount, dr.status,
                   CASE 
                       WHEN dr.operator_id = 999 THEN '自己'
                       WHEN dr.operator_id = 999999 THEN '管理员'
                       ELSE o.name 
                   END as operator_name,
                   CASE 
                       WHEN dr.channel_id = 1 THEN '微信支付'
                       WHEN dr.channel_id = 2 THEN '支付宝'
                       WHEN dr.channel_id = 3 THEN '其他渠道'
                       ELSE pc.name 
                   END as channel_name
            FROM daily_records dr
            LEFT JOIN operators o ON dr.operator_id = o.id
            LEFT JOIN payment_channels pc ON dr.channel_id = pc.id
            WHERE dr.customer_id = ? AND dr.is_daily_summary = 0 AND dr.status = 'done'
        '''
        params = [customer_id]
        
        if start_date:
            query += ' AND dr.date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND dr.date <= ?'
            params.append(end_date)
            
        if operator_id:
            if operator_id == 'self':
                query += ' AND dr.operator_id = 999'
            else:
                query += ' AND dr.operator_id = ?'
                params.append(operator_id)
                
        if channel_id:
            if channel_id == '0': # 不选择
                query += ' AND (dr.channel_id = 0 OR dr.channel_id IS NULL)'
            else:
                query += ' AND dr.channel_id = ?'
                params.append(channel_id)
                
        query += ' ORDER BY dr.date DESC'
        
        cursor.execute(query, params)
        records = cursor.fetchall()
        
        # 统计
        total_count = len(records)
        total_amount = sum(r['amount'] for r in records)
        
        # 转换为字典列表
        result_records = []
        for r in records:
            result_records.append({
                'date': r['date'],
                'amount': r['amount'],
                'status': r['status'],
                'operator_name': r['operator_name'],
                'channel_name': r['channel_name']
            })
            
        return jsonify({
            'success': True,
            'records': result_records,
            'stats': {
                'total_count': total_count,
                'total_amount': total_amount
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        close_db(conn)
