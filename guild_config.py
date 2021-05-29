import sys
import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Optional, Tuple

import discord
from discord.ext import commands

IMMUTABLE_COMMANDS = ['command', 'config', 'say', 'say_dm']
INFO_CHANNEL_TYPES = ['welcome', 'log'] # reports and mod-list are not yet implemented

# TODO: Module that stores data in separate channel in the discord guild itself.


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
@dataclass(frozen=True)
class CommandFilter:
    name: str
    filter_type: CommandDisability
    filter_list: List[discord.TextChannel]
    enabled: bool
    guild: discord.Guild

# TypedDict is not available in Python 3.7
# class InfoChannelSpec(TypedDict):
    # channel: discord.TextChannel = None
    # enabled: bool = None

def default_guild_config_data(guild: discord.Guild):
    default_channel = guild.system_channel.id if guild.system_channel is not None else guild.text_channels[0].ids
    guild_config_data = {
        "guild_name": guild.name,
        "default_roles": [],
        "info_channels": {
            "welcome": {
                "channel_id": default_channel,
                "enabled": False
            },
            "log": {
                "channel_id": default_channel,
                "enabled": False
            }
        }
    }
    return guild_config_data

# Updates DB info by itself, can be easily cached
class GuildConfig:
    guild: discord.Guild

    def __init__(self, guild: discord.Guild, guild_config_data: dict, guild_config_cog):
        # guild_config_data type is assumed to be dict but not always is.
        self.guild = guild
        self.raw_data = guild_config_data
        self.guild_config_cog = guild_config_cog

    # Update info channel's specs.
    async def update_info_channel(self, ic_name: str, state: Optional[bool] = None, new_channel: Optional[discord.TextChannel] = None):
        if ic_name in INFO_CHANNEL_TYPES:
            update_data = {}
            if state is not None:
                update_data['enabled'] = state
            if new_channel is not None:
                update_data['channel'] = new_channel
            if update_data != {}:
                new_data = await self.guild_config_cog.update_guild(self.guild, info_channels={ic_name: update_data})
                if new_data is not None:
                    self.raw_data = new_data
        else:
            raise InfoChannelNotFoundError(ic_name)

    # Get discord.TextChannel for welcome channel
    async def get_welcome_channel(self) -> Optional[discord.TextChannel]:
        if self.raw_data['info_channels']['welcome']['enabled']:
            return self.guild.get_channel(self.raw_data['info_channels']['welcome']['channel_id'])
        else:
            return None

    # Set the welcome channel
    async def set_welcome_channel(self, new_channel: discord.TextChannel):
        await self.update_info_channel('welcome', new_channel=new_channel)

    # Enable welcome channel
    async def enable_welcome_channel(self):
        await self.update_info_channel('welcome', state=True)

    # Disable welcome channel
    async def disable_welcome_channel(self):
        await self.update_info_channel('welcome', state=False)

    # Below all the same for log channel

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

    # Get default roles. Return empty list if no roles were set
    async def get_default_roles(self) -> List[discord.Role]:
        return [self.guild.get_role(role_id) for role_id in self.raw_data['default_roles']]

    # Set default roles. Passing an empty iterable results in removing all default roles.
    async def set_default_roles(self, new_roles: Iterable[discord.Role]):
        new_data = await self.guild_config_cog.update_guild(self.guild, default_roles=new_roles)
        if new_data is not None:
            self.raw_data = new_data

   # Unimplemented
   # def add_xp(self, member: discord.Member, xp_count: int):
       # if str(member.id) not in self.raw['members']:
           # self.raw['members'][str(member.id)] = 0
       # self.raw['members'][str(member.id)] += xp_count
       # self.write()

   # def get_xp(self, member: discord.Member) -> int:
       # return self.raw['members'][str(member.id)]

# Abstract base class for all GuildConfigCog modules. Defines some methods that need to be overriden and adds some checks.
class AbstractGuildConfigCog(commands.Cog):
    __gc_cache: Dict[int, GuildConfig]               = dict() # Guild ID is key, GuildConfig is the item
    __cf_cache: Dict[Tuple[int, str], CommandFilter] = dict() # Tuple of Guild ID and command name is key, CommandFilter is the item

    bot: commands.Bot
    name = 'GuildConfigCog' # Should not be changed!
    gc_type: str = '' # Define the Cog type. FOr example: 'mongo', 'json'

    # CommandFilter check
    # Suggestion: remove "enabled" property and use CommandDisability.GLOBAL insted.
    async def bot_check_once(self, ctx: commands.Context):
        # Don't bother to check the command filter if command can't be filtered
        if ctx.command.name in IMMUTABLE_COMMANDS:
            return True
        else:
            command_filter = await self.get_command_filter(ctx.guild, ctx.command.name)
            # Command filter isn't set up, so it's allowed to run
            if command_filter is None:
                return True
            else:
                # If command is disabled on the server (guild) globally, it's not allowed to run
                if not command_filter.enabled:
                    raise CommandDisabledError(ctx.guild, ctx.command.name, ctx.channel, CommandDisability.GLOBAL)
                # If command was called in a blacklisted channel, it's not allowed to run
                if command_filter.filter_type == CommandDisability.BLACKLISTED and ctx.channel in command_filter.filter_list:
                    raise CommandDisabledError(ctx.guild, ctx.command.name, ctx.channel, command_filter.filter_type)
                # If command wasn't called in a whitelisted channel, it's not allowed to run
                if command_filter.filter_type == CommandDisability.WHITELISTED and ctx.channel not in command_filter.filter_list:
                    raise CommandDisabledError(ctx.guild, ctx.command.name, ctx.channel, command_filter.filter_type)
                # Default
                return True

    # Handle CommandDisableError
    @commands.Cog.listener()
    async def on_command_error(self, ctx:commands.Context, exc: commands.errors.CommandError):
        # For now, just ignore if command is disabled
        # TODO: message for when command is disabled
        # TODO: settingg in GuildConfig if these messages should be displayed
        if isinstance(exc, CommandDisabledError):
            return
        else:
            # The default behaviour. I fell like there is a better way to do this. It was copied from discord.py source
            print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)

    # I have a feeling that this is unnecessary
    def teardown(self):
        self.__gc_cache.clear()
        self.__cf_cache.clear()

    # Get GuildConfig for given Guild.
    # Decide wheter next this one or the next is correct
    async def get_config(self, guild: discord.Guild) -> GuildConfig:
        pass

    async def get_guild(self, guild: discord.Guild) -> GuildConfig:
        return await self.get_config(guild)

    # Update GuildConfig in the DB
    async def update_guild(self,
                           guild: discord.Guild,
                           default_roles: List[discord.Role] = None,
                           info_channels: Dict[str, dict] = None) -> dict:
        pass

    # Add a new GuildConfig to the DB
    async def add_guild(self, guild: discord.Guild):
        pass

    # Get a CommandFilter from the DB
    async def get_command_filter(self, guild: discord.Guild, name: str) -> CommandFilter:
        pass

    # Update CommandFilter in the DB
    async def update_command_filter(self,
                                    guild: discord.Guild,
                                    name: str,
                                    new_channels: List[discord.TextChannel] = None,
                                    append_channels: bool = False,
                                    enabled: bool = None,
                                    filter_type: CommandDisability = None) -> dict:
        pass
