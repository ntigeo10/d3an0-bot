import discord
from discord.ext import commands, tasks
import feedparser
import os
from dotenv import load_dotenv
import json

# Load .env from the parent directory (where main.py is located)
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(ENV_PATH)



class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.latest_entry = None
        self.channel_id = self.load_channel_id()
        self.check_news.start()
        self.rss_state = self.load_rss_state()

    def cog_unload(self):
        self.check_news.cancel()

    def save_channel_id(self, channel_id):
        """Saves the RSS channel ID to the .env file."""
        with open(ENV_PATH, "r") as file:
            lines = file.readlines()

        # Update or add the RSS_CHANNEL_ID entry
        with open(ENV_PATH, "w") as file:
            found = False
            for line in lines:
                if line.startswith("RSS_CHANNEL_ID="):
                    file.write(f"RSS_CHANNEL_ID={channel_id}\n")
                    found = True
                else:
                    file.write(line)
            if not found:
                file.write(f"\nRSS_CHANNEL_ID={channel_id}\n")

        # Reload environment variables
        load_dotenv(ENV_PATH)

    def load_channel_id(self):
        """Loads the RSS channel ID from the .env file."""
        return os.getenv("RSS_CHANNEL_ID")

    def load_rss_state(self):
        """Load the paused state from a JSON file."""
        try:
            with open("rss_state.json", "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"paused": False}  # Default to not paused

    def save_rss_state(self):
        """Save the RSS state (paused or not) to a JSON file."""
        with open("rss_state.json", "w") as file:
            json.dump(self.rss_state, file)


    @commands.command(name="setrss")
    @commands.has_any_role("Admin", "Moderator", "Founder")
    @commands.has_permissions(manage_channels=True)
    async def set_rss_channel(self, ctx):
        print(f"Command invoked by: {ctx.author}")
        self.channel_id = str(ctx.channel.id)  # Store as string to match .env format
        self.save_channel_id(self.channel_id)
        await ctx.send(f"✅ RSS updates will now be sent to {ctx.channel.mention}.")


    @commands.command(name="pauserss")
    @commands.has_any_role("Admin", "Moderator", "Founder")
    @commands.has_permissions(manage_channels=True)
    async def pauserss(self, ctx):
        self.rss_state["paused"] = True
        self.save_rss_state()
        await ctx.send("⏸️ RSS feed updates have been **paused**.")


    @commands.command(name="resumerss")
    @commands.has_any_role("Admin", "Moderator", "Founder")
    @commands.has_permissions(manage_channels=True)
    async def resumerss(self, ctx):
        self.rss_state["paused"] = False
        self.save_rss_state()
        await ctx.send("▶️ RSS feed updates have **resumed**.")


    @tasks.loop(seconds=60)
    async def check_news(self):
        """Checks the RSS feed and posts new articles in the selected channel."""
        feed_url = 'https://www.enternity.gr/Rssfeeds/News.html'  # Replace with actual RSS URL

        if self.rss_state["paused"]:
            print("⏸️ RSS is paused. No updates will be sent.")
            return  # Skip if paused




        if not self.channel_id:
            return  # No channel set, so do nothing

        channel = self.bot.get_channel(int(self.channel_id))
        if channel is None:
            print(f"Error: Could not find the channel with ID {self.channel_id}")
            return

        feed = feedparser.parse(feed_url)
        if not feed.entries:
            print("No new RSS entries found.")
            return

        latest_entry = feed.entries[0]
        if self.latest_entry is None or latest_entry.link != self.latest_entry.link:
            self.latest_entry = latest_entry
            title = latest_entry.title
            link = latest_entry.link
            summary = latest_entry.summary

            embed = discord.Embed(title=title, url=link, description=summary, color=discord.Color.blue())
            await channel.send(embed=embed)

    @check_news.before_loop
    async def before_check_news(self):
        await self.bot.wait_until_ready()

    @set_rss_channel.error
    async def set_rss_channel_error(self, ctx, error):
        print(f"Error: {error}")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")

async def setup(bot):
    await bot.add_cog(News(bot))