import discord
from discord.ext import commands
import random
from utils.respond import send_response


class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.is_component() and interaction.custom_id.startswith("dice_"):
            await send_response(interaction,
                f"<@{interaction.user.id}>님의 주사위는 {str(random.randint(1, 6))}입니다!", delete_after=5)


def setup(bot):
    bot.add_cog(DiceCog(bot))
