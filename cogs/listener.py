import datetime
import logging

import discord
from discord.ext import commands

from utils.embed import Embed


class Listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("kbyeworld")

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info(f"🚥 {self.bot.user}이(가) 준비되었습니다.")

    @commands.Cog.listener()
    async def on_application_command(self, ctx):
        self.logger.info(f"💻 {ctx.author}({ctx.author.id}) - '/{ctx.command}' 명령어 사용")

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        try:
            error = error.original
        except:
            pass

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.NotOwner):
            embed = Embed.perm_warn(
                timestamp=datetime.datetime.now(), description="당신은 봇의 관리자가 아닙니다."
            )
            Embed.user_footer(embed, ctx.author)

        elif isinstance(error, commands.CommandOnCooldown):
            cooldown = int(error.retry_after)
            hours = cooldown // 3600
            minutes = (cooldown % 3600) // 60
            seconds = cooldown % 60
            time = []
            if not hours == 0:
                time.append(f"{hours}시간")
            if not minutes == 0:
                time.append(f"{minutes}분")
            if not seconds == 0:
                time.append(f"{seconds:02}초")
            embed = Embed.warn(
                timestamp=datetime.datetime.now(),
                description=f"이 명령어는 ``{' '.join(time)}`` 뒤에 사용하실 수 있습니다.",
            )
            Embed.user_footer(embed, ctx.author)

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = Embed.warn(
                timestamp=datetime.datetime.now(), description="필요한 값이 존재하지 않습니다."
            )
            Embed.user_footer(embed, ctx.author)

        elif isinstance(error, commands.MemberNotFound):
            embed = Embed.warn(
                timestamp=datetime.datetime.now(), description="존재하지 않는 멤버입니다."
            )
            Embed.user_footer(embed, ctx.author)

        elif isinstance(error, discord.errors.CheckFailure):
            return

        elif str(error) == "" or error == None or str(error) == None:
            return

        else:
            embed = Embed.error(
                timestamp=datetime.datetime.now(),
                description=f"```py\n{error}\n```",
            )
            Embed.user_footer(embed, ctx.author)
            self.logger.error(f"❌ | {ctx.author}({ctx.author.id}) - {error}")

        try:
            return await ctx.respond(
                embed=embed,
                ephemeral=True,
            )
        except:
            try:
                return await ctx.respond(
                    embed=embed,
                )
            except:
                return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Listener(bot))
