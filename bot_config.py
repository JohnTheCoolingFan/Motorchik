import json
import os.path as p
import sys
from typing import Optional

import discord
from discord.ext import commands


class BotConfig(commands.Cog):
    bot: commands.Bot
    log_channel: discord.TextChannel
    token: str
    storage_method: str
    mongo: Optional[dict]
    json: Optional[dict]

    def __init__(self, filename, bot: commands.Bot):
        print('Loading BotConfig module...', end='')
        if p.exists('config.json'):
            with open(filename, 'r') as bot_config_file:
                self.raw = json.load(bot_config_file)
            self.bot = bot
            self.log_channel = bot.get_channel(self.raw['log_channel'])
            self.token = self.raw['token']
            if self.raw['storage_method'] == 'mongo':
                if 'mongo' in self.raw:
                    self.mongo_init()
                else:
                    print('Error: storage_method is "mongo", but there is no configuration for MongoDB (no "mongo" entry)')
                    sys.exit(1)
            print(' Done')
        else:
            print('Error: config.json does not exist')
            sys.exit(1)

    def mongo_init(self):
        self.storage_method = 'mongo'
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
        self.mongo['username'] = self.raw['mongo']['username']
        self.mongo['password'] = self.raw['mongo']['password']

    def json_init(self):
        self.storage_method = 'mongo'
        self.json = dict()
        self.json['dir'] = 'guilds' if 'dir' not in self.raw['json'] else self.raw['json']['dir'] # Set the dir

def setup(bot: commands.Bot):
    bot.add_cog(BotConfig('config.json', bot))
