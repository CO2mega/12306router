#!/usr/bin/env python3

import sqlite3
import os
import sys

def create_city_trains_table(conn):
    """创建城市车次表"""
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS city_trains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        train_code TEXT NOT NULL,
        train_full_code TEXT,
        is_origin INTEGER DEFAULT 0,
        is_terminal INTEGER DEFAULT 0,
        UNIQUE(city, train_code)
    )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_city_trains_city ON city_trains(city)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_city_trains_train ON city_trains(train_code)')
    conn.commit()

def collect_train_data():
    """从trains.db收集数据并存储到stations.db"""
    try:
        # 确保数据库文件存在
        if not os.path.exists('trains.db'):
            print("错误: trains.db 文件不存在")
            return False
        
        # 连接trains.db数据库
        trains_conn = sqlite3.connect('trains.db')
        trains_cursor = trains_conn.cursor()
        
        # 连接stations.db数据库
        stations_conn = sqlite3.connect('stations.db')
        
        # 创建city_trains表
        create_city_trains_table(stations_conn)
        stations_cursor = stations_conn.cursor()
        
        print("正在清空city_trains表...")
        stations_cursor.execute("DELETE FROM city_trains")
        stations_conn.commit()
        
        # 首先查询表结构，看看有哪些列
        try:
            trains_cursor.execute("PRAGMA table_info(train_routes)")
            columns = [col[1] for col in trains_cursor.fetchall()]
            print(f"train_routes表的列: {columns}")
        except Exception as e:
            print(f"查询表结构失败: {e}")
        
        # 查询所有车次路线，使用正确的列名
        print("查询所有车次路线数据...")
        trains_cursor.execute('''
        SELECT train_code, train_full_code, city, station_no, 
               (SELECT MAX(station_no) FROM train_routes tr2 WHERE tr2.train_code = tr1.train_code) as max_station_no
        FROM train_routes tr1
        ORDER BY train_code, station_no
        ''')
        
        # 处理数据并插入
        print("开始处理数据并插入stations.db...")
        
        processed = set()  # 用于跟踪已处理的城市-车次组合
        batch_data = []
        batch_size = 1000
        count = 0
        
        for row in trains_cursor:
            train_code = row[0]
            train_full_code = row[1]
            city = row[2]
            station_no = int(row[3])
            max_station_no = int(row[4])
            
            # 跳过空的城市名
            if not city:
                continue
                
            # 跳过重复的城市-车次组合
            key = f"{city}-{train_code}"
            if key in processed:
                continue
            
            processed.add(key)
            
            # 判断是否为始发站或终点站
            is_origin = 1 if station_no == 1 else 0
            is_terminal = 1 if station_no == max_station_no else 0
            
            batch_data.append((city, train_code, train_full_code, is_origin, is_terminal))
            
            if len(batch_data) >= batch_size:
                stations_cursor.executemany(
                    "INSERT OR IGNORE INTO city_trains (city, train_code, train_full_code, is_origin, is_terminal) VALUES (?, ?, ?, ?, ?)",
                    batch_data
                )
                stations_conn.commit()
                count += len(batch_data)
                print(f"已处理 {count} 条记录...")
                batch_data = []
        
        # 插入剩余数据
        if batch_data:
            stations_cursor.executemany(
                "INSERT OR IGNORE INTO city_trains (city, train_code, train_full_code, is_origin, is_terminal) VALUES (?, ?, ?, ?, ?)",
                batch_data
            )
            stations_conn.commit()
            count += len(batch_data)
        
        print(f"数据收集完成! 共处理 {count} 条记录")
        
        # 查询验证
        stations_cursor.execute("SELECT COUNT(*) FROM city_trains")
        total = stations_cursor.fetchone()[0]
        print(f"city_trains表中共有 {total} 条记录")
        
        # 查询每个城市的车次数量
        stations_cursor.execute("SELECT city, COUNT(*) as count FROM city_trains GROUP BY city ORDER BY count DESC LIMIT 10")
        print("\n前10个城市的车次数量:")
        for city_data in stations_cursor.fetchall():
            print(f"{city_data[0]}: {city_data[1]}个车次")
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        return False
        
    finally:
        if 'trains_conn' in locals():
            trains_conn.close()
        if 'stations_conn' in locals():
            stations_conn.close()

if __name__ == "__main__":
    print("开始从trains.db收集车次数据到stations.db...")
    success = collect_train_data()
    sys.exit(0 if success else 1)