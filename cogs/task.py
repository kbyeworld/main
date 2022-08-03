import datetime
import logging
import random

import aiohttp
import discord
from discord.ext import commands, tasks

import config
from utils.database import *
from utils.embed import Embed


class Task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("kbyeworld")
        self.update_stats.start()

    def cog_unload(self):
        try:
            self.update_stats.stop()
        except:
            pass

    @tasks.loop(hours=1)
    async def update_stats(self):
        await self.bot.wait_until_ready()
        session = aiohttp.ClientSession()
        if config.Setting.social.koreanbots:
            try:
                async with session.post(
                    f"https://koreanbots.dev/api/v2/bots/{self.bot.user.id}/stats",
                    data={
                        "servers": len(self.bot.guilds),
                        "shards": len(self.bot.shards),
                    },
                    headers={"Authorization": config.Setting.social.koreanbots},
                ) as res:
                    if res.status != 200:
                        self.logger.error(
                            f"❌ 한디리 서버수 업데이트 실패 ({(await res.json())['message']})"
                        )
                    else:
                        self.logger.info(
                            f"✅ 한디리 서버수 업데이트 성공 ({(await res.json())['message']})"
                        )
            except Exception as error:
                self.logger.error(f"❌ 한디리 서버수 업데이트 중 오류 발생 ({error})")
        await session.close()

def setup(bot):
    bot.add_cog(Task(bot))