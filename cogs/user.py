import datetime

import discord
from discord.ext import commands

from utils.embed import Embed
from utils.database import UserDatabase


class ConfirmButton(discord.ui.View):
    def __init__(self, type):
        super().__init__()
        self.type = type

    @discord.ui.button(emoji="✅", label="진행하기", style=discord.ButtonStyle.green)
    async def confirm(self, button:discord.ui.Button, interaction: discord.Interaction):
        if self.type == "가입":
            result = await UserDatabase.add(interaction.user.id)
            if result['success']:
                embed = Embed.user_footer(Embed.default(timestamp=datetime.datetime.now(), title="✅ 가입 완료됨", description=result["result"]), interaction.user)
            else:
                embed = Embed.user_footer(Embed.default(timestamp=datetime.datetime.now(), title="❎ 가입 실패됨", description=result["result"]), interaction.user)
            return await interaction.response.edit_message(embed=embed, view=None)
        elif self.type == "탈퇴":
            result = await UserDatabase.delete(interaction.user.id)
            if result['success']:
                embed = Embed.user_footer(Embed.default(timestamp=datetime.datetime.now(), title="✅ 가입 완료됨", description=result["result"]), interaction.user)
            else:
                embed = Embed.user_footer(Embed.default(timestamp=datetime.datetime.now(), title="❎ 가입 실패됨", description=result["result"]), interaction.user)
            return await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(emoji="❎", label="취소하기", style=discord.ButtonStyle.red)
    async def cancel(self, button:discord.ui.Button, interaction: discord.Interaction):
        embed = Embed.user_footer(Embed.default(timestamp=datetime.datetime.now(), title="❎ 가입 취소됨", description="가입이 취소되었습니다."), interaction.user)
        return await interaction.response.edit_message(embed=embed, view=None)


class User(commands.Cog):
    def init(self, bot):
        self.bot = bot
        print("test")

    @commands.slash_command(
        name="가입",
        description="K-BYEWORLD의 서비스에 가입합니다.",
    )
    async def user_register(self, ctx):
        await ctx.defer(ephemeral=True)
        embed = Embed.default("👋 K-ByeWorld 서비스 가입", description="아래의 버튼을 눌러서 가입하세요.", timestamp=datetime.datetime.now())
        Embed.user_footer(embed, ctx.author)
        await ctx.respond(embed=embed, view=ConfirmButton(type="가입"))

    @commands.slash_command(
        name="탈퇴",
        description="K-BYEWORLD의 서비스에서 탈퇴합니다.",
    )
    async def user_delete(self, ctx):
        await ctx.defer(ephemeral=True)
        embed = Embed.default("👋 K-ByeWorld 서비스 탈퇴", description="아래의 버튼을 눌러서 탈퇴하세요.\n탈퇴 시 30일간 재가입이 불가합니다.", timestamp=datetime.datetime.now())
        Embed.user_footer(embed, ctx.author)
        await ctx.respond(embed=embed, view=ConfirmButton(type="탈퇴"))

def setup(bot):
    bot.add_cog(User(bot))
