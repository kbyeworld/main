import datetime
import json
import logging

import discord

from utils.embed import Embed
from utils.json_util import loadjson, savejson
from utils.respond import send_response
from utils.pan import pan

async def marble_game(interaction, players):
    game_data = loadjson("./data/game.json")[
        (interaction.custom_id.replace("marble_", "").replace("_join", "")).replace(
            "_start", ""
        )
    ]
    province = loadjson(f"./data/game/{game_data['channel_id']}.json")
    game_thread = interaction.guild.get_thread(int(game_data["channel_id"]))
    players_data = {str(players[0]): {"color": "🟥", "money": "5000000", "eventCard": []}, str(players[1]): {"color": "🟩", "money": "5000000", "eventCard": []}}
    if len(players) == 3:
        players_data[str(players[2])] = {"color": "🟪", "money": "5000000", "eventCard": []}

    province["players_data"] = players_data

    pan_data = await pan(province, players_data)
    m = await game_thread.send("\n".join(pan_data))
    province["pan_msg"] = m.id

    savejson(f"./data/game/{game_data['channel_id']}.json", province)

    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            emoji="🎲",
            label="주사위 던지기",
            custom_id=f"dice_{players[0]}",
            style=discord.ButtonStyle.blurple,
        )
    )

    await game_thread.send(f"<@{players[0]}>님의 차례입니다.", view=view)
