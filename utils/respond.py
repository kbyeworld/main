import discord

async def send_response(interaction, content, embed=None, **kwargs):
    try:
        await interaction.response.send_message(content=content, embed=embed, **kwargs)
    except discord.InteractionResponded:
        await interaction.followup.send(content=content, embed=embed, **kwargs)