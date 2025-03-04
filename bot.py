import discord
from discord.ext import commands, tasks
from discord.ui import Select, View
from dotenv import load_dotenv
import sqlite3
import os
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import aiosqlite
import asyncio
from flask import Flask

today = datetime.date.today()

os.makedirs("./downloads", exist_ok=True)

load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN1")

if token is None:
    raise ValueError("DISCORD_BOT_TOKEN1 環境變數未設置")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  # 同步指令
    command_count = len(bot.tree.get_commands())
    
    remind_exams.start()  # 啟動定時提醒考試任務
    delete_expired_exams.start()  # 啟動刪除過期考試任務

    print(f"Bot is ready. 名稱 ---> {bot.user}")
    print(f"已載入 {command_count} 項指令")

# 新增考試指令
@bot.tree.command(name="add_exam", description="新增考試")
async def add_exam(interaction: discord.Interaction, subject: str, date: str):
    userid = interaction.user.id
    try:
        # 確保日期格式正確
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        await interaction.response.send_message("日期格式錯誤，請使用 YYYY-MM-DD 格式")
        return

    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO exams (user_id, subject, date) VALUES (?, ?, ?)", (userid, subject, date))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"已新增考試: {subject} 在 {date}")

# 刪除考試指令
@bot.tree.command(name="delete_exam", description="刪除考試")
async def delete_exam(interaction: discord.Interaction, subject: str, date: str):
    userid = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exams WHERE user_id = ? AND subject = ? AND date = ?", (userid, subject, date))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"已刪除考試: {subject} 在 {date}")

# 查詢考試清單指令
@bot.tree.command(name="exam_list", description="查詢考試清單")
async def exam_check(interaction: discord.Interaction):
    userid = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subject, date FROM exams WHERE user_id = ?", (userid,))
    exams = cursor.fetchall()
    conn.close()

    response = "考試清單:\n"
    for subject, date_str in exams:
        exam_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        days_left = (exam_date - today).days
        if days_left == 0:
            response += f"今天有 {subject} 考試: \n"
        else:
            response += f"{subject}: 還有 {days_left} 天\n"

    await interaction.response.send_message(response)

# 新增課表指令
@bot.tree.command(name="add_timetable", description="新增課表")
async def add_timetable(interaction: discord.Interaction, subject: str, weekday: str, time_slot: str):
    userid = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO schedule (user_id, subject, weekday, time_slot) VALUES (?, ?, ?, ?)",
                   (userid, subject, weekday, time_slot))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"已新增課表: {subject} 在 {weekday} {time_slot}")

# 刪除課表指令
@bot.tree.command(name="delete_timetable", description="刪除課表")
async def delete_timetable(interaction: discord.Interaction, subject: str, weekday: str, time_slot: str):
    userid = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedule WHERE user_id = ? AND subject = ? AND weekday = ? AND time_slot = ?",
                   (userid, subject, weekday, time_slot))

# 匯入課表指令
@bot.tree.command(name="import_timetable", description="匯入課表")
async def import_timetable(interaction: discord.Interaction, attachment: discord.Attachment):
    userid = interaction.user.id
    file_path = f"./downloads/{userid}_{attachment.filename}" # 指定檔案路徑，並避免檔名重複
    await attachment.save(file_path)
    df = pd.read_csv(file_path)
    if attachment.filename.endswith(".csv"):
        df = pd.read_csv(file_path)
        conn = sqlite3.connect("user.db")
        cursor = conn.cursor()
        for _, row in df.iterrows():
            cursor.execute("INSERT INTO schedule (user_id, subject, weekday, time_slot) VALUES (?, ?, ?, ?)",
                           (userid, row["subject"], row["weekday"], row["time_slot"]))
        conn.commit()
        conn.close()
        
        await interaction.response.send_message(f"已成功上傳並處理檔案: {attachment.filename}")
    else:
        await interaction.response.send_message("請上傳 CSV 檔案")
    
# 查看課表指令
@bot.tree.command(name="check_timetable", description="查看課表")
async def check_timetable(interaction: discord.Interaction):
    userid = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subject, weekday, time_slot FROM schedule WHERE user_id = ?", (userid,))
    timetable_data = cursor.fetchall()
    conn.close()
    if not timetable_data:
        await interaction.response.send_message("沒有課表數據")
        return
    
    # 定義星期和時間對應表
    weekday_map = {1: "週一", 2: "週二", 3: "週三", 4: "週四", 5: "週五"}
    time_slot_map = {
        1: "08:10～09:00",
        2: "09:10～10:00",
        3: "10:10～11:00",
        4: "11:10～12:00",
        5: "13:00～13:50",
        6: "14:00～14:50",
        7: "15:00～15:50",
        8: "16:00～16:50",
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
    fig, ax = plt.subplots(figsize=(10, 16))
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
    fig.set_size_inches(6.5, 10.4)

    # 調整圖表的邊距
    plt.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)

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

    # 保存圖表為圖像文件
    chart_path = f"./downloads/{userid}_timetable_chart.png"
    plt.savefig(chart_path, bbox_inches="tight", pad_inches=0.05)

    # 發送圖像文件到 Discord
    await interaction.response.send_message(file=discord.File(chart_path))

# 查看延遲指令
@bot.tree.command(name="ping", description="查看延遲")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"延遲: {round(bot.latency * 1000)}ms")

# 定時提醒考試
@tasks.loop(hours=24)
async def remind_exams():
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, subject, date FROM exams")
    exams = cursor.fetchall()
    conn.close()

    today = datetime.date.today()
    for user_id, subject, date_str in exams:
        exam_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        days_left = (exam_date - today).days
        if days_left == 1:
            user = await bot.fetch_user(user_id)
            await user.send(f"明天有考試: {subject}")
        elif days_left == 0:
            user = await bot.fetch_user(user_id)
            await user.send(f"今天有考試: {subject}")

# 刪除過期考試
@tasks.loop(hours=24)
async def delete_expired_exams():
    today = datetime.date.today().strftime("%Y-%m-%d")
    async with aiosqlite.connect("user.db") as db:
        await db.execute("DELETE FROM exams WHERE date < ?", (today,))
        await db.commit()

# 定時提醒課表
@tasks.loop(minutes=5)
async def timetable_reminder():
    async with aiosqlite.connect("user.db") as db:
        async with db.execute("SELECT user_id, subject, weekday, time_slot FROM schedule") as cursor:
            timetable = await cursor.fetchall()

    
    start_time = {
        1: "08:10",
        2: "09:10",
        3: "10:10",
        4: "11:10",
        5: "13:00",
        6: "14:00",
        7: "15:00",
        8: "16:00",
    }

    today = datetime.datetime.now().weekday() + 1  # 獲取今天是星期幾
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    for user_id, subject, weekday, time_slot in timetable:
        if int(weekday) == today:  # 轉成數字比對
            start_time_dt = datetime.datetime.strptime(start_time[int(time_slot)], "%H:%M").time()
            current_time_dt = datetime.datetime.strptime(current_time, "%H:%M").time()

            # 計算時間差（分鐘）
            time_diff = (datetime.datetime.combine(datetime.date.today(), start_time_dt) - 
                         datetime.datetime.combine(datetime.date.today(), current_time_dt)).total_seconds() / 60

            if 0 < time_diff <= 5:
                user = await bot.fetch_user(user_id)
                await user.send(f"提醒: {subject} 即將開始")

bot.start(token)
