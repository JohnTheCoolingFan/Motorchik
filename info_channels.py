from discord.ext import commands
import discord
from typing import Union
from guild_config import GuildConfig

class InfoChannels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: Union[discord.User, discord.Member]):
        guild_config = GuildConfig(guild)
        if guild_config.log_channel:
            await guild_config.log_channel.send('{} was banned'.format(str(user)))

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        guild_config = GuildConfig(guild)
        if guild_config.log_channel:
            await guild_config.log_channel.send('{} was unbanned'.format(str(user)))

def setup(bot: commands.Bot):
    bot.add_cog(InfoChannels(bot))
