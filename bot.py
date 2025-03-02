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
@bot.tree.command(name="exam_list", description="查詢考試清單")
async def exam_check(interaction: discord.Interaction):
    user_id = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subject, date FROM exams WHERE user_id = ?", (user_id,))
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

class Timeslot_select(Select):
    def __init__(self, subject, weekday):
        self.subject = subject
        self.weekday = weekday
        options = [            
            discord.SelectOption(label="08:00-09:00", description="08:00-09:00"),
            discord.SelectOption(label="09:00-10:00", description="09:00-10:00"),
            discord.SelectOption(label="10:00-11:00", description="10:00-11:00"),
            discord.SelectOption(label="11:00-12:00", description="11:00-12:00"),
            discord.SelectOption(label="12:00-13:00", description="12:00-13:00"),
            discord.SelectOption(label="13:00-14:00", description="13:00-14:00"),
            discord.SelectOption(label="14:00-15:00", description="14:00-15:00"),
            discord.SelectOption(label="15:00-16:00", description="15:00-16:00"),
        ]
        super().__init__(placeholder="請選擇時段", options=options min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        time_slot = self.values[0]
        conn = sqlite3.connect("user.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO schedule (user_id, subject, weekday, time_slot) VALUES (?, ?, ?, ?)",
                       (user_id, self.subject, self.weekday, time_slot))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"已新增課表: {self.subject} 在 {self.weekday} {time_slot}")

class TimeSlotView(View):
    def __init__(self, subject, weekday):
        super().__init__()
        self.add_item(Timeslot_select(subject, weekday))



@bot.tree.command(name="select", description="顯示下拉選單")
async def select(interaction: discord.Interaction):
    view = MyView()
    await interaction.response.send_message("請選擇一個選項：", view=view)

# 新增課表指令
@bot.tree.command(name="add_timetable", description="新增課表")
async def add_timetable(interaction: discord.Interaction, subject: str, weekday: str):
    view = TimeSlotView(subject, weekday)
    await interaction.response.send_message("請選擇一個時間段：", view=view)


# 刪除課表指令
@bot.tree.command(name="delete_timetable", description="刪除課表")
async def delete_timetable(interaction: discord.Interaction, subject: str, weekday: str, time_slot: str):
    user_id = interaction.user.id
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedule WHERE user_id = ? AND subject = ? AND weekday = ? AND time_slot = ?",
                   (user_id, subject, weekday, time_slot))

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

# 刪除過期考試
async def delete_expired_exams():
    while True:
        await asyncio.sleep(86400)  # 每天運行一次
        today = datetime.date.today().strftime("%Y-%m-%d")
        async with aiosqlite.connect("user.db") as db:
            await db.execute("DELETE FROM exams WHERE date < ?", (today,))
            await db.commit()

# 啟動主程式
async def main():
    asyncio.create_task(delete_expired_exams()) # 啟動刪除過期考試任務

    remind_exams.start() # 啟動定時提醒考試任務

bot.run(token)
