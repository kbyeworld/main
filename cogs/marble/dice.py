import discord
from discord.ext import commands
import random
from utils.respond import send_response

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.custom_id.startswith("dice_"):
            await interaction.defer(ephemeral=True)

            await send_response(interaction, f"<@{interaction.custom_id.replace('dice_', '')}>{str(random.randint(1, 6)})

def setup(bot):
    bot.add_cog(DiceCog(bot)