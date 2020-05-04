import json
import discord
from discord.ext import commands

class BotConfig:
    bot: commands.Bot
    token: str

    def __init__(self, filename, bot: commands.Bot):
        with open(filename, 'r') as bot_config_file:
            self.raw = json.load(bot_config_file)
        self.bot = bot

    @property
    def log_channel(self) -> discord.TextChannel:
        return self.bot.get_channel(self.raw['log_channel'])
