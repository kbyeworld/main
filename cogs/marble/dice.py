import random
import asyncio
import datetime

import discord
from discord.ext import commands

from utils.json_util import loadjson, savejson
from utils.respond import send_response
from utils.pan import pan
from utils.embed import Embed

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.is_component() and interaction.custom_id.startswith("dice_"):
            if str(interaction.user.id) == interaction.custom_id.replace("dice_", ""):
                con = str(random.randint(1, 6))
                game_data = loadjson(f"./data/game/{interaction.channel_id}.json")
                user_loc_num = 0
                for d in game_data["province"]:
                    if interaction.user.id in d["users"]:
                        if (user_loc_num + int(con)) >= len(game_data["province"]):
                            user_now_loc_num = (user_loc_num + int(con)) - len(
                                game_data["province"]
                            )
                        else:
                            user_now_loc_num = user_loc_num + int(con)
                        user_new_loc = game_data["province"][user_now_loc_num]["name"]
                        user_pre_loc_num = user_loc_num
                    user_loc_num += 1
                embed = Embed.default(description=f"<@{interaction.user.id}>님의 주사위는 ``{con}``입니다!\n현재 위치는 ``{user_new_loc}``입니다.", timestamp=datetime.datetime.now())
                view = discord.ui.View()
                view_data = []
                if game_data['province'][user_now_loc_num]['owner'] != "System":
                    embed.add_field(name="부가 정보", value=f">>> 땅 주인 : {f'''<@{game_data['province'][user_now_loc_num]['owner']}>''' if game_data['province'][user_now_loc_num]['owner'] != 0 else '소유주 없음 (구매 가능)'}")
                    if game_data['province'][user_now_loc_num]['owner'] == 0:
                        btn = discord.ui.Button(
                                emoji="💳",
                                label="땅 구매하기",
                                custom_id=f"buy_{interaction.user.id}",
                                style=discord.ButtonStyle.green,
                            )
                        view_data.append(btn)
                        view.add_item(btn)
                elif game_data['province'][user_now_loc_num]['owner'] == interaction.user.id:
                    btn = discord.ui.Button(
                        emoji="🏛️",
                        label="랜드마크 건설하기",
                        custom_id=f"built_{interaction.user.id}",
                        style=discord.ButtonStyle.blurple,
                    )
                    view_data.append(btn)
                    view.add_item(btn)
                msg = await send_response(
                    interaction,
                    content=f"<@{interaction.user.id}>",
                    embed=Embed.user_footer(embed, interaction.user),
                    view=view,
                    delete_after=(5 if game_data['province'][user_now_loc_num]['owner'] == "System" else None),
                )

                data = loadjson(f"./data/game/{interaction.channel_id}.json")
                province = data["province"]
                province[user_pre_loc_num]["users"].remove(interaction.user.id)
                province[user_now_loc_num]["users"].append(interaction.user.id)
                savejson(f"./data/game/{interaction.channel_id}.json", data)

                diceview = discord.ui.View()
                diceview.add_item(
                    discord.ui.Button(
                        emoji="🎲",
                        label="주사위 던지기",
                        custom_id=f"dice_0",
                        style=discord.ButtonStyle.blurple,
                    )
                )
                await (
                    await interaction.channel.fetch_message(int(interaction.message.id))
                ).edit(content=f"<@{interaction.user.id}>님의 차례입니다.", view=diceview)

                mydict = loadjson("./data/game.json")[game_data["game_owner"]][
                    "players"
                ]
                this_turn = list(mydict).index(interaction.user.id)
                if this_turn == (len(mydict) - 1):
                    next_turn = mydict[0]
                else:
                    next_turn = mydict[(list(mydict).index(interaction.user.id)) + 1]

                pan_data = await pan(data, game_data['players_data'])
                await (await interaction.channel.fetch_message(int(game_data['pan_msg']))).edit(content="\n".join(pan_data))

                if len(view_data) != 0:
                    def check(inter):
                        return inter.user.id == interaction.user.id and inter.channel.id == interaction.channel.id and ("buy_" in inter.custom_id or "built_" in inter.custom_id)

                    try:
                        interaction_check = await self.bot.wait_for(
                            "interaction", check=check, timeout=15.0
                        )
                        if interaction_check.custom_id.startswith("buy_"):
                            view.disable_all_items()
                            if int(data["players_data"][str(interaction.user.id)]["money"]) >= data['province'][user_now_loc_num]["money"]:
                                data["players_data"][str(interaction.user.id)]["money"] = str(int(data["players_data"][str(interaction.user.id)]["money"]) - data['province'][user_now_loc_num]["money"])
                                data["province"][user_now_loc_num]["owner"] = interaction.user.id
                                embed2 = Embed.default(timestamp=datetime.datetime.now(), title="✅ 구매 성공", description=f"`{user_new_loc}` 구매를 성공하였습니다!")
                                Embed.user_footer(embed2, interaction.user)
                                savejson(f"./data/game/{interaction.channel_id}.json", data)
                                await send_response(interaction_check, content=None, embeds=[embed2], ephemeral=True, delete_after=5)
                                await msg.edit_original_response(embeds=[embed, embed2], view=view, delete_after=5)
                                pan_data = await pan(data, data['players_data'])
                                await (await interaction.channel.fetch_message(int(data['pan_msg']))).edit(content="\n".join(pan_data))
                            else:
                                embed2 = Embed.default(timestamp=datetime.datetime.now(), title="❎ 구매 실패", description="소유한 돈이 부족하여 땅을 구매하지 못했습니다.")
                                Embed.user_footer(embed2, interaction.user)
                                await send_response(interaction_check, content=None, embeds=[embed2], ephemeral=True, delete_after=5)
                                await msg.edit_original_response(embeds=[embed, embed2], view=view, delete_after=5)
                    except asyncio.TimeoutError:
                        view.disable_all_items()
                        await msg.edit_original_response(view=view, delete_after=5)

                view = discord.ui.View()
                view.add_item(
                    discord.ui.Button(
                        emoji="🎲",
                        label="주사위 던지기",
                        custom_id=f"dice_{next_turn}",
                        style=discord.ButtonStyle.blurple,
                    )
                )
                await (
                    await interaction.channel.fetch_message(int(interaction.message.id))
                ).edit(content=f"<@{next_turn}>님의 차례입니다.", view=view)

            else:
                await send_response(
                    interaction,
                    f"지금은 <@{interaction.user.id}>님의 턴이 아닙니다.",
                    delete_after=5,
                    ephemeral=True,
                )


def setup(bot):
    bot.add_cog(DiceCog(bot))
