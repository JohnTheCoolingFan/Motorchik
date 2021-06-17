"""
Module that stores GuildConfig data in MongoDB
"""

from typing import Dict, List, Optional, Tuple

import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo

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
    __gc_cache: Dict[int, GuildConfig]               = dict() # Guild ID is key, GuildConfig is the item
    __cf_cache: Dict[Tuple[int, str], CommandFilter] = dict() # Tuple of Guild ID and command name is key, CommandFilter is the item

    def __init__(self, bot: commands.Bot):
        print('Loading MongoDB GuildConfig module...', end='')
        # Bot
        self.bot = bot
        bot_config = bot.get_cog('BotConfig')

        # Mongo setup
        self.mongo_client = AsyncIOMotorClient(host = bot_config.mongo['host'],
                                               port=bot_config.mongo['port'],
                                               username=bot_config.mongo['username'],
                                               password=bot_config.mongo['password'],
                                               io_loop=bot.loop,
                                               authSource='motorchik_guild_config',
                                               connect=True
                                               )
        self.mongo_db = self.mongo_client['motorchik_guild_config']

        # Collections
        self.guilds_collection = self.mongo_db.guilds
        self.cf_collection = self.mongo_db.command_filters

        # Cache
        # Done in parent class.
        #self.__gc_cache = dict() # keys are ints representing guild ids
        #self.__cf_cache = dict() # keys are tuples, consisting of: 1. guild id 2. command name
        print(' Done')

    # This could be a command...
    async def create_indexes(self):
        # Create indexes
        # I'm not sure what indexing method to use for guild ids, but for now let it be ascending...
        # I'm not even sure if I really need to index guild ids
        # This is currently unused
        await self.cf_collection.create_index([('guild_id', pymongo.ASCENDING), ('name', pymongo.TEXT)])
        await self.guilds_collection.create_index([('guild_id', pymongo.ASCENDING)])

    def teardown(self):
        self.__gc_cache.clear()
        self.__cf_cache.clear()
        self.mongo_client.close()
        self.bot.remove_check(self.bot_check_once, call_once=True)

    # Get GuildConfig
    async def get_config(self, guild: discord.Guild) -> GuildConfig:
        # Get a cached version, if it is cached
        if guild.id in self.__gc_cache:
            return self.__gc_cache[guild.id]
        else:
            guild_config_data = await self.guilds_collection.find_one({"guild_id": guild.id})
            # Add the default GuildConfig if it dows not exist
            if guild_config_data is None:
                inserted_id = await self.add_guild(guild)
                guild_config_data = await self.guilds_collection.find_one({'_id': inserted_id})
            guild_config = GuildConfig(guild, guild_config_data, self)
            self.__gc_cache[guild.id] = guild_config
            return guild_config

    async def update_guild(self, guild: discord.Guild,
                           default_roles: List[discord.Role] = None,
                           info_channels: Dict[str, dict] = None) -> Optional[dict]:
        mongo_update_data = {'$set': {}}
        if default_roles is not None:
            mongo_update_data['$set']['default_roles'] = [role.id for role in default_roles]
        if info_channels is not None:
            for ic_name, ic_spec in info_channels.items():
                # TODO: support for other properties.
                if ic_name in INFO_CHANNEL_TYPES:
                    if ic_spec['channel'] is not None:
                        mongo_update_data['$set']['info_channels.{}.channel_id'.format(ic_name)] = ic_spec['channel'].id
                    if ic_spec['enabled'] is not None:
                        mongo_update_data['$set']['info_channels.{}.enabled'.format(ic_name)] = ic_spec['enabled']
        if mongo_update_data != {'$set': {}}:
            new_data = await self.guilds_collection.find_one_and_update({'guild_id': guild.id}, mongo_update_data, return_document=True)
            return new_data
        return None

    # Add default GuildConfig to the database
    async def add_guild(self, guild: discord.Guild):
        guild_config_data = default_guild_config_data(guild)
        guild_config_data['guild_id'] = guild.id
        guilds_collection = self.mongo_db.guilds
        insert_result = await guilds_collection.insert_one(guild_config_data)
        return insert_result.inserted_id

    # Get command filter from the database
    async def get_command_filter(self, guild: discord.Guild, name: str) -> Optional[CommandFilter]:
        command_filter_data = await self.cf_collection.find_one({"guild_id": guild.id, "name": name})
        if command_filter_data is not None:
            return CommandFilter(name,
                                 CommandDisability(command_filter_data['type']),
                                 # F*** off
                                 [self.bot.get_channel(channel_id) for channel_id in command_filter_data['channels']],  # type: ignore
                                 command_filter_data['enabled'],
                                 guild)
        else:
            return None

    # Update command filter
    async def update_command_filter(self, guild: discord.Guild,                     # Guild
                                    name: str,                                      # command name
                                    new_channels: List[discord.TextChannel] = None, # new channels for the update
                                    append_channels: bool = False,                  # wheter to append or overwrite the new channels. True - append, False - overwite
                                    enabled: bool = None,                           # wheter the command will be enabled or not
                                    filter_type: CommandDisability = None):         # set filter type, if needed
        mongo_update_data = {'$set': dict(), '$setOnInsert': {}}

        # return None if no arguments specified.
        if new_channels is None and enabled is None and filter_type is None:
            return
        if name in IMMUTABLE_COMMANDS:
            raise CommandImmutableError(name)
        if name not in [command.name for command in self.bot.commands]:
            raise CommandNotFoundError(name)

        # New channels
        if new_channels is not None:
            if append_channels:
                mongo_update_data['$push'] = {'channels': {'$each': [channel.id for channel in new_channels]}}
            else:
                mongo_update_data['$set']['channels'] = [channel.id for channel in new_channels]
        else:
            mongo_update_data['$setOnInsert']['channels'] = []

        # 'enabled'
        if enabled is not None:
            mongo_update_data['$set']['enabled'] = enabled
        else:
            mongo_update_data['$setOnInsert']['enabled'] = True

        # Filter type
        # Should this method throw an error when the wrong type disability is passed? Open for discussion.
        if filter_type is not None and filter_type.value >= 2:
            mongo_update_data['$set']['type'] = filter_type.value
        else:
            mongo_update_data['$setOnInsert']['type'] = CommandDisability.BLACKLISTED.value

        # Find, update, upsert if not found
        await self.cf_collection.find_one_and_update({'guild_id': guild.id, 'name': name}, mongo_update_data, upsert=True)

    async def create_command_filter(self, guild: discord.Guild, name: str):
        await self.update_command_filter(guild, name, [], False, True, CommandDisability.BLACKLISTED)

def setup(bot: commands.Bot):
    bot.add_cog(GuildConfigCog(bot))

def teardown(bot: commands.Bot):
    bot.get_cog('GuildConfigCog').teardown()
