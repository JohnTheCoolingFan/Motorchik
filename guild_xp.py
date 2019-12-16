import discord
from discord.ext import commands
from guild_config import GuildConfig

class GuildXp(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild and message.guild.id == 370167294439063564:
            guildconfig = GuildConfig(message.guild)
            guildconfig.process_message(message)

def setup(bot: commands.Bot):
    bot.add_cog(GuildXp(bot))
