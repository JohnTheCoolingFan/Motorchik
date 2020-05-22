import discord
from discord.ext import commands
from guild_config import GuildConfig
import datetime


class XpLogCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild:
            guildconfig = GuildConfig(message.guild)
            guildconfig.process_message(message)

    @commands.Cog.listener()
    async def on_disconnect(self):
        with open('latest_connection.txt', 'w') as timestamp_file:
            timestamp_file.write(str(datetime.datetime.now().timestamp()))


def setup(bot: commands.Bot):
    bot.add_cog(XpLogCog(bot))
