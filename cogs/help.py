import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Help cog loaded!")

    @commands.command()
    async def help(self, ctx):
        await ctx.send("Help Command under construction!")


async def setup(bot):
    await bot.add_cog(Help(bot))
