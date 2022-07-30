import datetime
import json
import logging

import discord
from discord.commands import Option
from discord.ext import commands

from utils.embed import Embed
from utils.json_util import loadjson, savejson
from utils.respond import send_response


class marble_game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("kbyeworld")
        mydict = loadjson("./data/game.json")
        self.join = [member for dic in mydict for member in mydict[dic]["players"]]


def setup(bot):
    bot.add_cog(marble_game(bot))
