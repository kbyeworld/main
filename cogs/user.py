import datetime

import discord
from discord.ext import commands

from utils.embed import Embed
from utils.database import UserDatabase

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="가입",
        description="K-BYEWORLD의 서비스에 가입합니다.",
    )
    async def user_register(self, ctx):
        await ctx.defer(ephemeral=True)
        result = await UserDatabase.add(ctx.author.id)
        await ctx.respond(result['result'])

    @commands.slash_command(
        name="탈퇴",
        description="K-BYEWORLD의 서비스에서 탈퇴합니다.",
    )
    async def user_delete(self, ctx):
        await ctx.defer(ephemeral=True)
        result = await UserDatabase.delete(ctx.author.id)
        await ctx.respond(result['result'])

def setup(bot):
    bot.add_cog(User(bot))
