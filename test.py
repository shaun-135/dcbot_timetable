import matplotlib.pyplot as plt

# 創建一些數據和列標籤
data = [["Apple", 10], ["Banana", 20], ["Orange", 30]]
column_labels = ["Fruit", "Quantity"]

# 創建一個圖和軸
fig, ax = plt.subplots()

# 關閉坐標軸顯示
ax.axis("off")

# 插入表格
ax.table(cellText=data, colLabels=column_labels, loc="center",  cellLoc="center")

# 顯示圖表
plt.show()