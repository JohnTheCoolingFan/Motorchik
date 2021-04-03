import json
from typing import Optional, TypedDict

import discord
from discord.ext import commands


class MongoCredentials(TypedDict):
    host: str
    port: Optional[int]
    username: Optional[str]
    password: Optional[str]


class BotConfig(commands.Cog):
    bot: commands.Bot
    log_channel: discord.TextChannel
    token: str
    mongo: MongoCredentials

    def __init__(self, filename, bot: commands.Bot):
        with open(filename, 'r') as bot_config_file:
            self.raw = json.load(bot_config_file)
        self.bot = bot
        self.log_channel = bot.get_channel(self.raw['log_channel'])
        self.token = self.raw['token']
        self.mongo = dict()
        self.mongo['host'] = self.raw['mongo']['host']
        if self.raw['mongo']['port']:
            try:
                port = int(self.raw['mongo']['port'])
                self.mongo['port'] = port
            except ValueError:
                print('Invalid port: {}'.format(self.raw['mongo']['port']))
        if self.raw['mongo']['username']:
            self.mongo['username'] = self.raw['mongo']['username']
        if self.raw['mongo']['password']:
            self.mongo['password'] = self.raw['mongo']['password']

def setup(bot: commands.Bot):
    bot.add_cog(BotConfig('config.json', bot))
