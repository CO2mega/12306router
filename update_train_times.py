import sqlite3
import os

def get_all_letters():
    """获取所有字母表名"""
    return ['C', 'D', 'G', 'K', 'P', 'S', 'T', 'Y', 'Z']

def update_train_times():
    """从train_basic.db导入运行时间数据到trains.db，不新增车次"""
    print('开始更新车次时间信息...')
    
    # 验证文件存在
    if not os.path.exists('train_basic.db'):
        print("错误: train_basic.db 文件不存在!")
        return
    if not os.path.exists('trains.db'):
        print("错误: trains.db 文件不存在!")
        return
    
    # 连接到两个数据库
    conn_basic = sqlite3.connect('train_basic.db')
    conn_trains = sqlite3.connect('trains.db')
    
    # 创建游标
    cursor_basic = conn_basic.cursor()
    cursor_trains = conn_trains.cursor()
    
    try:
        # 检查并添加run_time列（如果不存在）
        try:
            cursor_trains.execute('ALTER TABLE train_routes ADD COLUMN run_time TEXT')
            print("已添加run_time列")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                raise e
            print("run_time列已存在")
        
        # 获取现有车次信息
        print("\n获取trains.db中的所有车次信息...")
        cursor_trains.execute('''
            SELECT DISTINCT train_code, train_full_code 
            FROM train_routes 
            WHERE train_full_code IS NOT NULL
        ''')
        train_data = cursor_trains.fetchall()
        
        # 创建车次到完整代码的映射
        train_codes = {}
        train_full_codes = {}
        for row in train_data:
            train_code, train_full_code = row
            train_codes[train_code] = train_full_code
            train_full_codes[train_full_code] = train_code
        
        print(f"共找到 {len(train_codes)} 个带完整车次号的车次")
        
        # 获取没有完整代码的车次
        cursor_trains.execute('''
            SELECT DISTINCT train_code 
            FROM train_routes 
            WHERE train_full_code IS NULL
        ''')
        
        for row in cursor_trains.fetchall():
            train_code = row[0]
            if train_code not in train_codes:
                train_codes[train_code] = None
        
        print(f"总共找到 {len(train_codes)} 个不同车次")
        
        # 按字母类型处理
        letters = get_all_letters()
        updated_count = 0
        
        for letter in letters:
            print(f"\n处理{letter}字头车次...")
            
            # 验证表是否存在
            cursor_basic.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{letter}'")
            if not cursor_basic.fetchone():
                print(f"表 {letter} 不存在，跳过")
                continue
            
            try:
                # 获取表结构
                cursor_basic.execute(f"PRAGMA table_info({letter})")
                columns = [col[1] for col in cursor_basic.fetchall()]
                
                # 确定需要的列名
                if 'run_time' in columns and 'train_full_code' in columns:
                    query = f"SELECT train_full_code, run_time FROM {letter}"
                    cursor_basic.execute(query)
                    records = cursor_basic.fetchall()
                    
                    print(f"从{letter}表中找到 {len(records)} 条记录")
                    
                    # 批量准备更新数据
                    update_data = []
                    for train_full_code, run_time in records:
                        if run_time and ':' in run_time:  # 确保时间格式有效
                            # 尝试直接匹配完整车次号
                            if train_full_code in train_full_codes:
                                train_code = train_full_codes[train_full_code]
                                update_data.append((run_time, train_code))
                            else:
                                # 尝试匹配车次编号（提取数字部分）
                                digits = ''.join([c for c in train_full_code if c.isdigit()])
                                if digits in train_codes:
                                    update_data.append((run_time, digits))
                    
                    # 执行批量更新
                    if update_data:
                        cursor_trains.executemany(
                            "UPDATE train_routes SET run_time = ? WHERE train_code = ?", 
                            update_data
                        )
                        
                        updated_count += len(update_data)
                        print(f"更新了 {len(update_data)} 条{letter}字头车次记录")
                        conn_trains.commit()
                    else:
                        print(f"没有找到可匹配的{letter}字头车次")
                
                else:
                    print(f"表 {letter} 缺少必要的列(train_full_code 或 run_time)")
                    
            except sqlite3.Error as e:
                print(f"处理表 {letter} 时出错: {e}")
        
        # 验证结果
        cursor_trains.execute('''
            SELECT COUNT(*) as total,
                   COUNT(run_time) as with_time
            FROM train_routes
        ''')
        total, with_time = cursor_trains.fetchone()
        
        print("\n更新完成:")
        print(f"总记录数: {total}")
        print(f"已添加时间的记录数: {with_time}")
        print(f"更新成功率: {(with_time/total*100):.2f}%")
            
    except Exception as e:
        print(f"更新车次时间信息出错: {e}")
        conn_trains.rollback()
        
    finally:
        cursor_basic.close()
        cursor_trains.close()
        conn_basic.close()
        conn_trains.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    update_train_times()