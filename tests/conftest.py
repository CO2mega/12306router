# tests/conftest.py
import os
import sys
import pytest

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def memory_db():
    """提供内存数据库连接"""
    import sqlite3
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # 创建测试表
    cursor.execute("""
    CREATE TABLE tickets (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        train_code TEXT NOT NULL,
        travel_date TEXT NOT NULL,
        seat_number INTEGER NOT NULL,
        status TEXT DEFAULT 'booked'
    )
    """)
    
    # 添加一些测试数据
    cursor.executemany("""
    INSERT INTO tickets (user_id, train_code, travel_date, seat_number, status)
    VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 'G101', '2025-06-04', 10, 'booked'),
        (1, 'G102', '2025-06-05', 5, 'booked'),
        (2, 'G101', '2025-06-04', 11, 'booked')
    ])
    
    conn.commit()
    yield conn
    conn.close()