import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import sqlite3
import os
import datetime
import matplotlib.pyplot as plt
import pandas as pd

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
    print(f"Bot is ready. 名稱 ---> {bot.user}")
    print(f"已載入 {command_count} 項指令")

# 新增課表指令
@bot.tree.command(name="add_timetable", description="新增課表")
async def add_schedule(interaction: discord.Interaction, subject: str, weekday: str, time_slot):
    user_id = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO schedule (user_id, subject, weekday, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
                   (user_id, subject, weekday, start_time, end_time))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"已新增課表: {subject} 在 星期{weekday}，時間: {start_time} - {end_time}")

# 刪除課表指令
@bot.tree.command(name="delete_timetable", description="刪除課表")
async def delete_schedule(interaction: discord.Interaction, subject: str, weekday: str, start_time: str, end_time: str):
    user_id = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedule WHERE user_id = ? AND subject = ? AND weekday = ? AND start_time = ? AND end_time = ?",
                   (user_id, subject, weekday, start_time, end_time))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"已刪除課表: {subject} 在 星期{weekday}，時間: {start_time} - {end_time}")

# 刪除全部課表指令
@bot.tree.command(name="delete_all_schedule", description="刪除全部課表")
async def delete_all_schedule(interaction: discord.Interaction):
    user_id = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedule WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    await interaction.response.send_message("已刪除全部課表")

# 批量導入課表指令(csv)
@bot.tree.command(name="import_timetable", description="批量導入課表")
async def import_schedule(interaction: discord.Interaction, file: discord.Attachment):
    user_id = interaction.user.id
    file_path = f"temp_{user_id}.csv"
    await file.save(file_path)

    try:
        df = pd.read_csv(file_path)
        conn = sqlite3.connect("user.db")
        cursor = conn.cursor()

        for index, row in df.iterrows():
            try:
                cursor.execute("INSERT INTO schedule (user_id, subject, weekday, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
                               (user_id, row['subject'], row['weekday'], row['start_time'], row['end_time']))
            except sqlite3.IntegrityError:
                continue

        conn.commit()
        await interaction.response.send_message("課表已成功導入。")
    except Exception as e:
        await interaction.response.send_message(f"導入課表時發生錯誤: {e}")
    finally:
        conn.close()
        os.remove(file_path)

# 新增考試指令
@bot.tree.command(name="add_exam", description="新增考試")
async def add_exam(interaction: discord.Interaction, subject: str, date: str):
    user_id = interaction.user.id
    try:
        # 確保日期格式正確
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        await interaction.response.send_message("日期格式錯誤，請使用 YYYY-MM-DD 格式")
        return

    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO exams (user_id, subject, date) VALUES (?, ?, ?)", (user_id, subject, date))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"已新增考試: {subject} 在 {date}")

# 刪除考試指令
@bot.tree.command(name="delete_exam", description="刪除考試")
async def delete_exam(interaction: discord.Interaction, subject: str, date: str):
    user_id = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exams WHERE user_id = ? AND subject = ? AND date = ?", (user_id, subject, date))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"已刪除考試: {subject} 在 {date}")

# 查詢考試清單指令
@bot.tree.command(name="exam_countdown", description="查詢考試剩餘時間")
async def exam_countdown(interaction: discord.Interaction):
    user_id = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subject, date FROM exams WHERE user_id = ?", (user_id,))
    exams = cursor.fetchall()
    conn.close()

    today = datetime.date.today()
    response = "考試清單:\n"
    for subject, date_str in exams:
        exam_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        days_left = (exam_date - today).days
        response += f"{subject}: 還有 {days_left} 天\n"

    await interaction.response.send_message(response)

# 查看課表指令
@bot.tree.command(name="view_timetable", description="查看課表")
async def view_schedule(interaction: discord.Interaction):
    user_id = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subject, weekday, start_time, end_time FROM schedule WHERE user_id = ?", (user_id,))
    schedule = cursor.fetchall()
    conn.close()

    if not schedule:
        await interaction.response.send_message("沒有找到課表資料。")
        return

    # 生成課表圖表
    weekdays = [row[1] for row in schedule]
    subjects = [row[0] for row in schedule]
    start_times = [datetime.datetime.strptime(row[2], "%H:%M").time() for row in schedule]
    end_times = [datetime.datetime.strptime(row[3], "%H:%M").time() for row in schedule]

    fig, ax = plt.subplots()
    for i, (subject, weekday, start_time, end_time) in enumerate(zip(subjects, weekdays, start_times, end_times)):
        start_time_str = start_time.strftime("%H:%M")
        end_time_str = end_time.strftime("%H:%M")
        ax.plot([start_time_str, end_time_str], [i, i], marker='o', label=subject)

    ax.set_yticks(range(len(subjects)))
    ax.set_yticklabels(subjects)
    ax.set_xlabel('時間')
    ax.set_title('課表')

    plt.legend()
    plt.tight_layout()

    # 保存圖表為圖片
    image_path = "schedule.png"
    plt.savefig(image_path)
    plt.close()

    # 發送圖片到 Discord 頻道
    await interaction.response.send_message(file=discord.File(image_path))

# 定時提醒功能
@tasks.loop(hours=24)
async def check_exams():
    await bot.wait_until_ready()
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
            await user.send(f"提醒: 明天有 {subject} 考試!")

# 定時檢查課表功能
@tasks.loop(seconds=20)
async def check_schedules():
    await bot.wait_until_ready()
    now = datetime.datetime.now()
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, subject, weekday, start_time FROM schedule")
    schedules = cursor.fetchall()
    conn.close()

    for user_id, subject, weekday, start_time_str in schedules:
        # 將中文的 weekday 轉換為具體的日期
        today = datetime.datetime.now().date()
        weekday_map = {'日': 6, '一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5}
        days_ahead = (weekday_map[weekday] - today.weekday() + 7) % 7
        schedule_date = today + datetime.timedelta(days=days_ahead)
        start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
        schedule_datetime = datetime.datetime.combine(schedule_date, start_time)
        time_diff = (schedule_datetime - now).total_seconds()
        if 0 < time_diff <= 600:  # 提前十分鐘提醒
            user = await bot.fetch_user(user_id)
            await user.send(f"課表提醒: {subject} 課程即將開始，時間: {start_time_str}")

bot.run(token)
