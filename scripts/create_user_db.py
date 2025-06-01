import sqlite3

def create_user_db():
    try:
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建车票订单表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            train_code TEXT NOT NULL,
            train_full_code TEXT,
            from_station TEXT NOT NULL,
            to_station TEXT NOT NULL,
            travel_date DATE NOT NULL,
            booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'booked',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 创建每日售票统计表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_ticket_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_code TEXT NOT NULL,
            travel_date DATE NOT NULL,
            sold_count INTEGER DEFAULT 0,
            UNIQUE(train_code, travel_date)
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_tickets ON tickets(user_id, travel_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_train_date ON tickets(train_code, travel_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_stats ON daily_ticket_stats(train_code, travel_date)')
        
        conn.commit()
        print("用户数据库创建成功")
        
    except sqlite3.Error as e:
        print(f"创建数据库错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    create_user_db()