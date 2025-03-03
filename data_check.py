#本程式用來測試資料庫
import sqlite3
import pandas as pd
import datetime


# ###檢查用戶考試資料庫
# conn = sqlite3.connect("user.db")   # 連接資料庫   
# cursor = conn.cursor()   # 創建一個 cursor 物件
# cursor.execute("SELECT * FROM exams")
# rows = cursor.fetchall()  # 獲取所有結果
# for row in rows:
#     print(row)
# print("以上為用戶考試資料\n")

# conn.commit()   # 提交  
# conn.close()     # 關閉 


# ###檢查用戶課表資料庫
# conn = sqlite3.connect("user.db")   # 連接資料庫   
# cursor = conn.cursor()   # 創建一個 cursor 物件
# cursor.execute("SELECT * FROM schedule")
# rows = cursor.fetchall()  # 獲取所有結果
# for row in rows:
#     print(row)
# print("以上為用戶課表資料\n")

# conn.commit()   # 提交  
# conn.close()     # 關閉 

df=pd.read_csv("schedule.csv")
print(df)
# ###檢查用戶匯入資料

conn = sqlite3.connect("user.db")   # 連接資料庫
cursor = conn.cursor()   # 創建一個 cursor 物件




