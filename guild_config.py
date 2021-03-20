import pymongo
from enum import Enum
from discord.ext import commands
import discord
import json
import os.path
import asyncio
from typing import List, Iterable, Optional

def info_channels():
    return dict(log=dict(), welcome=dict())

GUILD_CONFIG_ENTRIES_TYPES = dict(commands=dict,
                                  default_roles=list,
                                  levels=dict,
                                  members=dict,
                                  name=str,
                                  info_channels=info_channels)


class CommandDisability(Enum):
    NONE = 0
    GLOBAL = 1
    BLACKLISTED = 2
    WHITELISTED = 3

class CommandDisabledException(discord.DiscordException):
    def __init__(self, guild: discord.Guild, command_name: str, channel: discord.TextChannel, disability: CommandDisability):
        self.guild = guild
        self.command_name = command_name
        self.channel = channel
        self.disability = disability

# TODO: updating data
class GuildConfig:
    guild: discord.Guild

    def __init__(self, guild: discord.Guild, guild_config_data: pymongo.cursor.Cursor):
        # The guild_config_data type is weird but that's what is being returned by pymongo's find_one() (probably).
        # But it can still be used as a dict, I think.
        self.guild = guild
        self.raw_data = guild_config_data

    @property
    def welcome_channel(self) -> Optional[discord.TextChannel]:
        if self.raw_data['info_channels']['welcome']['enabled']:
            return self.guild.get_channel(self.raw_data['info_channels']['welcome']['channel_id'])
        else:
            return None

    @welcome_channel.setter
    def welcome_channel(self, new_channel: discord.TextChannel):
        self.raw['info_channels']['welcome']['channel_id'] = new_channel.id

    @property
    def log_channel(self) -> Optional[discord.TextChannel]:
        if self.raw_data['info_channels']['log']['enabled']:
            return self.guild.get_channel(self.raw_data['info_channels']['log']['channel_id'])
        else:
            return None

    @log_channel.setter
    def log_channel(self, new_channel: discord.TextChannel):
        self.raw['info_channels']['log']['channel_id'] = new_channel.id

    @property
    def default_roles(self) -> List[discord.Role]:
        return [self.guild.get_role(role_id) for role_id in self.raw_data['default_roles']]

    @default_roles.setter
    def default_roles(self, new_roles: Iterable[discord.Role]):
        self.raw_data['default_roles'] = list({role.id for role in new_roles})

# May be reused somewhere
#    @classmethod
#    async def check(cls, bot: commands.Bot, guild: discord.Guild = None):
#        def check_for_entry(entry: str, guild_config_to_check: cls, entry_type):
#            if entry not in guild_config_to_check.raw:
#                guild_config_to_check.raw[entry] = entry_type()
#        if guild is None:
#            await asyncio.wait([cls.check(bot, _guild) for _guild in bot.guilds])
#        else:
#            if not os.path.exists('guilds/guild_{}.json'.format(guild.id)):
#                cls.create_guild_config(guild)
#            guild_config = cls(guild)
#            print('Checking config of guild ID:{}'.format(guild.id))
#            for entry_name in GUILD_CONFIG_ENTRIES_TYPES:
#                check_for_entry(entry_name, guild_config, GUILD_CONFIG_ENTRIES_TYPES[entry_name])
#            for command in bot.commands:
#                if command.name not in guild_config.raw['commands'].keys():
#                    print('Config for command "{0}" not found in config of guild ID:{1}'.format(command.name, guild_config.guild.id))
#                    guild_config.raw['commands'][command.name] = dict(whitelist=[], blacklist=[], enabled=True)
#            guild_config.write()

# Unimplemented for now
#    def add_xp(self, member: discord.Member, xp_count: int):
#        if str(member.id) not in self.raw['members']:
#            self.raw['members'][str(member.id)] = 0
#        self.raw['members'][str(member.id)] += xp_count
#        self.write()
#
#    def get_xp(self, member: discord.Member) -> int:
#        return self.raw['members'][str(member.id)]

# Don't work with command filters
#    def switch_command(self, command_name: str, new_state: bool) -> bool:
#        if command_name in self.commands_names:
#            self.raw['commands'][command_name]['enabled'] = new_state
#            self.write()
#            return True
#        else:
#            return False
#
#    def set_command_filter(self, command_name: str, filter_name: str, new_filter: Iterable[discord.TextChannel]) -> bool:
#        if command_name in self.commands_names:
#            self.raw['commands'][command_name][filter_name] = list({channel.id for channel in new_filter})
#            self.write()
#            return True
#        else:
#            return False

# TODO
#    def switch_info_channel(self, info_channel_type: str, new_state: bool) -> bool:
#        if info_channel_type in ['welcome', 'log']:
#            self.raw_data['info_channels'][info_channel_type]['enabled'] = new_state
#            self.write()
#            return True
#        else:
#            return False

class GuildConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.mongo_client = pymongo.MongoClient('localhost', 27017) # TODO with BotConfig
        self.bot = bot
        self.mongo_db = self.mongo_client['motorchik_guild_config']

    async def get_config(self, guild: discord.Guild) -> GuildConfig:
        guilds_collection = self.mongo_db.guilds
        guild_config_data = guilds_collection.find_one({"guild_id": guild.id})
        return GuildConfig(guild, guild_config_data)

    async def add_guild(self, guild: discord.Guild):
        default_channel = guild.system_channel.id if guild.system_channel is not None else guild.text_channels[0].id
        # New entries may be added in the future.
        guild_config_data = {
            "guild_id": guild.id,
            "guild_name": guild.name, # For debugging purposes.
            "default_roles": [], # Empty list by default
            "info_channels": { # Names are hardcoded but there is some clearance for expanding Info Channels functionality
                "welcome": {
                    "channel_id": default_channel, # Use default system channel or the first text channel
                    "enabled": False # Disabled by default
                },
                "log": {
                    "channel_id": default_channel, # Same as with 'welcome' info channel
                    "enabled": False # Disabled by default
                }
            },
            "command_filters": [] # Empty list that will be filled when setting up
        }
        guilds_collection = self.mongo_db.guilds
        guilds_collection.insert_one(guild_config_data)

class MotorchikBot(commands.Bot):
    async def guild_config(self, guild: discord.Guild) -> GuildConfig:
        return await self.get_cog('GuildConfigCog').get_config(guild)
