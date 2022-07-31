import discord
import datetime
import json
import logging

from utils.embed import Embed
from utils.json_util import loadjson, savejson
from utils.respond import send_response


async def marble_game(interaction, players):
    game_data = loadjson('./data/game.json')[
        (interaction.custom_id.replace("marble_", "").replace("_join", "")).replace("_start", "")]
    province = loadjson(f"./data/game/{game_data['channel_id']}.json")
    #province = loadjson(f"./data/province.json")
    game_thread = interaction.guild.get_thread(int(game_data["channel_id"]))
    player_1, player_1_color = players[0], "🟥"
    player_2, player_2_color = players[1], "🟩"
    if len(players) == 3:
        player_3, player_3_color = players[2], "🟪"
    else:
        player_3, player_3_color = None, None
    pan_data = []
    for data in province['province']:
        if data['name'] == "시작":
            pan_data.append(f"[{player_1_color}, {player_2_color}{f', {player_3_color}' if player_3 else ''}] {data['name']}")
        elif data['name'] == "이벤트 카드":
            pan_data.append(f"[⬜️] 💳 {data['name']}")
        elif data['name'] == "여행":
            pan_data.append(f"[⬜️] 🧳 {data['name']}")
        elif data['name'] == "감옥":
            pan_data.append(f"[⬜️] 🔒 {data['name']}")
        else:
            pan_data.append(f"[⬜️] 🏙️ {data['name']} (소유주 없음, {data['money']})")
    await game_thread.send('\n'.join(pan_data))

    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(emoji="🎲", label="주사위 던지기", custom_id=f"dice_{player_1}", style=discord.ButtonStyle.blurple))

    await game_thread.send(embed=Embed.default("주사위 던지기"), view=view)
