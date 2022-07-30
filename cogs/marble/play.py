import datetime
import json
import logging

import discord
from discord.commands import Option
from discord.ext import commands

from utils.embed import Embed
from utils.json_util import loadjson, savejson
from utils.respond import send_response


class marble_play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("kbyeworld")
        mydict = loadjson("./data/game.json")
        self.join = [member for dic in mydict for member in mydict[dic]["players"]]

    @commands.slash_command(name="시작", description="마블 게임을 시작합니다.")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def play_start(
        self,
        ctx,
        multie: Option(
            str, "플레이 종류를 선택해주세요.", choices=["이 서버에서 게임"], required=False, name="종류"
        ),
    ):
        await ctx.defer()

        mydict = loadjson("./data/game.json")
        try:
            if mydict[str(ctx.author.id)] or ctx.author.id in self.join:
                return await ctx.respond("이미 생성되거나 참여한 게임이 있습니다!", ephemeral=True)
        except KeyError:
            pass

        if ctx.author.id in self.join:
            return await ctx.respond("이미 생성되거나 참여한 게임이 있습니다!", ephemeral=True)

        kind = ({"이 서버에서 게임": "Server", "글로벌 멀티게임": "Global_Multie", None: "Server"})[
            multie
        ]
        start_msg = await ctx.respond(
            f"<a:loading:911450437209706556> {'이 서버에서' if kind == 'Server' else '글로벌 멀티'} 게임 시작을 준비하고 있어요..."
        )
        thread = await ctx.channel.create_thread(
            name=f"{ctx.author}님의 마블게임방", message=start_msg
        )
        embed = Embed.default(
            title="🚩 게임 시작하기",
            description=f"{ctx.author}님이 마블 게임을 시작하셨습니다.\n참가하시려면 아래의 버튼을 눌러주세요.",
            timestamp=datetime.datetime.now(),
        )
        Embed.user_footer(embed, ctx.author)

        mydict[ctx.author.id] = {
            "channel_id": thread.id,
            "players": [ctx.author.id],
            "start_at": datetime.datetime.now().timestamp(),
        }

        savejson("./data/game.json", mydict)

        await thread.add_user(ctx.guild.get_member(ctx.author.id))
        self.join.append(ctx.author.id)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(emoji="✅", label="참가하기", custom_id=f"marble_{ctx.author.id}_join", style=discord.ButtonStyle.green))
        view.add_item(discord.ui.Button(emoji="➡️", label="시작하기", custom_id=f"marble_{ctx.author.id}_start", style=discord.ButtonStyle.blurple))

        try:
            await start_msg.edit(
                content=f"✅ {'이 서버에서' if kind == 'Server' else '글로벌 멀티'} 게임이 시작 준비중이에요.",
                embed=embed,
                view=view,
            )
        except Exception as error:
            pass

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            if interaction.custom_id.startswith(
                "marble_"
            ) and interaction.custom_id.endswith("_join"):
                user_id = interaction.custom_id.replace("marble_", "").replace(
                    "_join", ""
                )
                mydict = loadjson("./data/game.json")
                try:
                    game_data = mydict[user_id]
                    game_thread = interaction.guild.get_thread(int(game_data["channel_id"]))
                except KeyError:
                    return await send_response(
                        interaction, content="존재하지 않는 게임이에요.", ephemeral=True
                    )
                if int(user_id) == interaction.user.id:
                    try:
                        await game_thread.archive(locked=True)
                    except discord.Forbidden:
                        await game_thread.archive()
                    msg = await interaction.channel.fetch_message(
                        int(game_data["channel_id"])
                    )
                    await msg.edit(
                        content="⏹ 게임이 취소되었어요!",
                        view=None,
                        embed=Embed.user_footer(
                            Embed.default(
                                timestamp=datetime.datetime.now(),
                                title="⏹ 게임 취소",
                                description="호스트가 게임을 취소하였습니다.",
                            ),
                            interaction.user,
                        ),
                    )
                    for player in mydict[user_id]["players"]:
                        self.join.remove(player)
                    del mydict[user_id]
                    savejson("./data/game.json", mydict)
                    return await send_response(
                        interaction, content=f"게임이 취소되었어요.", ephemeral=True
                    )
                if interaction.user.id in game_data["players"]:
                    self.join.remove(interaction.user.id)
                    mydict[user_id]['players'].remove(interaction.user.id)
                    try:
                        await game_thread.remove_user(interaction.guild.get_member(interaction.user.id))
                    except discord.Forbidden:
                        pass
                    savejson("./data/game.json", mydict)
                    return await send_response(
                        interaction, content=f"게임 대기실에서 퇴장했어요. 참가 버튼을 누르면 다시 참여하실 수 있어요!", ephemeral=True
                    )
                if interaction.user.id in self.join:
                    return await send_response(
                        interaction, content="이미 생성되거나 참여한 게임이 있어요.", ephemeral=True
                    )
                game_data["players"].append(interaction.user.id)
                savejson("./data/game.json", mydict)
                await game_thread.add_user(interaction.guild.get_member(interaction.user.id))
                await send_response(
                    interaction, content=f"참가 처리가 완료되었어요.", ephemeral=True
                )
                self.join.append(interaction.user.id)

                if len(game_data["players"]) == 3:
                    await game_thread.send("게임 시작 가능 인원인 3명이 모였습니다! 게임을 시작합니다.")
                    await (await interaction.channel.fetch_message(int(game_data["channel_id"]))).edit(embed=Embed.user_footer(Embed.default(timestamp=datetime.datetime.now(), title="▶️ 게임 시작", description="게임 최대 인원 3명이 모여 게임을 자동 시작합니다."),interaction.user), view=None)


def setup(bot):
    bot.add_cog(marble_play(bot))
