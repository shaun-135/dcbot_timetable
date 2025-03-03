import discord
from discord.ext import commands, tasks
from discord.ui import Select, View
from dotenv import load_dotenv
import sqlite3
import os
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import asyncio
import aiosqlite

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
    timetable = cursor.fetchall()
    conn.close()
    if not timetable:
        await interaction.response.send_message("沒有課表數據")
        return
    
    # 設置中文字體
    plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]  
    
    # 將數據轉換為 DataFrame
    df = pd.DataFrame(timetable, columns=["subject", "weekday", "time_slot"])

    # 生成課表圖表

    fig, ax = plt.subplots()
    column_labels = ["", "一", "二", "三", "四", "五"]
    ax.axis("off")
    ax.table(cellText=df.values, colLabels=column_labels, loc="center", cellLoc="center")
    


    # 保存圖表為圖像文件
    chart_path = f"./downloads/{userid}_timetable_chart.png"
    plt.savefig(chart_path)
    plt.close()

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

@tasks.loop(minutes=10)
async def timetable_reminder():
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, subject, weekday, time_slot FROM schedule")
    schedules = cursor.fetchall()
    conn.close()
    
    today = datetime.datetime.now().strftime("%A")
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    for user_id, subject, weekday, time_slot in schedules:
        if weekday == today and time_slot == current_time:
            user = await bot.fetch_user(user_id)
            await user.send(f"提醒: {subject} 即將開始")

bot.run(token) # 啟動機器人
