import sqlite3

def get_all_letters():
    """获取所有字母表名"""
    return ['C', 'D', 'G', 'K', 'P', 'S', 'T', 'Y', 'Z']

def import_train_times():
    try:
        # 连接数据库
        conn_source = sqlite3.connect('train_basic.db')
        conn_target = sqlite3.connect('trains.db')
        
        cursor_source = conn_source.cursor()
        cursor_target = conn_target.cursor()
        
        print("正在添加时间列...")
        try:
            cursor_target.execute('ALTER TABLE train_routes ADD COLUMN run_time TEXT')
            print("已添加时间列")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise e
            print("时间列已存在")

        # 获取目标数据库中的所有车次及其完整车次号
        print("\n正在获取车次信息...")
        cursor_target.execute('SELECT DISTINCT train_code, train_full_code FROM train_routes WHERE train_full_code IS NOT NULL')
        train_codes = {row[1]: row[0] for row in cursor_target.fetchall()}
        print(f"共找到 {len(train_codes)} 个带完整车次号的车次")

        updated_count = 0
        letters = get_all_letters()
        
        for letter in letters:
            print(f"\n处理{letter}字头车次...")
            
            try:
                cursor_source.execute(f'''
                    SELECT 
                        start_station,
                        arrive_station,
                        run_time 
                    FROM {letter}
                ''')
                
                batch_data = cursor_source.fetchall()
                print(f"找到 {len(batch_data)} 条记录")
                
                # 批量更新以提高性能
                update_data = []
                for row in batch_data:
                    start_station = row[0]
                    arrive_station = row[1]
                    run_time = row[2]
                    
                    # 构造可能的完整车次号格式
                    possible_codes = [
                        f"{start_station}{arrive_station}",
                        f"{start_station}00{arrive_station}"
                    ]
                    
                    # 找到匹配的train_code
                    for full_code in possible_codes:
                        if full_code in train_codes:
                            update_data.append((run_time, train_codes[full_code], arrive_station))
                            break
                
                # 批量执行更新
                if update_data:
                    cursor_target.executemany('''
                        UPDATE train_routes 
                        SET run_time = ?
                        WHERE train_code = ?
                        AND EXISTS (
                            SELECT 1 
                            FROM stations s 
                            WHERE s.id = train_routes.station_id 
                            AND s.name = ?
                        )
                    ''', update_data)
                    
                    updated_count += len(update_data)
                    print(f"更新了 {len(update_data)} 条记录")
                    conn_target.commit()
                        
            except sqlite3.OperationalError as e:
                print(f"处理{letter}表时出错: {e}")
                continue

        # 最终提交
        conn_target.commit()
        
        # 验证更新
        cursor_target.execute('''
            SELECT COUNT(*) as total,
                   COUNT(run_time) as with_time
            FROM train_routes
        ''')
        total, with_time = cursor_target.fetchone()
        
        print("\n更新完成:")
        print(f"总记录数: {total}")
        print(f"已添加时间的记录数: {with_time}")
        print(f"更新成功率: {(with_time/total*100):.2f}%")
        
        # 显示示例数据
        print("\n数据示例:")
        cursor_target.execute('''
            SELECT r.train_code, r.train_full_code, s.name as station_name, r.run_time
            FROM train_routes r
            JOIN stations s ON r.station_id = s.id
            WHERE r.run_time IS NOT NULL
            LIMIT 5
        ''')
        
        print("\n车次代码  | 完整车次号      | 站名     | 运行时间")
        print("-" * 60)
        for row in cursor_target.fetchall():
            print(f"{row[0]:<8} | {row[1]:<14} | {row[2]:<8} | {row[3]}")

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        conn_target.rollback()
    finally:
        conn_source.close()
        conn_target.close()

if __name__ == '__main__':
    import_train_times()