from discord.ext import commands
import guild_config

class Levels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(Levels(bot))