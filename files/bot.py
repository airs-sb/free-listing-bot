import discord
from discord.ext import commands
import json
import sqlite3
import os
from utils.database import initialize_database
from utils.listViews import ListViews
from utils.bedwars_database import initialize_bedwars_database
import requests


# Load main bot config.json for token
with open("config.json") as f:
    config = json.load(f)

initialize_database()
initialize_bedwars_database()

intents = discord.Intents.all()
bot = commands.Bot(intents=intents)



# Create SQLite connection
conn = sqlite3.connect('database.db')  # Changed to database.db
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bots (bot_id TEXT, folder TEXT, main_file TEXT, config TEXT)''')
conn.commit()

# Syncing the slash commands with Discord
@bot.event
async def on_ready():
    print(f'{bot.user} is online and ready!')
    activity = discord.CustomActivity(name="discord.gg/airs")  # Shows as "Playing with code"
    # Set the activity and status
    await bot.change_presence(status=discord.Status.online, activity=activity)
    bot.add_view(ListViews())

# Load the cogs
def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")

# Run the bot
if __name__ == "__main__":
    load_extensions()
    bot.run(config['token'])
