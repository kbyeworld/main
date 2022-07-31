import datetime
import logging
import os

import discord
from discord.ext import commands

import config
from utils.json_util import savejson


class kByeWorld(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True if "members" in config.Setting.intents else False
        intents.presences = True if "presences" in config.Setting.intents else False
        intents.message_content = (
            True if "message_content" in config.Setting.intents else False
        )
        super().__init__(
            command_prefix=config.Bot.prefix,
            owner_ids=config.Setting.owner_ids,
            intents=intents,
        )

        if os.path.isdir("./logs") is False:
            os.mkdir("./logs")

        logger = logging.getLogger("kbyeworld")
        logger.setLevel(logging.INFO)
        stream = logging.StreamHandler()
        time = datetime.datetime.now().strftime("%Y%m%d%H%M")
        handler = logging.FileHandler(
            filename=f"logs/{time}.log",
            encoding="utf-8",
            mode="w",
        )
        formatter = logging.Formatter("[%(levelname)s] (%(asctime)s) : %(message)s")
        stream.setFormatter(formatter)
        handler.setFormatter(formatter)
        logger.addHandler(stream)
        logger.addHandler(handler)

        logger.info("📋 | Loading Modules...")
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"

        self.load_extension("jishaku")

        if os.path.isfile("./data/game.json") is False:
            savejson("./data/game.json", {})
            logger.info("🛒 | Add GameData File")

        if os.path.isdir("./data/game") is False:
            os.mkdir("./data/game")
            logger.info("🛒 | Add GameData Folder")

        files = [
                    f"cogs.{item[:-3]}"
                    for item in os.listdir(f"./cogs/")
                    if os.path.isfile(f"./cogs/{item}")
                    if item.endswith(".py")
                ] + [
                    f"cogs.{i}.{item[:-3]}"
                    for i in os.listdir("./cogs/")
                    if os.path.isdir(f"./cogs/{i}")
                    for item in os.listdir(f"./cogs/{i}")
                    if item.endswith(".py")
                ]
        for file in files:
            try:
                self.load_extension(file)
                logger.info(f"✅ | Success to Load : {file}")
            except Exception as error:
                logger.error(f"❎ | Failed to Load : {file} (reason : {error})")


if __name__ == "__main__":
    kByeWorld().run(config.Bot.token)
