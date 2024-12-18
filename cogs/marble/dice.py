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
                deletePass = False
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
                stopType = 0 # 0 : 구매, 1 : 건설, 2 : 통행료 지불

                if game_data['province'][user_now_loc_num]['owner'] != "System":
                    embed.add_field(name="부가 정보", value=f">>> 땅 주인 : {f'''<@{game_data['province'][user_now_loc_num]['owner']}>''' if game_data['province'][user_now_loc_num]['owner'] != 0 else '소유주 없음 (구매 가능)'}")
                    if game_data['province'][user_now_loc_num]['owner'] == 0:
                        btn = discord.ui.Button(
                            emoji="💳",
                            label="땅 구매하기",
                            custom_id=f"buy_{interaction.user.id}",
                            style=discord.ButtonStyle.green,
                        )
                        btn2 = discord.ui.Button(
                            emoji="▶️",
                            label="넘어가기",
                            custom_id=f"pass_{interaction.user.id}",
                            style=discord.ButtonStyle.gray,
                        )
                        view_data.append(btn)
                        view.add_item(btn)
                        view_data.append(btn2)
                        view.add_item(btn2)
                        stopType = 0

                    if game_data['province'][user_now_loc_num]['owner'] != 0 and game_data['province'][user_now_loc_num]['owner'] != interaction.user.id:
                        eventCard = False
                        for i in game_data["players_data"][str(interaction.user.id)]["eventCard"]:
                            if i["id"] == "billingPass":
                                eventCard = True

                        if eventCard == True:
                            stopType = 2
                            embed.add_field(name="통행료 지불 필요", value=f">>> 이 지역은 통행료 지불이 필요합니다. 지불 방식을 선택해주세요.", inline=False)
                            btn = discord.ui.Button(
                                emoji="💵",
                                label="통행료 지불하기",
                                custom_id=f"bill_{interaction.user.id}",
                                style=discord.ButtonStyle.blurple,
                            )
                            btn2 = discord.ui.Button(
                                emoji="💳",
                                label="통행료 면제 이용권 사용하기",
                                custom_id=f"billpass_{interaction.user.id}",
                                style=discord.ButtonStyle.blurple,
                            )
                            view_data.append(btn)
                            view.add_item(btn)
                            view_data.append(btn2)
                            view.add_item(btn2)

                        else:
                            embed.add_field(name="통행료 지불 완료", value=f">>> <@{game_data['province'][user_now_loc_num]['owner']}>님에게 통행료를 지불하였습니다.", inline=False)
                            game_data["players_data"][str(interaction.user.id)]["money"] = str(int(game_data["players_data"][str(interaction.user.id)]["money"]) - game_data['province'][user_now_loc_num]["money"])
                            game_data["players_data"][str(game_data['province'][user_now_loc_num]['owner'])]["money"] = str(int(game_data["players_data"][str(game_data['province'][user_now_loc_num]['owner'])]["money"]) + game_data['province'][user_now_loc_num]["money"])
                            deletePass = True

                elif game_data['province'][user_now_loc_num]['owner'] == interaction.user.id:
                    btn = discord.ui.Button(
                        emoji="🏛️",
                        label="랜드마크 건설하기",
                        custom_id=f"built_{interaction.user.id}",
                        style=discord.ButtonStyle.blurple,
                    )
                    view_data.append(btn)
                    view.add_item(btn)
                    stopType = 1
                    deletePass = True

                # elif game_data['province'][user_now_loc_num]['owner'] == "System":
                #     embed.add_field(name="시스템 땅", value=f">>> 시스템 땅입니다. 구매할 수 없습니다.", inline=False)

                msg = await send_response(
                    interaction,
                    content=f"<@{interaction.user.id}>",
                    embed=Embed.user_footer(embed, interaction.user),
                    view=view,
                    delete_after=(5 if (game_data['province'][user_now_loc_num]['owner'] == "System" or deletePass == True) else None),
                )

                province = game_data["province"]
                province[user_pre_loc_num]["users"].remove(interaction.user.id)
                province[user_now_loc_num]["users"].append(interaction.user.id)
                savejson(f"./data/game/{interaction.channel_id}.json", game_data)

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

                pan_data = await pan(game_data, game_data['players_data'])
                await (await interaction.channel.fetch_message(int(game_data['pan_msg']))).edit(content="\n".join(pan_data))

                if len(view_data) != 0:
                    def check(inter):
                        return inter.user.id == interaction.user.id and inter.channel.id == interaction.channel.id and ("buy_" in inter.custom_id or "built_" in inter.custom_id or "pass_" in inter.custom_id or "bill" in inter.custom_id or "billpass_" in inter.custom_id)

                    try:
                        interaction_check = await self.bot.wait_for(
                            "interaction", check=check, timeout=15.0
                        )
                        if interaction_check.custom_id.startswith("buy_"):
                            view.disable_all_items()
                            if int(game_data["players_data"][str(interaction.user.id)]["money"]) >= game_data['province'][user_now_loc_num]["money"]:
                                game_data["players_data"][str(interaction.user.id)]["money"] = str(int(game_data["players_data"][str(interaction.user.id)]["money"]) - game_data['province'][user_now_loc_num]["money"])
                                game_data["province"][user_now_loc_num]["owner"] = interaction.user.id
                                embed2 = Embed.default(timestamp=datetime.datetime.now(), title="✅ 구매 성공", description=f"`{user_new_loc}` 구매를 성공하였습니다!")
                                Embed.user_footer(embed2, interaction.user)
                                savejson(f"./data/game/{interaction.channel_id}.json", game_data)
                                await send_response(interaction_check, content=None, embeds=[embed2], ephemeral=True, delete_after=5)
                                await msg.edit_original_response(embeds=[embed, embed2], view=view, delete_after=5)
                                pan_data = await pan(game_data, game_data['players_data'])
                                await (await interaction.channel.fetch_message(int(game_data['pan_msg']))).edit(content="\n".join(pan_data))
                            else:
                                embed2 = Embed.default(timestamp=datetime.datetime.now(), title="❎ 구매 실패", description="소유한 돈이 부족하여 땅을 구매하지 못했습니다.")
                                Embed.user_footer(embed2, interaction.user)
                                await send_response(interaction_check, content=None, embeds=[embed2], ephemeral=True, delete_after=5)
                                await msg.edit_original_response(embeds=[embed, embed2], view=view, delete_after=5)

                        if interaction_check.custom_id.startswith("pass_"):
                            view.disable_all_items()
                            embed2 = Embed.default(timestamp=datetime.datetime.now(), title="▶️ 구매 넘김", description=f"`{user_new_loc}`를 구매하지 않았습니다.")
                            Embed.user_footer(embed2, interaction.user)
                            await send_response(interaction_check, content=None, embeds=[embed2], ephemeral=True, delete_after=5)
                            await msg.edit_original_response(embeds=[embed, embed2], view=view, delete_after=5)

                        if interaction_check.custom_id.startswith("bill_"):
                            view.disable_all_items()
                            game_data["players_data"][str(interaction.user.id)]["money"] = str(int(game_data["players_data"][str(interaction.user.id)]["money"]) - game_data['province'][user_now_loc_num]["money"])
                            game_data["players_data"][str(game_data['province'][user_now_loc_num]['owner'])]["money"] = str(int(game_data["players_data"][str(game_data['province'][user_now_loc_num]['owner'])]["money"]) + game_data['province'][user_now_loc_num]["money"])
                            savejson(f"./data/game/{interaction.channel_id}.json", game_data)
                            embed2 = Embed.default(timestamp=datetime.datetime.now(), title="💵 지불 완료", description=f" <@{game_data['province'][user_now_loc_num]['owner']}>님에게 통행료를 지불하였습니다.")
                            Embed.user_footer(embed2, interaction.user)
                            await send_response(interaction_check, content=None, embeds=[embed2], ephemeral=True, delete_after=5)
                            await msg.edit_original_response(embeds=[embed, embed2], view=view, delete_after=5)

                        if interaction_check.custom_id.startswith("billpass_"):
                            view.disable_all_items()
                            newCard = []
                            for i in game_data["players_data"][str(interaction.user.id)]["eventCard"]:
                                if i["id"] != "billingPass": newCard.append(i)
                            game_data["players_data"][str(interaction.user.id)]["eventCard"] = newCard
                            savejson(f"./data/game/{interaction.channel_id}.json", game_data)
                            embed2 = Embed.default(timestamp=datetime.datetime.now(), title="💳 카드 사용 완료", description=f"이벤트 카드를 사용하여 지불을 면제받았습니다.")
                            Embed.user_footer(embed2, interaction.user)
                            await send_response(interaction_check, content=None, embeds=[embed2], ephemeral=True, delete_after=5)
                            await msg.edit_original_response(embeds=[embed, embed2], view=view, delete_after=5)

                    except asyncio.TimeoutError:
                        view.disable_all_items()
                        if stopType == 2:
                            embed3 = Embed.default(timestamp=datetime.datetime.now(), title="❎ 시간 초과", description=f"시간 초과로 <@{game_data['province'][user_now_loc_num]['owner']}>님에게 통행료를 지불하였습니다.")
                            Embed.user_footer(embed3, interaction.user)
                            game_data["players_data"][str(interaction.user.id)]["money"] = str(int(game_data["players_data"][str(interaction.user.id)]["money"]) - game_data['province'][user_now_loc_num]["money"])
                            game_data["players_data"][str(game_data['province'][user_now_loc_num]['owner'])]["money"] = str(int(game_data["players_data"][str(game_data['province'][user_now_loc_num]['owner'])]["money"]) + game_data['province'][user_now_loc_num]["money"])
                            savejson(f"./data/game/{interaction.channel_id}.json", game_data)
                            await msg.edit_original_response(embeds=[embed3], view=view, delete_after=5)
                        else:
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

                infoEmbed = Embed.default()

                count = 1
                for player in game_data['players_data']:
                    infoEmbed.add_field(
                        name=f"{game_data['players_data'][player]['color']} Player {count}",
                        value=f"유저 : <@{player}>\n돈 : ``{(format(int(game_data['players_data'][player]['money']), ','))}원``",
                        inline=False,
                    )
                    count += 1

                await (
                    await interaction.channel.fetch_message(int(interaction.message.id))
                ).edit(content=f"<@{next_turn}>님의 차례입니다.", embed=infoEmbed, view=view)

            else:
                await send_response(
                    interaction,
                    f"지금은 <@{interaction.user.id}>님의 턴이 아닙니다.",
                    delete_after=5,
                    ephemeral=True,
                )


def setup(bot):
    bot.add_cog(DiceCog(bot))
