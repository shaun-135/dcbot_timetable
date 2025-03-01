import sqlite3

def initialize_database():
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()

    # 建立 schedule 資料表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        user_id INTEGER,
        subject TEXT,
        weekday TEXT,
        start_time TEXT,
        end_time TEXT,
        PRIMARY KEY (user_id, subject, weekday, start_time, end_time)
    )
    """)

    # 建立 exams 資料表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exams (
        user_id INTEGER,
        subject TEXT,
        date TEXT,
        PRIMARY KEY (user_id, subject, date)
    )
    """)

    conn.commit()
    conn.close()
    print("資料庫初始化完成")

if __name__ == "__main__":
    initialize_database()