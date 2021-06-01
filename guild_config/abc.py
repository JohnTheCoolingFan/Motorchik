"""
Abstract Base Classes
"""

import abc
import sys
import traceback
from typing import Any, Dict, List, Tuple

import discord
from discord.ext import commands

from guild_config.guild_config import (
    CommandDisability,
    CommandDisabledError,
    CommandFilter,
    GuildConfig,
    IMMUTABLE_COMMANDS,
)

class CogABCMeta(commands.CogMeta, abc.ABCMeta):
    pass

class GuildConfigABC(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def __gc_cache(self) -> Dict[int, GuildConfig]:
        pass

    @property
    @abc.abstractmethod
    def __cf_cache(self) -> Dict[Tuple[int, str], CommandFilter]:
        pass

    @property
    @abc.abstractmethod
    def bot(self) -> commands.Bot:
        pass

    name = 'GuildConfigCog'

    # CommandFilter check
    # Suggestion: remove "enabled" property and use CommandDisability.GLOBAL insted.
    async def bot_check_once(self, ctx: commands.Context):
        if ctx.guild is not None and ctx.channel is not None:
            # Don't bother to check the command filter if command can't be filtered
            if ctx.command.name in IMMUTABLE_COMMANDS:
                return True
            else:
                command_filter = await self.get_command_filter(ctx.guild, ctx.command.name)  # type: ignore
                # Command filter isn't set up, so it's allowed to run
                if command_filter is None:
                    return True
                else:
                    # If command is disabled on the server (guild) globally, it's not allowed to run
                    if not command_filter.enabled:
                        raise CommandDisabledError(ctx.guild, ctx.command.name, ctx.channel, CommandDisability.GLOBAL)  # type: ignore
                    # If command was called in a blacklisted channel, it's not allowed to run
                    if command_filter.filter_type == CommandDisability.BLACKLISTED and ctx.channel in command_filter.filter_list:
                        raise CommandDisabledError(ctx.guild, ctx.command.name, ctx.channel, command_filter.filter_type)  # type: ignore
                    # If command wasn't called in a whitelisted channel, it's not allowed to run
                    if command_filter.filter_type == CommandDisability.WHITELISTED and ctx.channel not in command_filter.filter_list:
                        raise CommandDisabledError(ctx.guild, ctx.command.name, ctx.channel, command_filter.filter_type)  # type: ignore
                    # Default
                    return True

    # Handle CommandDisableError
    @commands.Cog.listener()
    async def on_command_error(self, ctx:commands.Context, exc: commands.errors.CommandError):
        # For now, just ignore if command is disabled
        # TODO: message for when command is disabled
        #       send the message in DM, also would need an opt-out system, so UserConfig will probably need to be brought back...
        if isinstance(exc, CommandDisabledError):
            return
        else:
            # The default behaviour. I fell like there is a better way to do this. It was copied from discord.py source
            print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)

    @abc.abstractmethod
    async def get_config(self, guild: discord.Guild) -> GuildConfig:
        pass

    async def get_guild(self, guild: discord.Guild) -> GuildConfig:
        return await self.get_config(guild)

    @abc.abstractmethod
    async def update_guild(self, guild: discord.Guild,
                           default_roles: List[discord.Role] = None,
                           info_channels: Dict[str, dict] = None) -> dict:
        pass

    @abc.abstractmethod
    async def add_guild(self, guild: discord.Guild) -> Any:
        pass

    @abc.abstractmethod
    async def get_command_filter(self, guild: discord.Guild, name: str) -> CommandFilter:
        pass

    @abc.abstractmethod
    async def update_command_filter(self, guild: discord.Guild,
                                    name: str,
                                    new_channels: List[discord.TextChannel] = None,
                                    append_channels: bool = False,
                                    enabled: bool = None,
                                    filter_type: CommandDisability = None) -> dict:
        pass
