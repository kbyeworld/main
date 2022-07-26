import datetime

import aiohttp
import discord
from discord.ext import commands

import config
from utils.database import UserDatabase
from utils.embed import Embed


class ConfirmButton(discord.ui.View):
    def __init__(self, type):
        super().__init__()
        self.type = type

    @discord.ui.button(emoji="✅", label="진행하기", style=discord.ButtonStyle.green)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if self.type == "가입":
            result = await UserDatabase.add(interaction.user.id)
            if result["success"]:
                embed = Embed.user_footer(
                    Embed.default(
                        timestamp=datetime.datetime.now(),
                        title="✅ 가입 완료됨",
                        description=result["result"],
                    ),
                    interaction.user,
                )
            else:
                embed = Embed.user_footer(
                    Embed.default(
                        timestamp=datetime.datetime.now(),
                        title="❎ 가입 실패됨",
                        description=result["result"],
                    ),
                    interaction.user,
                )
            return await interaction.response.edit_message(embed=embed, view=None)
        elif self.type == "탈퇴":
            result = await UserDatabase.delete(interaction.user.id)
            if result["success"]:
                embed = Embed.user_footer(
                    Embed.default(
                        timestamp=datetime.datetime.now(),
                        title="✅ 가입 완료됨",
                        description=result["result"],
                    ),
                    interaction.user,
                )
            else:
                embed = Embed.user_footer(
                    Embed.default(
                        timestamp=datetime.datetime.now(),
                        title="❎ 가입 실패됨",
                        description=result["result"],
                    ),
                    interaction.user,
                )
            return await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(emoji="❎", label="취소하기", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = Embed.user_footer(
            Embed.default(
                timestamp=datetime.datetime.now(),
                title="❎ 가입 취소됨",
                description="가입이 취소되었습니다.",
            ),
            interaction.user,
        )
        return await interaction.response.edit_message(embed=embed, view=None)


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def account_check(self):
        result = await UserDatabase.find(self.author.id)
        if result:
            embed = Embed.perm_warn(
                timestamp=datetime.datetime.now(),
                description=f"{self.author.mention}님은 ``{self.bot.user.name} 서비스``에 에 이미 가입되어 있어요.\n``/탈퇴`` 명령어로 탈퇴하실 수 있어요.",
            )
            Embed.user_footer(embed, self.author)
            await self.respond(embed=embed, ephemeral=True)
            return False
        return True

    async def not_account_check(self):
        result = await UserDatabase.find(self.author.id)
        if result == None:
            embed = Embed.perm_warn(
                timestamp=datetime.datetime.now(),
                description=f"{self.author.mention}님은 ``{self.bot.user.name} 서비스``에 가입되어 있지 않아요.\n``/가입`` 명령어로 서비스에 가입하실 수 있어요.",
            )
            Embed.user_footer(embed, self.author)
            await self.respond(embed=embed, ephemeral=True)
            return False
        return True

    @commands.slash_command(
        name="가입",
        description="K-BYEWORLD의 서비스에 가입합니다.",
        checks=[account_check],
    )
    async def user_register(self, ctx):
        await ctx.defer(ephemeral=True)
        embed = Embed.default(
            "👋 K-ByeWorld 서비스 가입",
            description="아래의 버튼을 눌러서 가입하세요.",
            timestamp=datetime.datetime.now(),
        )
        Embed.user_footer(embed, ctx.author)
        await ctx.respond(embed=embed, view=ConfirmButton(type="가입"))

    @commands.slash_command(
        name="투표인증",
        description="K-BYEWORLD의 투표를 인증하여 보상을 받습니다.",
        checks=[not_account_check],
    )
    async def user_votecheck(self, ctx):
        await ctx.defer(ephemeral=True)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://kxdapi.herokuapp.com/get/{config.Setting.KxD_API_Key}/{ctx.author.id}"
            ) as response:
                json = await response.json()

        if json["message"]:
            # await UserDatabase.money.add(ctx.author.id, "1500000") # 인증 보상; 사용시 주석 해제
            await ctx.respond("투표해주셔서 감사합니다!")
        else:
            embed = Embed.default(
                "투표를 안하셨네요!",
                description="아직 투표를 하지 않으셨다구요?\n아래의 버튼을 눌러서 투표를 진행하세요!",
                timestamp=datetime.datetime.now()
            )
            Embed.user_footer(embed, ctx.author)
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    emoji="🔗",
                    label="투표하러가기",
                    style=discord.ButtonStyle.primary,
                    url="https://discord.com/channels/972789561719652412/1002922909309882448/1002923749198278686"
                )
            )
            await ctx.respond("https://discord.gg/WzFc9CYeJZ", embed=embed, view=view)

    @commands.slash_command(
        name="탈퇴",
        description="K-BYEWORLD의 서비스에서 탈퇴합니다.",
        checks=[not_account_check],
    )
    async def user_delete(self, ctx):
        await ctx.defer(ephemeral=True)
        embed = Embed.default(
            "👋 K-ByeWorld 서비스 탈퇴",
            description="아래의 버튼을 눌러서 탈퇴하세요.\n탈퇴 시 30일간 재가입이 불가합니다.",
            timestamp=datetime.datetime.now(),
        )
        Embed.user_footer(embed, ctx.author)
        await ctx.respond(embed=embed, view=ConfirmButton(type="탈퇴"))


def setup(bot):
    bot.add_cog(User(bot))
