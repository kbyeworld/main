import discord
from discord.ext import commands
from discord.commands import Option

import json
import datetime

from utils.embed import Embed


class JoinButton(discord.ui.Button):
    def __init__(self, author: discord.Member):
        super().__init__(
            emoji="✅",
            label="참가하기",
            custom_id=f"marble_{author.id}_join",
            style=discord.ButtonStyle.green
        )


    # async def callback(self, interaction: discord.Interaction):
    #     await interaction.response.defer()
    #     print(interaction.user)
    #     with open("./data/game.json", encoding='utf-8', mode="r") as f:
    #         mydict = json.loads(f.read())
    #     print(mydict)
    #     mydict[interaction.custom_id]["player"].append(interaction.user.id)
    #     print(mydict)
    #     print(interaction.custom_id)
    #     with open("./data/game.json", encoding='utf-8', mode="w") as f:
    #         json.dump(mydict, f, ensure_ascii=True)
    #     await interaction.response.send_message(f"참가 처리됨", ephemeral=True)


class marble_play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join = []

        with open("./data/game.json", encoding='utf-8', mode="r") as f:
            mydict = json.loads(f.read())
        for d in mydict:
            for member in d['players']: self.join.append(member)

    @commands.slash_command(name="gj")
    async def get_j(self, ctx: discord.ApplicationContext):
        await ctx.respond(self.join)

    @commands.slash_command(name="시작", description="마블 게이")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def play_start(self, ctx,
                       multie: Option(str, "플레이 종류를 선택해주세요.", choices=["이 서버에서 게임"], required=False, name="종류")):
        await ctx.defer()
        print(self.join)

        with open("./data/game.json", encoding='utf-8', mode="r") as f:
            mydict = json.loads(f.read())
        try:
            if mydict[str(ctx.author.id)] or ctx.author.id in self.join:
                return await ctx.respond("이미 생성되거나 참여한 게임이 있습니다!", ephemeral=True)
        except KeyError:
            pass

        if ctx.author.id in self.join:
            return await ctx.respond("이미 생성되거나 참여한 게임이 있습니다!", ephemeral=True)

        kind = ({'이 서버에서 게임': "Server", '글로벌 멀티게임': "Global_Multie", None: 'Server'})[multie]
        start_msg = await ctx.respond(
            f"<a:loading:911450437209706556> {'이 서버에서' if kind == 'Server' else '글로벌 멀티'} 게임 시작을 준비하고 있어요...")
        thread = await ctx.channel.create_thread(name=f"{ctx.author}님의 마블게임방", message=start_msg)
        embed = Embed.default(title="🚩 게임 시작하기", description=f"{ctx.author}님이 마블 게임을 시작하셨습니다.\n참가하시려면 아래의 버튼을 눌러주세요.",
                              timestamp=datetime.datetime.now())
        Embed.user_footer(embed, ctx.author)

        mydict[ctx.author.id] = {"channel_id": thread.id, "players": [ctx.author.id], "start_at": datetime.datetime.now().timestamp()}

        with open("./data/game.json", encoding='utf-8', mode="w") as f:
            json.dump(mydict, f, indent=4, ensure_ascii=False)

        await thread.add_user(ctx.guild.get_member(ctx.author.id))
        self.join.append(ctx.author.id)

        view = discord.ui.View()
        view.add_item(JoinButton(ctx.author))

        try:
            await start_msg.edit(content=f"✅ {'이 서버에서' if kind == 'Server' else '글로벌 멀티'} 게임이 시작 준비중이에요.", embed=embed, view=view)
        except Exception as error:
            pass

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        print(self.join)
        if interaction.type == discord.InteractionType.component:
            if interaction.custom_id.startswith("marble_") and interaction.custom_id.endswith("_join"):
                user_id = interaction.custom_id.replace("marble_", "").replace("_join", "")
                with open("./data/game.json", encoding='utf-8', mode="r") as f:
                    mydict = json.loads(f.read())
                if interaction.user.id in self.join:
                    return await interaction.response.send_message("이미 생성되거나 참여한 게임이 있습니다!", ephemeral=True)
                try:
                    game_data = mydict[user_id]
                except KeyError:
                    return await interaction.response.send_message("존재하지 않는 게임이에요.", ephemeral=True)
                if int(user_id) == interaction.user.id:
                    try:
                        await interaction.guild.get_thread(int(game_data["channel_id"])).archive(locked=True)
                    except discord.Forbidden:
                        await interaction.guild.get_thread(int(game_data["channel_id"])).archive()
                    msg = await interaction.channel.fetch_message(int(game_data["channel_id"]))
                    await msg.edit(content="⏹ 게임이 취소되었어요!", view=None, embed=Embed.user_footer(Embed.default(timestamp=datetime.datetime.now(), title="⏹ 게임 취소", description="호스트가 게임을 취소하였습니다."), interaction.user))
                    del mydict[user_id]
                    json.dump(mydict, open("./data/game.json", encoding='utf-8', mode="w"), ensure_ascii=True)
                    return await interaction.response.send_message(f"게임이 취소되었습니다.", ephemeral=True)
                if interaction.user.id in game_data["players"]:
                    return await interaction.response.send_message(f"이미 참가처리 되었습니다!", ephemeral=True)
                print(mydict)
                game_data["players"].append(interaction.user.id)
                print(mydict)
                print(interaction.custom_id)
                print(interaction.user.id)
                with open("./data/game.json", encoding='utf-8', mode="w") as f:
                    json.dump(mydict, f, ensure_ascii=True)
                thread = interaction.guild.get_thread(game_data['channel_id'])
                await thread.add_user(interaction.guild.get_member(interaction.user.id))
                await interaction.response.send_message(f"참가 처리가 완료되었어요.", ephemeral=True)
                self.join.append(interaction.user.id)
                # print(self.join)


def setup(bot):
    bot.add_cog(marble_play(bot))
