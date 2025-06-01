import sqlite3

def remove_duplicates():
    try:
        conn = sqlite3.connect('trains.db')
        cursor = conn.cursor()

        print("开始查找重复记录...")

        # 找出完全重复的记录
        cursor.execute("""
            WITH duplicates AS (
                SELECT 
                    train_code,
                    station_id,
                    station_no,
                    train_full_code,
                    COUNT(*) as cnt,
                    MIN(id) as min_id
                FROM train_routes
                GROUP BY train_code, station_id, station_no, train_full_code
                HAVING COUNT(*) > 1
            )
            SELECT COUNT(*) as total_duplicates
            FROM duplicates
        """)
        
        duplicate_count = cursor.fetchone()[0]
        print(f"\n找到 {duplicate_count} 组完全重复的记录")

        if duplicate_count > 0:
            # 删除重复记录，保留最小ID的记录
            cursor.execute("""
                DELETE FROM train_routes
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM train_routes
                    GROUP BY train_code, station_id, station_no, train_full_code
                )
            """)
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            # 验证结果
            cursor.execute("SELECT COUNT(*) FROM train_routes")
            remaining_records = cursor.fetchone()[0]
            
            print(f"\n清理完成:")
            print(f"删除的重复记录数: {deleted_count}")
            print(f"剩余记录总数: {remaining_records}")
            
            # 显示一些示例数据
            print("\n剩余记录示例:")
            cursor.execute("""
                SELECT id, train_code, station_id, station_no, train_full_code
                FROM train_routes
                LIMIT 5
            """)
            
            print("\nID     | 车次代码  | 站点ID | 站序 | 完整车次代码")
            print("-" * 60)
            for row in cursor.fetchall():
                print(f"{row[0]:<6} | {row[1]:<8} | {row[2]:<6} | {row[3]:<4} | {row[4]}")
        else:
            print("数据库中没有找到完全重复的记录")

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    remove_duplicates()