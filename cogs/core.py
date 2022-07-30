import datetime

import discord
import pytz
from discord.ext import commands

from utils.embed import Embed


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="정보",
        description="K-BYEWORLD의 정보를 확인하는 명령어입니다.",
    )
    async def info(self, ctx):
        text = ""
        if ctx.channel.type != discord.ChannelType.private:
            text += f"`이 서버는 샤드 #{ctx.guild.shard_id+1}번에 속해있어요!`\n"
        text += "```"
        for shard in self.bot.shards.values():
            text += f"샤드 #{shard.id+1}: {int(shard.latency*1000)}ms\n"
        text += "```"
        embed = Embed.default(
            timestamp=datetime.datetime.now(), title=f"{self.bot.user.name} 정보"
        )
        embed.add_field(
            name="개발자",
            value=f">>> Happytree Samsung#7612\n스네이크블랭킷#6109",
            inline=False,
        )
        embed.add_field(name="서버 상태(핑)", value=text)
        Embed.user_footer(embed, ctx.author)
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="서포트 서버",
                emoji="<:discord_blurple:858642003327057930>",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/TD9BvMxhP6",
            )
        )
        await ctx.respond(embed=embed, view=view)

    @commands.slash_command(
        name="핑",
        description="K-BYEWORLD의 응답 시간을 확인하는 명령어입니다.",
    )
    async def ping(self, ctx):
        start_time: datetime = (datetime.datetime.utcnow()).replace(tzinfo=pytz.utc)
        await ctx.defer()
        embed = Embed.default(
            description=f"<a:loading:911450437209706556> 응답 시간을 측정하고 있어요....",
            timestamp=datetime.datetime.now(),
        )
        Embed.user_footer(embed, ctx.author)
        m = await ctx.respond(
            embed=embed,
        )
        target_time: datetime = (m.created_at).replace(tzinfo=pytz.utc)
        ping = target_time - start_time
        embed = Embed.default(
            title="🏓 Pong!",
            description=f"``디스코드 API 핑`` : {round(self.bot.latency * 1000)}ms\n``디스코드 인터렉션 핑`` : {int(ping.total_seconds() * 1000)}ms",
            timestamp=datetime.datetime.now(),
        )
        Embed.user_footer(embed, ctx.author)
        await ctx.edit(embed=embed)

    @commands.slash_command(
        name="개발자",
        description="K-BYEWORLD의 개발자를 확인해보세요!",
    )
    async def dev_check(self, ctx):
        embed = Embed.default(title="K-BYEWORLD 개발자", timestamp=datetime.datetime.now())
        embed.add_field(
            name="개발자",
            value=f">>> Happytree Samsung#7612\n스네이크블랭킷#6109",
            inline=False,
        )
        Embed.user_footer(embed, ctx.author)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Core(bot))
