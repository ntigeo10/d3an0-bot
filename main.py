import discord
import os
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv(".env")

TOKEN: str = os.getenv("TOKEN")
BOT_PREFIX: str = os.getenv("BOT_PREFIX")

intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded {filename}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()


async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


asyncio.run(main())
