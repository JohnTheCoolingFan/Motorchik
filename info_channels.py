from typing import Union

import discord
from discord.ext import commands


class InfoChannels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        print('Loading InfoChannels module...', end='')
        self.bot = bot
        self.guild_config_cog = bot.get_cog('GuildConfigCog')
        print(' Done')

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: Union[discord.User, discord.Member]):
        guild_config = await self.guild_config_cog.get_guild(guild)
        log_channel = await guild_config.get_log_channel()
        if log_channel:
            await log_channel.send('{} was banned'.format(str(user)))

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        guild_config = await self.guild_config_cog.get_guild(guild)
        log_channel = await guild_config.get_log_channel()
        if log_channel:
            await log_channel.send('{} was unbanned'.format(str(user)))

def setup(bot: commands.Bot):
    bot.add_cog(InfoChannels(bot))
