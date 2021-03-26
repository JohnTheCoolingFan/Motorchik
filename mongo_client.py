import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from guild_config import GuildConfig

class GuildConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.mongo_client = AsyncIOMotorClient('localhost', 27017, io_loop=bot.loop())
        self.bot = bot
        self.mongo_db = self.mongo_client['motorchik_guild_config']

    async def get_config(self, guild: discord.Guild) -> GuildConfig:
        guilds_db = self.mongo_db.guilds
        guild_config_data = await guilds_db.find_one({"guild_id": guild.id})
        return GuildConfig(guild, guild_config_data, guilds_db)
