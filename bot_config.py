import json
from typing import Optional

import discord
from discord.ext import commands


class BotConfig(commands.Cog):
    bot: commands.Bot
    log_channel: discord.TextChannel
    token: str
    mongo: dict

    def __init__(self, filename, bot: commands.Bot):
        with open(filename, 'r') as bot_config_file:
            self.raw = json.load(bot_config_file)
        self.bot = bot
        self.log_channel = bot.get_channel(self.raw['log_channel'])
        self.token = self.raw['token']
        self.mongo = dict()
        self.mongo['host'] = self.raw['mongo']['host']
        port = self.raw['mongo']['port']
        if port:
            try:
                if port is not int:
                    port = int(port)
                self.mongo['port'] = port
            except ValueError:
                print('Invalid port: {}'.format(port))
        if self.raw['mongo']['username']:
            self.mongo['username'] = self.raw['mongo']['username']
        if self.raw['mongo']['password']:
            self.mongo['password'] = self.raw['mongo']['password']

def setup(bot: commands.Bot):
    bot.add_cog(BotConfig('config.json', bot))
