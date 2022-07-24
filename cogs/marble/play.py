import config

from discord.ext import commands
from discord.commands import Option

from utils.embed import Embed


class marble_play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="시작")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def testtest(self, ctx, multie: Option(str, "플레이 종류를 선택해주세요.", choices=["이 서버에서 게임"], required=False, name="종류")):
        await ctx.defer()
        whdfb = ({'이 서버에서 게임': "Server", '글로벌 멀티게임':"Global_Multie", None: 'Server'})[multie] # 종류
        start_msg = await ctx.respond(f"<a:loading:911450437209706556> {'이 서버에서' if whdfb == 'Server' else '글로벌 멀티'} 게임 시작을 준비하고 있어요...")
        await ctx.channel.create_thread(name=f"{ctx.author}님의 마블게임방", message=start_msg, auto_archive_duration=60)
        try:
            await start_msg.edit(content=f"✅ {'이 서버에서' if whdfb == 'Server' else '글로벌 멀티'} 게임이 시작 준비중이에요.")
        except Exception as error:
            pass

def setup(bot):
    bot.add_cog(marble_play(bot))