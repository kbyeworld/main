import datetime

from discord.ext import commands

from utils.embed import Embed


class user(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
    bot.add_cog(user(bot))