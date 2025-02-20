import discord
from discord.ext import commands
import os
import asyncpraw
import random


class jokecommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            user_agent="discord_bot/1.0"
        )


    @commands.command()
    async def programmingjoke(self, ctx, subreddit_name: str = "ProgrammerHumor"):

        subreddit = await self.reddit.subreddit(subreddit_name)

        top_posts = [post async for post in subreddit.top(time_filter="month", limit=50)]

        if not top_posts:
            await ctx.send("There has been a problem with this command, try again later!")
            return

        random_post = random.choice(top_posts)

        programmingjokeembed = discord.Embed(
            title=random_post.title,
            url=f"https://www.reddit.com{random_post.permalink}",
            color=discord.Color.green()
        )

        if random_post.url.endswith(("jpg", "png", "gif", "jpeg", "webp")):
            programmingjokeembed.set_image(url=random_post.url)

        await ctx.send(embed=programmingjokeembed)

    @commands.command()
    async def dadjoke(self, ctx, subreddit_name: str = "DadJokes"):

        subreddit = await self.reddit.subreddit(subreddit_name)

        top_posts = [post async for post in subreddit.top(time_filter="month", limit=50)]

        if not top_posts:
            await ctx.send("There has been a problem with this command, try again later!")
            return

        random_post = random.choice(top_posts)

        dadjokeembed = discord.Embed(
            title=random_post.title,
            description=random_post.selftext[:1024],
            color=discord.Color.green()
        )


        await ctx.send(embed=dadjokeembed)

async def setup(bot):
    await bot.add_cog(jokecommands(bot))


