import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from guild_config import GuildConfig

class GuildConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.mongo_client = AsyncIOMotorClient('localhost', 27017, io_loop=bot.loop())
        self.bot = bot
        self.mongo_db = self.mongo_client['motorchik_guild_config']
        self.collections = self.mongo_db.guilds

    async def get_config(self, guild: discord.Guild) -> GuildConfig:
        guild_config_data = await self.collections.find_one({"guild_id": guild.id})
        return GuildConfig(guild, guild_config_data, self.collections)

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
        await guilds_collection.insert_one(guild_config_data)
