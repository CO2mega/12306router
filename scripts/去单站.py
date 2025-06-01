import sqlite3

def clean_single_station_routes():
    try:
        conn = sqlite3.connect('trains.db')
        cursor = conn.cursor()

        print("开始清理单站点路线...")

        # 首先找出只有一个站点的列车
        cursor.execute("""
            WITH train_station_counts AS (
                SELECT train_code, COUNT(*) as station_count
                FROM train_routes
                GROUP BY train_code
            )
            SELECT train_code, station_count
            FROM train_station_counts
            WHERE station_count = 1
        """)
        
        single_station_trains = cursor.fetchall()
        
        if not single_station_trains:
            print("没有找到只有单个站点的列车")
            return
            
        print(f"\n找到 {len(single_station_trains)} 条只有单站点的列车")
        
        # 删除这些列车的记录
        cursor.execute("""
            DELETE FROM train_routes
            WHERE train_code IN (
                SELECT train_code
                FROM (
                    SELECT train_code, COUNT(*) as cnt
                    FROM train_routes
                    GROUP BY train_code
                )
                WHERE cnt = 1
            )
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        # 验证结果
        cursor.execute("SELECT COUNT(DISTINCT train_code) FROM train_routes")
        remaining_trains = cursor.fetchone()[0]
        
        print(f"\n清理完成:")
        print(f"已删除的单站点列车数: {deleted_count}")
        print(f"剩余列车数: {remaining_trains}")
        
        # 显示一些示例数据
        print("\n剩余列车示例:")
        cursor.execute("""
            SELECT train_code, COUNT(*) as station_count
            FROM train_routes
            GROUP BY train_code
            LIMIT 5
        """)
        
        print("车次代码  |  站点数")
        print("-" * 20)
        for row in cursor.fetchall():
            print(f"{row[0]:<10}|  {row[1]}")

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    clean_single_station_routes()