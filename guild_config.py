from enum import Enum
from typing import Iterable, List, Optional

import discord
from discord.ext import commands


IMMUTABLE_COMMANDS = ['command', 'config', 'say', 'say_dm']

# TODO: make GuildConfig imdependent from mongodb, just use Cog's methods.
# TODO: make Interface class (abstract class) for GuildConfigCog


# Enums
class CommandDisability(Enum):
    NONE = 0
    GLOBAL = 1
    BLACKLISTED = 2
    WHITELISTED = 3

# Errors/Exceptions
class GuildConfigError(commands.errors.CommandError):
    pass

class InfoChannelNotFoundError(GuildConfigError):
    def __init__(self, ic_name: str):
        self.ic_name = ic_name

class CommandDisabledError(GuildConfigError):
    def __init__(self, guild: discord.Guild, command_name: str, channel: discord.TextChannel, disability: CommandDisability):
        self.guild = guild
        self.command_name = command_name
        self.channel = channel
        self.disability = disability

# Raised if bot doesn't have this command
class CommandNotFoundError(GuildConfigError):
    def __init__(self, name: str):
        self.name = name

# Raised if command can't be filtered
class CommandImmutableError(GuildConfigError):
    def __init__(self, name: str):
        self.name = name

# Data structures
class CommandFilter:
    name: str
    filter_type: CommandDisability
    filter_list: List[discord.TextChannel]
    enabled: bool
    guild: discord.Guild

    def __init__(self, name: str, filter_type: CommandDisability, filter_list: List[discord.TextChannel], enabled: bool, guild: discord.Guild):
        self.name = name
        self.filter_type = filter_type
        self.filter_list = filter_list
        self.enabled = enabled
        self.guild = guild

# Updates DB info by itself, can be easily cached
class GuildConfig:
    guild: discord.Guild

    def __init__(self, guild: discord.Guild, guild_config_data, guilds_collections):
        # The guild_config_data type is weird but that's what is being returned by pymongo's find_one() (probably).
        # But it can still be used as a dict, I think.
        self.guild = guild
        self.raw_data = guild_config_data
        self.guilds_collections = guilds_collections

    async def update_info_channel(self, ic_name: str, state: Optional[bool] = None, new_channel: Optional[discord.TextChannel] = None):
        if state is None and new_channel is None:
            return
        if ic_name in ['log', 'welcome']:
            if state is not None:
                new_data = await self.guilds_collections.find_one_and_update({'_id': self.raw_data['_id']}, {'$set': {'info_channels.{}.enabled'.format(ic_name): state}}, return_document=True)
            if new_channel is not None:
                new_data = await self.guilds_collections.find_one_and_update({'_id': self.raw_data['_id']}, {'$set': {'info_channels.{}.channel_id'.format(ic_name): new_channel.id}}, return_document=True)
            self.raw_data = new_data
        else:
            raise InfoChannelNotFoundError(ic_name)

    async def get_welcome_channel(self) -> Optional[discord.TextChannel]:
        if self.raw_data['info_channels']['welcome']['enabled']:
            return self.guild.get_channel(self.raw_data['info_channels']['welcome']['channel_id'])
        else:
            return None

    async def set_welcome_channel(self, new_channel: discord.TextChannel):
        await self.update_info_channel('welcome', new_channel=new_channel)

    async def enable_welcome_channel(self):
        await self.update_info_channel('welcome', state=True)

    async def disable_welcome_channel(self):
        await self.update_info_channel('welcome', state=False)

    async def get_log_channel(self) -> Optional[discord.TextChannel]:
        if self.raw_data['info_channels']['log']['enabled']:
            return self.guild.get_channel(self.raw_data['info_channels']['log']['channel_id'])
        else:
            return None

    async def set_log_channel(self, new_channel: discord.TextChannel):
        await self.update_info_channel('log', new_channel=new_channel)

    async def enable_log_channel(self):
        await self.update_info_channel('log', state=True)

    async def disable_log_channel(self):
        await self.update_info_channel('log', state=False)

    async def get_default_roles(self) -> List[discord.Role]:
        return [self.guild.get_role(role_id) for role_id in self.raw_data['default_roles']]

    async def set_default_roles(self, new_roles: Iterable[discord.Role]):
        new_roles = [role.id for role in new_roles]
        new_data = await self.guilds_collections.find_one_and_update({'_id': self.raw_data['_id']}, {'$set': {'default_roles': new_roles}})
        self.raw_data = new_data

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
