import json
import discord
from discord.ext import commands

class BotConfig(commands.Cog):
    bot: commands.Bot
    log_channel: discord.TextChannel
    token: str

    def __init__(self, filename, bot: commands.Bot):
        with open(filename, 'r') as bot_config_file:
            self.raw = json.load(bot_config_file)
        self.bot = bot
        self.log_channel = bot.get_channel(self.raw['log_channel'])
        self.token = self.raw['token']

def setup(bot: commands.Bot):
    bot.add_cog(BotConfig('config.json', bot))
