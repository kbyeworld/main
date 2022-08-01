import discord


async def send_response(interaction, content, embed=None, **kwargs):
    try:
        return await interaction.response.send_message(content=content, embed=embed, **kwargs)
    except discord.InteractionResponded:
        return await interaction.followup.send(content=content, embed=embed, **kwargs)
    except discord.errors.HTTPException:
        return await interaction.followup.send(content=content, embed=embed, **kwargs)
