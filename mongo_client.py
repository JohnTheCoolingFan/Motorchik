from typing import List, Optional

import discord
import pymongo
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient

from guild_config import (CommandDisability, CommandDisabledError,
                          CommandFilter, CommandImmutableError,
                          CommandNotFoundError, GuildConfig)

IMMUTABLE_COMMANDS = ['command', 'config', 'say', 'say_dm']

class GuildConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        bot_config = bot.get_cog('BotConfig')
        self.mongo_client = AsyncIOMotorClient(host = bot_config.mongo['host'],
                                               port=bot_config.mongo['port'],
                                               username=bot_config.mongo['username'],
                                               password=bot_config.mongo['password'],
                                               io_loop=bot.loop,
                                               authSource='motorchik_guild_config',
                                               connect=True)
        self.bot = bot
        self.mongo_db = self.mongo_client['motorchik_guild_config']
        self.guilds_collection = self.mongo_db.guilds
        self.cf_collection = self.mongo_db.command_filters
        self._gc_cache = dict()

    async def bot_check_once(self, ctx: commands.Context):
        if ctx.command.name in IMMUTABLE_COMMANDS:
            return True
        else:
            command_filter = await self.get_command_filter(ctx.guild, ctx.command.name)
            if command_filter is None:
                return True
            else:
                if not command_filter.enabled:
                    raise CommandDisabledError(ctx.guild, ctx.command.name, ctx.channel, CommandDisability.GLOBAL)
                if command_filter.filter_type == CommandDisability.BLACKLISTED and ctx.channel in command_filter.filter_list:
                    raise CommandDisabledError(ctx.guild, ctx.vommand.name, ctx.channel, command_filter.filter_type)
                if command_filter.filter_type == CommandDisability.WHITELISTED and ctx.channel not in command_filter.filter_list:
                    raise CommandDisabledError(ctx.guild, ctx.command.name, ctx.channel, command_filter.filter_type)
                return True

    async def create_indexes(self):
        # Create indexes
        # I'm not sure what indexing method to use for guild ids, but for now let it be ascending...
        # I'm not even sure if I really need index guild ids
        await self.cf_collection.create_index([('guild_id', pymongo.ASCENDING), ('name', pymongo.TEXT)])
        await self.guilds_collection.create_index([('guild_id', pymongo.ASCENDING)])

    def teardown(self):
        self._gc_cache.clear()
        self.mongo_client.close()
        self.bot.remove_check(self.bot_check_once, call_once=True)

    async def get_config(self, guild: discord.Guild) -> GuildConfig:
        if guild.id in self._gc_cache:
            return self._gc_cache[guild.id]
        else:
            guild_config_data = await self.guilds_collection.find_one({"guild_id": guild.id})
            if guild_config_data is not None:
                guild_config = GuildConfig(guild, guild_config_data, self.guilds_collection)
                self._gc_cache[guild.id] = guild_config
            else:
                inserted_id = self.add_guild(guild)
                guild_config_data = await self.guilds_collection.find_one({'_id': inserted_id})
            return guild_config

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
            }
        }
        guilds_collection = self.mongo_db.guilds
        return await guilds_collection.insert_one(guild_config_data).inserted_id

    async def get_command_filter(self, guild: discord.Guild, name: str) -> Optional[CommandFilter]:
        command_filter_data = await self.cf_collection.find_one({"guild_id": guild.id, "name": name})
        if command_filter_data is not None:
            return CommandFilter(name,
                                 command_filter_data['type'],
                                 [self.bot.get_channel(channel_id) for channel_id in command_filter_data['channels']],
                                 command_filter_data['enabled'],
                                 guild)
        else:
            return None

    async def update_command_filter(self, guild: discord.Guild,                     # Guild
                                    name: str,                                      # command name
                                    new_channels: List[discord.TextChannel] = None, # new channels for the update
                                    append_channels: bool = False,                  # wheter to append or overwrite the new channels. True - append, False - overwite
                                    enabled: bool = None,                           # wheter the command will be enabled oe not
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
