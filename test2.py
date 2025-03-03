import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


conn = sqlite3.connect("user.db")
userid = 251333196195561472
cursor = conn.cursor()
cursor.execute("SELECT subject, weekday, time_slot FROM schedule WHERE user_id = ?", (userid,))
timetable = cursor.fetchall()
conn.close()

# 設置中文字體
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]  

# 將數據轉換為 DataFrame


# 生成課表圖表

fig, ax = plt.subplots()
column_labels = ["", "一", "二", "三", "四", "五"]
ax.axis("off")
ax.table(cellText=df.values, colLabels=column_labels, loc="center", cellLoc="center")

plt.show()

