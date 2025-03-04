import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

userid = 251333196195561472
conn = sqlite3.connect("user.db")
cursor = conn.cursor()
cursor.execute("SELECT subject, weekday, time_slot FROM schedule WHERE user_id = ?", (userid,))
timetable_data = cursor.fetchall()
conn.close()

# 定義星期和時間對應表
weekday_map = {1: "週一", 2: "週二", 3: "週三", 4: "週四", 5: "週五"}
time_slot_map = {
    1: "08:10\n|\n09:00",
    2: "09:10\n|\n10:00",
    3: "10:10\n|\n11:00",
    4: "11:10\n|\n12:00",
    5: "13:00\n|\n13:50",
    6: "14:00\n|\n14:50",
    7: "15:00\n|\n15:50",
    8: "16:00\n|\n16:50",
}

# 設置中文字體
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]  

# 將數據轉換為 DataFrame
df = pd.DataFrame(timetable_data, columns=["subject", "weekday", "time_slot"])

# 創建一個空的課表
timetable=[[""for _ in range (5)]for _ in range(8)]

# 將數據填入課表
for _, row in df.iterrows():
    day = int(row["weekday"]) - 1
    period = int(row["time_slot"]) - 1
    timetable[period][day] = row["subject"]

# 繪製課表表格
fig, ax = plt.subplots(figsize=(5, 8))
ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)

# 設定表格內容
table = ax.table(
    cellText=timetable,
    colLabels=[weekday_map[i] for i in range(1, 6)],
    rowLabels=[time_slot_map[i] for i in range(1, 9)],
    cellLoc="center",
    loc="center"
)

# 調整表格外觀
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1, 4.2)

# 調整圖表的邊距
plt.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)

# 調整圖表的大小
fig.set_size_inches(9.75, 15.6)


# 設定表格顏色與樣式
for (i, j), cell in table.get_celld().items():
    cell.set_edgecolor("gray")  # 改為灰色邊框
    cell.set_linewidth(0.6)  # 更細的邊框，讓視覺更輕盈
    cell.set_text_props(ha="center", va="center")  # 內容置中
    
    # 設定標題列（colLabels）與索引列（rowLabels）的樣式
    if i == 0 or j == -1:
        cell.set_facecolor("#34495e")  # 深灰藍色
        cell.set_text_props(color="white", fontweight="bold")
    
    # 交錯行底色（提升可讀性）
    elif i % 2 == 0:
        cell.set_facecolor("#ecf0f1")  # 淡灰色背景

plt.show()