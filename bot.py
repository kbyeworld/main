import datetime
import logging
import os

import discord
from discord.ext import commands

import config


class kbyeworld(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = (True if "members" in config.setting.intents else False)
        intents.presences = (True if "presences" in config.setting.intents else False)
        intents.message_content = (True if "message_content" in config.setting.intents else False)
        super().__init__(
            command_prefix=(
                config.bot.prefix
            ),
            owner_ids=config.setting.owner_ids,
            help_command=None,
            intents=intents,
        )

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
        logger.info("✅ | Success to Load : Jishaku")
        cogs = [i.replace(".py", "") for i in os.listdir("./cogs") if i.endswith(".py")]
        cogs += [f"marble.{i.replace('.py', '')}" for i in os.listdir("./cogs/marble") if i.endswith(".py")]
        for i in cogs:
            try:
                self.load_extension(f"cogs.{i}")
                logger.info(f"✅ | Success to Load : cogs.{i}")
            except Exception as error:
                logger.error(f"❎ | Failed to Load : cogs.{i} (reason : {error})")


if __name__ == "__main__":
    kbyeworld().run(config.bot.token)