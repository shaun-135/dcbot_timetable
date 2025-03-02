import sqlite3

# 連接到資料庫
conn = sqlite3.connect("user.db")
cursor = conn.cursor()

# 查詢星期數字
cursor.execute("SELECT subject, weekday FROM exams")
exams = cursor.fetchall()

# 星期名稱對應表
week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# 轉換為對應的星期名稱
for subject, week_day in exams:
    day_name = week_days[week_day - 1]  # 週日是7，對應列表索引6
    print(f"{subject}: {day_name}")
    
conn.close()