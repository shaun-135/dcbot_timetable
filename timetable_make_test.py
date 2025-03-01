import matplotlib.pyplot as plt

# 示例數據
data = [
    ["Subject", "Hours", "Percentage"],
    ["Math", 5, 20],
    ["Science", 3, 15],
    ["English", 4, 30],
    ["History", 2, 10],
    ["Art", 1, 25]
]

# 創建圖形
fig, ax = plt.subplots(figsize=(7, 4))

# 隱藏坐標軸
ax.axis('off')

# 顯示表格
table = ax.table(cellText=data, colLabels=None, loc='center', cellLoc='center', colColours=['#f2f2f2']*3)

# 設定表格的樣式
table.auto_set_font_size(False)
table.set_fontsize(10)
table.auto_set_column_width([0, 1, 2])  # 自動調整列寬

# 顯示圖表
plt.show()