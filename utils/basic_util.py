import os.path

import discord


async def is_text_channel(ctx):
    if ctx.channel.type == discord.ChannelType.text:
        return True
    else:
        await ctx.respond("이 명령어는 일반 텍스트 채널에서만 사용이 가능합니다.", ephemeral=True)
        return False


async def is_thread(ctx):
    print(ctx.channel.type)
    if ctx.channel.type == discord.ChannelType.public_thread:
        if ctx.channel.name.endswith("마블게임방") and os.path.isfile(f"./data/game/{ctx.channel.id}.json"):
            return True
    else:
        await ctx.respond("이 명령어는 게임이 진행중인 스레드에서만 사용이 가능합니다.", ephemeral=True)
        return False
