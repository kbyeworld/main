import discord

async def is_text_channel(ctx):
    if ctx.channel.type == discord.ChannelType.text:
        return True
    else:
        await ctx.respond("이 명령어는 일반 텍스트 채널에서만 명령어 사용이 가능합니다.", ephemeral=True)
        return False
