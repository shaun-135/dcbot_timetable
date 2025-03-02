import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Select, View
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

###

# 查看延遲指令
@bot.tree.command(name="ping", description="查看延遲")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"延遲: {round(bot.latency * 1000)}ms")


bot.run(token)