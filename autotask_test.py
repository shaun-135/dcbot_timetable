import discord
import datetime
import aiosqlite
from discord.ext import tasks, commands
import os
from dotenv import load_dotenv
import sqlite3

today = datetime.date.today()

os.makedirs("./downloads", exist_ok=True)

load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN1")

if token is None:
    raise ValueError("DISCORD_BOT_TOKEN1 環境變數未設置")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(seconds=10)
async def timetable_reminder():
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, subject, date FROM exams")
    exams = cursor.fetchall()
    conn.close()
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

@bot.event
async def on_ready():
    timetable_reminder.start()
    print(f"Bot is ready. 名稱 ---> {bot.user}")

bot.run(token)