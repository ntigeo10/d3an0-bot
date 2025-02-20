import discord
from discord.ext import commands
import requests
import asyncpraw
import os
from dotenv import load_dotenv
import random

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(ENV_PATH)

class marvelRelated(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            user_agent="discord_bot/1.0"
        )

    @commands.command(name="nextmcu")
    async def marvel_info(self, ctx):
        """Fetches and displays upcoming Marvel movies and series."""
        try:
            response = requests.get("https://www.whenisthenextmcufilm.com/api")
            data = response.json()

            if response.status_code == 200 and data:
                title = data.get("title", "N/A")
                release_date = data.get("release_date", "N/A")
                overview = data.get("overview", "No overview available.")
                days_until = data.get("days_until", "N/A")
                next_production = data.get("following_production", {})
                next_title = next_production.get("title", "N/A")

                embed = discord.Embed(
                    title="Upcoming Marvel Cinematic Universe Release",
                    color=discord.Color.red()
                )
                embed.add_field(name="Title", value=title, inline=False)
                embed.add_field(name="Release Date", value=release_date, inline=False)
                embed.add_field(name="Days Until Release", value=days_until, inline=False)
                embed.add_field(name="Overview", value=overview, inline=False)
                embed.add_field(name="Following Production", value=next_title, inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send("Could not retrieve Marvel information at this time.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(name="marvelmeme")
    async def marvel_meme(self, ctx, subreddit_name: str = "marvelmemes"):
        subreddit = await self.reddit.subreddit(subreddit_name)

        top_posts = [post async for post in subreddit.top(time_filter="month", limit=100)]

        if not top_posts:
            await ctx.send("There has been a problem with this command, try again later!")
            return

        random_post = random.choice(top_posts)

        embed = discord.Embed(
            title=random_post.title,
            url=f"https://www.reddit.com{random_post.permalink}",
            color=discord.Color.red()
        )

        if random_post.url.endswith(("jpg", "png", "gif", "jpeg", "webp")):
            embed.set_image(url=random_post.url)


        await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(marvelRelated(bot))
