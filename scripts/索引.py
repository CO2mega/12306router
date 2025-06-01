import sqlite3

def create_indexes():
    try:
        conn = sqlite3.connect('trains.db')
        cursor = conn.cursor()
        
        # 先删除现有索引
        print("正在删除现有索引...")
        cursor.execute("DROP INDEX IF EXISTS idx_train_station_no")
        cursor.execute("DROP INDEX IF EXISTS idx_station_order")
        
        print("正在创建新索引...")
        
        # 1. 为车次代码创建索引 - 支持快速查找特定车次
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_train_code 
        ON train_routes(train_code)
        ''')
        
        # 2. 为站序和车次创建复合索引 - 优化站序查询
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_station_train 
        ON train_routes(station_no, train_code)
        ''')
        
        # 3. 站点ID索引 - 优化站点查找
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_station_id
        ON train_routes(station_id)
        ''')
        
        # 4. 完整车次代码索引 - 支持全车次号查询
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_train_full_code
        ON train_routes(train_full_code)
        ''')
        
        # 5. 综合索引 - 优化多条件查询
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_route_search
        ON train_routes(train_code, station_id, station_no)
        ''')

        conn.commit()
        
        # 验证索引创建
        cursor.execute("""
            SELECT name, tbl_name 
            FROM sqlite_master 
            WHERE type='index' AND tbl_name='train_routes'
        """)
        
        indexes = cursor.fetchall()
        print("\n已创建的索引:")
        for idx in indexes:
            print(f"- {idx[0]}")
        
        print("\n索引创建完成")
        
    except sqlite3.Error as e:
        print(f"创建索引时发生错误: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    create_indexes()