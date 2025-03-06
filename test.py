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
import webserver
from matplotlib import font_manager

today = datetime.date.today()

os.makedirs("./downloads", exist_ok=True)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN1")


@tasks.loop(seconds=5)
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

webserver.keep_alive()
bot.run(token)