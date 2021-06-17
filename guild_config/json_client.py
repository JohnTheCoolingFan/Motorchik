"""
GuildConfigCog to store GuildConfig data on disk in JSON files
"""

import json
import os
import os.path as p
import sys
from typing import Dict, List, Optional, Tuple

import discord
from discord.ext import commands

from guild_config.guild_config import (
    AbstractGuildConfigCog,
    CommandDisability,
    CommandFilter,
    CommandImmutableError,
    CommandNotFoundError,
    GuildConfig,
    IMMUTABLE_COMMANDS,
    INFO_CHANNEL_TYPES,
    default_guild_config_data,
)


class GuildConfigCog(AbstractGuildConfigCog):
    bot: commands.Bot
    __gc_cache: Dict[int, GuildConfig]               = dict() # Guild ID is key, GuildConfig is the item
    __cf_cache: Dict[Tuple[int, str], CommandFilter] = dict() # Tuple of Guild ID and command name is key, CommandFilter is the item

    def __init__(self, bot: commands.Bot):
        print('Loading JSON GuildConfig module...', end='')
        self.bot = bot
        bot_config = bot.get_cog('BotConfig')

        # Read config storage path from config.json, parsed by BotConfig cog
        self.path = bot_config.json['dir']
        if self.path[-1] != '/':
            self.path = self.path + '/'

        # Some assitional checks for the validity of the path
        if not p.isdir(self.path):
            print('Error: {} is not a directory'.format(self.path), file=sys.stderr)
            sys.exit(1)
        if not p.exists(self.path):
            os.mkdir(self.path)

        # Add the prefix beforehand
        self.path = self.path + 'guild_'
        print(' Done')

    def dump_json(self, data: dict, guild: discord.Guild):
        filename = self.path + str(guild.id) + '.json'
        with open(filename, 'w') as guild_config_file:
            json.dump(data, guild_config_file,
                      indent=4, sort_keys=True) # Easy way to change saving settings in one place
        os.chmod(filename, 0o666)

    def load_json(self, guild: discord.Guild) -> Optional[dict]:
        filename = self.path + str(guild.id) + '.json'
        if p.exists(filename):
            with open(filename) as guild_config_file:
                guild_config_data = json.load(guild_config_file)
            return guild_config_data
        else:
            return None

    async def get_guild_config_data(self, guild: discord.Guild) -> dict:
        guild_config_data = self.load_json(guild)
        if guild_config_data is None:
            guild_config_data = await self.add_guild(guild)
        return guild_config_data

    async def get_config(self, guild: discord.Guild) -> GuildConfig:
        if guild.id in self.__gc_cache:
            return self.__gc_cache[guild.id]
        else:
            filename = self.path + str(guild.id) + '.json'
            if not p.exists(filename):
                await self.add_guild(guild)
            guild_config_data = await self.get_guild_config_data(guild)
            guild_config = GuildConfig(guild, guild_config_data, self)
            self.__gc_cache[guild.id] = guild_config
            return guild_config

    async def update_guild(self, guild: discord.Guild,
                           default_roles: List[discord.Role] = None,
                           info_channels: Dict[str, dict] = None) -> Optional[dict]:
        guild_config_data = await self.get_guild_config_data(guild)

        if default_roles is not None:
            guild_config_data['default_roles'] = [role.id for role in default_roles]
        if info_channels is not None:
            for ic_name, ic_spec in info_channels.items():
                if ic_name in INFO_CHANNEL_TYPES:
                    if 'channel' in ic_spec and ic_spec['channel'] is not None:
                        guild_config_data['info_channels'][ic_name]['channel_id'] = ic_spec['channel'].id
                    if 'enabled'in ic_spec and ic_spec['enabled'] is not None:
                        guild_config_data['info_channels'][ic_name]['enabled'] = ic_spec['enabled']

        self.dump_json(guild_config_data, guild)
        return guild_config_data

    async def add_guild(self, guild: discord.Guild) -> dict:
        guild_config_data = default_guild_config_data(guild)
        guild_config_data['command_filters'] = dict()
        self.dump_json(guild_config_data, guild)
        return guild_config_data

    # return some generic empty filter by default? Or processing None is just simplier?
    async def get_command_filter(self, guild: discord.Guild, name: str) -> Optional[CommandFilter]:
        if (guild.id, name) in self.__cf_cache:
            return self.__cf_cache[(guild.id, name)]
        else:
            guild_config_data = await self.get_guild_config_data(guild)

            if name in guild_config_data['command_filters']:
                command_filter_data = guild_config_data['command_filters'][name]
                # Maybe update the command filter data if it contains deleted channels?
                # But they will be removed anyway when filter is updated
                # But while filter is not updated, they will take space and bandwidth!
                # And updating the command filter will also use bandwidth and/or cpu time
                command_filter_channels = []
                for channel_id in command_filter_data['channels']:
                    channel = self.bot.get_channel(channel_id)
                    if channel is not None:
                        command_filter_channels.append(channel)
                command_filter =  CommandFilter(name,
                                                CommandDisability(command_filter_data['type']),
                                                # Pyright was whyning about Unknown | None, so I amde a check earlier
                                                #[self.bot.get_channel(channel_id) for channel_id in command_filter_data['channels']],
                                                command_filter_channels,
                                                command_filter_data['enabled'],
                                                guild)
                self.__cf_cache[(guild.id, name)] = command_filter
                return command_filter
            else:
                return None

    async def update_command_filter(self, guild: discord.Guild,
                                    name: str,
                                    new_channels: List[discord.TextChannel] = None,
                                    append_channels: bool = False,
                                    enabled: bool = None,
                                    filter_type: CommandDisability = None):
        if new_channels is None and enabled is None and filter_type is None:
            return
        if name in IMMUTABLE_COMMANDS:
            raise CommandImmutableError(name)
        if name not in [command.name for command in self.bot.commands]:
            raise CommandNotFoundError(name)

        guild_config_data = await self.get_guild_config_data(guild)

        if name not in guild_config_data['command_filters']:
            guild_config_data['command_filters'][name] = {"type": 2, "channels": [], "enabled": True}
        command_filter_data = guild_config_data['command_filters'][name]
        if new_channels is not None:
            if append_channels and new_channels:
                command_filter_data['channels'].append([channel.id for channel in new_channels])
            else:
                command_filter_data['channels'] = [channel.id for channel in new_channels]
        if enabled is not None:
            command_filter_data['enabled'] = enabled
        if filter_type is not None and filter_type.value >= 2:
            command_filter_data['type'] = filter_type.value

        guild_config_data['command_filters'][name] = command_filter_data
        self.dump_json(guild_config_data, guild)
        if (guild.id, name) in self.__cf_cache:
            del self.__cf_cache[(guild.id, name)]

def setup(bot: commands.Bot):
    bot.add_cog(GuildConfigCog(bot))
