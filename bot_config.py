"""
Manages loading and processing config values from config.json and loads GuildConfig clients
"""

import json
import os.path as p
import sys
from typing import Optional

import discord
from discord.ext import commands


class BotConfig(commands.Cog):
    bot: commands.Bot
    log_channel: Optional[discord.TextChannel]
    token: str
    storage_method: str = ''
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
                    self.storage_method = 'mongo'
                else:
                    print('Error: storage_method is "mongo", but there is no configuration for MongoDB (no "mongo" entry)', file=sys.stderr)
                    sys.exit(1)
            elif self.raw['storage_method'] == 'json':
                if 'json' in self.raw:
                    self.storage_method = 'json'
                else:
                    print('Error: storage_method is "json", but there is no configuration for JSON (no "json" entry)', file=sys.stderr)
                    sys.exit(1)
            else:
                print('No config storage method specified. Running without GuildConfig is not supported yet.', file=sys.stderr)
                sys.exit(1)
            print(' Done')
        else:
            print('Error: config.json does not exist', file=sys.stderr)
            sys.exit(1)

    def mongo_init(self):
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
        self.bot.load_extension('mongo_client')

    def json_init(self):
        # More settings? Dunno.
        self.json = dict()
        if 'dir' in self.raw['json']:
            if isinstance(self.raw['json']['dir'], str):
                self.json['dir'] = self.raw['json']['dir']
            else:
                print('Non-critical Error: "dir" entry for json config storage is not a string. Setting default ("guilds")')
                self.json['dir'] = 'guilds'
        else:
            print('"dir" not found in json config storage method, defaulting to "guilds"')
        if 'minimize' in self.raw['json']:
            self.json['minimize'] = bool(self.raw['json']['minimize'])
        self.bot.load_extension('json_client')

def setup(bot: commands.Bot):
    bot_config_cog = BotConfig('config.json', bot)
    bot.add_cog(bot_config_cog)
    if bot_config_cog.storage_method == 'mongo':
        bot_config_cog.mongo_init()
    elif bot_config_cog.storage_method == 'json':
        bot_config_cog.json_init()
    else:
        print("Error: no storage method", file=sys.stderr)
        sys.exit(1)
