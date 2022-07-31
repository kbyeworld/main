import discord
from discord.ext import commands
import random
from utils.respond import send_response
from utils.json_util import loadjson, savejson


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
                print(game_data)
                print(game_data['province'])
                for d in game_data['province']:
                    if interaction.user.id in d['users']:
                        if (user_loc_num + int(con)) >= len(game_data['province']):
                            user_now_loc_num = (user_loc_num + int(con)) - len(game_data['province'])
                        else:
                            user_now_loc_num = (user_loc_num + int(con))
                        print(game_data['province'][user_now_loc_num]['name'])
                        user_new_loc = game_data['province'][user_now_loc_num]['name']
                        user_pre_loc_num = user_loc_num
                        # print((list(game_data['province']).index(d['name'])) + int(con))
                        # print(game_data['province'][(list(game_data['province']).index(d['name'])) + int(con)])
                    user_loc_num += 1
                await send_response(interaction,
                        f"<@{interaction.user.id}>님의 주사위는 {con}입니다! 현재 위치는 {user_new_loc}입니다.")

                # 주사위 후 말 이동(json 파일 변경 우선)
                print("말 이동")
                data = loadjson(f"./data/game/{interaction.channel_id}.json")
                province = data['province']
                print(user_loc_num)
                # print(province[user_now_loc_num]['users'])
                province[user_pre_loc_num]['users'].remove(interaction.user.id)
                province[user_now_loc_num]['users'].append(interaction.user.id)
                savejson(f"./data/game/{interaction.channel_id}.json", data)

                mydict = loadjson("./data/game.json")[game_data["game_owner"]]["players"]
                print(interaction.custom_id)
                this_turn = list(mydict).index(interaction.user.id)
                print(this_turn)
                print(mydict)
                print(len(mydict))
                if this_turn == (len(mydict) - 1):
                    next_turn = mydict[0]
                else:
                    next_turn = mydict[(list(mydict).index(interaction.user.id)) + 1]
                print(next_turn)
                view = discord.ui.View()
                view.add_item(
                    discord.ui.Button(emoji="🎲", label="주사위 던지기", custom_id=f"dice_{next_turn}", style=discord.ButtonStyle.blurple))
                await (await interaction.channel.fetch_message(int(interaction.message.id))).edit(content=f"<@{next_turn}>님의 차례입니다.", view=view)

            else:
                await send_response(interaction,
                    f"지금은 <@{interaction.user.id}>님의 턴이 아닙니다.", delete_after=5, ephemeral=True)


def setup(bot):
    bot.add_cog(DiceCog(bot))
