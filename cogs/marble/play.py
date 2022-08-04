import asyncio
import datetime
import logging
import os
import shutil

import discord
from discord.commands import Option
from discord.ext import commands

from utils.basic_util import is_text_channel, is_thread
from utils.database import UserDatabase
from utils.embed import Embed
from utils.game import marble_game
from utils.json_util import loadjson, savejson
from utils.respond import send_response


class marble_play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("kbyeworld")
        mydict = loadjson("./data/game.json")
        self.join = [member for dic in mydict for member in mydict[dic]["players"]]

        def delete_join(del_data):
            try:
                self.join.remove(del_data)
            except ValueError:
                pass

    async def finish(self, thread_id):
        province_data = loadjson(f"./data/game/{thread_id}.json")
        game_owner = province_data["game_owner"]
        os.remove(f"./data/game/{thread_id}.json")
        game_data = loadjson("./data/game.json")
        game_member = game_data[str(game_owner)]["players"]
        game_data.pop(game_owner)
        savejson("./data/game.json", game_data)
        [self.join.remove(userid) for userid in game_member]
        channel = self.bot.get_channel(int(thread_id))
        await channel.send("게임이 종료되었습니다. 60초 후 스레드가 아카이브됩니다.")
        await asyncio.sleep(60)
        await channel.archive(locked=True)

    async def start(self, interaction, user_id, game_thread, game_data, type):
        self.logger.info(f"⏩ | '{game_thread.id}'방의 게임이 시작되었습니다.")
        shutil.copyfile(
            "./data/province.json", f"./data/game/{game_thread.id}.json"
        )
        province_data = loadjson(f"./data/game/{game_thread.id}.json")
        province_data["game_owner"] = user_id
        province_data["province"][0]["users"] = game_data["players"]
        savejson(f"./data/game/{game_thread.id}.json", province_data)
        await (
            await interaction.channel.fetch_message(
                int(game_data["channel_id"])
            )
        ).edit(
            embed=Embed.user_footer(
                Embed.default(
                    timestamp=datetime.datetime.now(),
                    title="▶️ 게임 시작",
                    description="게임 최대 인원 3명이 모여 게임을 자동 시작합니다." if type == "auto" else "호스트가 게임을 시작했습니다.",
                ),
                interaction.user,
            ),
            view=None,
        )
        await marble_game(interaction, players=game_data["players"])

    async def account_check(self):
        result = await UserDatabase.find(self.author.id)
        print(result)
        if result == None:
            embed = Embed.perm_warn(
                timestamp=datetime.datetime.now(),
                description=f"{self.author.mention}님은 ``{self.bot.user.name} 서비스``에 가입하지 않으셨어요.\n``/가입`` 명령어로 서비스에 가입하실 수 있어요.",
            )
            Embed.user_footer(embed, self.author)
            await self.respond(embed=embed, ephemeral=True)
            return False
        return True

    @commands.slash_command(
        name="시작", description="마블 게임을 시작합니다.", checks=[account_check, is_text_channel]
    )
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
            description=f"{ctx.author}님이 마블 게임을 시작하셨습니다.\n참가하시려면 아래의 버튼을 눌러주세요.\n\n게임 생성자가 ``참가하기``를 클릭할 경우, 게임이 종료됩니다.",
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
        view.add_item(
            discord.ui.Button(
                emoji="✅",
                label="참가하기",
                custom_id=f"marble_{ctx.author.id}_join",
                style=discord.ButtonStyle.green,
            )
        )
        view.add_item(
            discord.ui.Button(
                emoji="➡️",
                label="시작하기",
                custom_id=f"marble_{ctx.author.id}_start",
                style=discord.ButtonStyle.blurple,
            )
        )

        try:
            await start_msg.edit(
                content=f"✅ {'이 서버에서' if kind == 'Server' else '글로벌 멀티'} 게임이 시작 준비중이에요.",
                embed=embed,
                view=view,
            )
        except Exception as error:
            pass

    @commands.slash_command(name="종료", description="[게임 생성자 전용] 게임을 종료합니다.", checks=[is_thread, account_check])
    async def finish_game(self, ctx):
        game_data = loadjson("./data/game/{}.json".format(ctx.channel.id))
        if ctx.author.id != int(game_data["game_owner"]):
            return await ctx.respond(
                f"이 명령어는 게임 생성자(<@{game_data['game_owner']}>)만 사용할수 있습니다.",
                ephemeral=True,
            )
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                emoji="✅",
                label="종료하기",
                custom_id=f"marble_finish_{ctx.channel.id}_confirm",
                style=discord.ButtonStyle.green,
            )
        )
        view.add_item(
            discord.ui.Button(
                emoji="❎",
                label="취소하기",
                custom_id=f"marble_finish_{ctx.channel.id}_cancel",
                style=discord.ButtonStyle.red,
            )
        )
        await ctx.respond("게임을 종료하시겠습니까?", view=view)

    @commands.slash_command(
        name="강제종료", description="게임 생성자가 오프라인일때 일반 참가자가 강제로 종료할수 있습니다.", checks=[account_check, is_thread],
    )
    async def force_finish_game(self, ctx):
        await ctx.defer(ephemeral=True)
        try:
            if os.path.isfile(f"./data/game/{ctx.channel.id}.json"):
                province_data = loadjson(f"./data/game/{ctx.channel.id}.json")
                if (
                    ctx.guild.get_member(int(province_data["game_owner"])).status
                    == discord.Status.offline
                ):
                    await ctx.respond("게임을 강제종료하였습니다.")
                    return await self.finish(ctx.channel.id)
                else:
                    await ctx.respond("게임 생성자가 오프라인이 아닙니다.")
            else:
                await ctx.respond("존재하지 않는 게임입니다.")
        except FileNotFoundError:
            await ctx.respond("존재하지 않는 게임입니다.")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            if interaction.custom_id.startswith(
                "marble_finish_"
            ) and interaction.custom_id.endswith("_confirm"):
                if interaction.user.id == int(
                    loadjson(f"./data/game/{interaction.channel.id}.json")["game_owner"]
                ):
                    await interaction.message.delete()
                    await self.finish(interaction.channel.id)

            if interaction.custom_id.startswith(
                "marble_"
            ) and interaction.custom_id.endswith("_join"):
                if (await UserDatabase.find(interaction.user.id)) is None:
                    embed = Embed.perm_warn(
                        timestamp=datetime.datetime.now(),
                        description=f"{interaction.user.mention}님은 ``{self.bot.user.name} 서비스``에 가입하지 않으셨어요.\n``/가입`` 명령어로 서비스에 가입하실 수 있어요.",
                    )
                    Embed.user_footer(embed, interaction.user)
                    return await send_response(
                        interaction, content=None, embed=embed, ephemeral=True
                    )
                user_id = interaction.custom_id.replace("marble_", "").replace(
                    "_join", ""
                )
                mydict = loadjson("./data/game.json")
                try:
                    game_data = mydict[user_id]
                    game_thread = interaction.guild.get_thread(
                        int(game_data["channel_id"])
                    )
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
                    self.logger.info(
                        f"❌ | {interaction.user}의 '{game_thread.id}'방이 취소되었습니다."
                    )
                    return await send_response(
                        interaction, content=f"게임이 취소되었어요.", ephemeral=True
                    )
                if interaction.user.id in game_data["players"]:
                    self.join.remove(interaction.user.id)
                    mydict[user_id]["players"].remove(interaction.user.id)
                    try:
                        await game_thread.remove_user(
                            interaction.guild.get_member(interaction.user.id)
                        )
                    except discord.Forbidden:
                        pass
                    savejson("./data/game.json", mydict)
                    self.logger.info(
                        f"📤 | {interaction.user}가 '{game_thread.id}'방에서 퇴장하였습니다."
                    )
                    return await send_response(
                        interaction,
                        content=f"게임 대기실에서 퇴장했어요. 참가 버튼을 누르면 다시 참여하실 수 있어요!",
                        ephemeral=True,
                    )
                if interaction.user.id in self.join:
                    return await send_response(
                        interaction, content="이미 생성되거나 참여한 게임이 있어요.", ephemeral=True
                    )
                game_data["players"].append(interaction.user.id)
                savejson("./data/game.json", mydict)
                await game_thread.add_user(
                    interaction.guild.get_member(interaction.user.id)
                )
                self.logger.info(
                    f"📥 | {interaction.user}가 '{game_thread.id}'방에 입장하였습니다."
                )
                await send_response(
                    interaction, content=f"참가 처리가 완료되었어요.", ephemeral=True
                )
                self.join.append(interaction.user.id)

                if len(game_data["players"]) == 3:
                    await game_thread.send("게임 시작 가능 인원인 3명이 모였습니다! 게임을 시작합니다.")
                    await self.start(interaction, user_id, game_thread, game_data, type="auto")

            if interaction.custom_id.startswith(
                "marble_"
            ) and interaction.custom_id.endswith("_start"):
                if (await UserDatabase.find(interaction.user.id)) is None:
                    embed = Embed.perm_warn(
                        timestamp=datetime.datetime.now(),
                        description=f"{interaction.user.mention}님은 ``{self.bot.user.name} 서비스``에 가입하지 않으셨어요.\n``/가입`` 명령어로 서비스에 가입하실 수 있어요.",
                    )
                    Embed.user_footer(embed, interaction.user)
                    return await send_response(
                        interaction, content=None, embed=embed, ephemeral=True
                    )
                user_id = interaction.custom_id.replace("marble_", "").replace(
                    "_start", ""
                )
                if int(user_id) != interaction.user.id:
                    return await send_response(
                        interaction, content="게임의 호스트만 시작할 수 있어요.", ephemeral=True
                    )
                mydict = loadjson("./data/game.json")
                try:
                    game_data = mydict[user_id]
                    game_thread = interaction.guild.get_thread(
                        int(game_data["channel_id"])
                    )
                except KeyError:
                    return await send_response(
                        interaction, content="존재하지 않는 게임이에요.", ephemeral=True
                    )

                if len(game_data["players"]) == 1:
                    return await send_response(
                        interaction,
                        content="1명으로 게임을 시작할 수 없습니다.",
                        embed=None,
                        ephemeral=True,
                    )
                else:
                    await self.start(interaction, user_id, game_thread, game_data, type="btn")

def setup(bot):
    bot.add_cog(marble_play(bot))
