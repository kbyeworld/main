import json

import discord

from utils.custom_except import AlreadyJoined, UnknownGame
from utils.json_util import loadjson, savejson


def is_already_join(interaction: discord.Interaction) -> bool:
    mydict = loadjson("./data/game.json")
    join = [member for dic in mydict for member in dic["players"]]

    if not interaction.type == discord.InteractionType.component:
        return True
    if interaction.type == discord.InteractionType.application_command:
        print(interaction.message.content)
    try:
        if mydict[str(interaction.user.id)] or interaction.user.id in join:
            raise AlreadyJoined("이미 게임을 생성하였거나 참여중입니다.")
    except KeyError:
        raise UnknownGame("존재하지 않는 게임이에요.")
    return True
