from discord.ext import commands
import discord

import json

from typing import List


class BotConfig:
    def __init__(self, bot: commands.Bot, filename: str):
        self.bot = bot
        with open(filename, 'r') as config_file:
            self.raw_config = json.load(config_file)
        self.filename = filename

    async def write(self):
        with open(self.filename, 'w') as config_file:
            json.dump(self.raw_config, config_file, indent=4, sort_keys=True)

    async def check(self):
        print('Checking config')
        # Check that all guild where bot is are in config
        for guild in self.bot.guilds:
            if str(guild.id) not in self.raw_config.keys():
                print('Guild "{0.name}" ({0.id}) not found in config.'.format(guild))
                await self.add_guild(guild)

        # Check guild configs
        for guild_id, guild_config in self.raw_config.items():
            for command in self.bot.commands:
                if command.name not in guild_config['commands'].keys():
                    print('Config for command "{0}" not found in config of guild "{1}"'.format(command.name, guild_config['name']+'(ID '+guild_id+')'))
                    guild_config['commands'][command.name] = {'whitelist': [], 'blacklist': [], 'enabled': True}

        # Write config
        await self.write()
        print('Config check successful')

    async def add_guild(self, guild):
        default_channel = guild.system_channel.id if guild.system_channel is not None else guild.text_channels[0].id
        self.raw_config[str(guild.id)] = {'name': guild.name, 'welcome': {'channel_id': default_channel, 'enabled': False}, 'log': {'channel_id': default_channel, 'enabled': False}, 'reports': {'channel_id': default_channel, 'enabled': False}, 'default_roles': [], 'commands': {}}

    class GuildConfig:
        guild: discord.Guild
        raw_config: dict
        commands: list
        welcome_channel: discord.TextChannel
        log_channel: discord.TextChannel
        reports_channel: discord.TextChannel
        default_roles: list

        def __init__(self, guild: discord.Guild, bot_config):
            self.guild = guild
            self.bot_config = bot_config
            self.raw_config = bot_config.raw_config[str(guild.id)]
            self.update()

        def update(self):
            self.commands = self.raw_config['commands'].keys()
            self.welcome_channel = self.guild.get_channel(self.raw_config['welcome']['channel_id']) if self.raw_config['welcome']['enabled'] else None
            self.log_channel = self.guild.get_channel(self.raw_config['log']['channel_id']) if self.raw_config['log']['enabled'] else None
            self.reports_channel = self.guild.get_channel(self.raw_config['reports']['channel_id']) if self.raw_config['reports']['enabled'] else None
            self.default_roles = [self.guild.get_role(role_id) for role_id in self.raw_config['default_roles']] if self.raw_config['default_roles'] else []
            self.bot_config.raw_config[str(self.guild.id)] = self.raw_config

        async def switch_command(self, command_name: str, new_state: bool) -> bool:
            if command_name in self.commands:
                self.raw_config['commands'][command_name]['enabled'] = new_state
                self.update()
                await self.bot_config.write()
                return True
            else:
                return False

        async def command_filter(self, command_name, filter_name, new_filter) -> bool:
            if command_name in self.commands:
                self.raw_config['commands'][command_name][filter_name] = list({channel.id for channel in new_filter})
                self.update()
                await self.bot_config.write()
                return True
            else:
                return False

        async def set_messages(self, messages_type: str, new_id: int):
            self.raw_config[messages_type]['channel_id'] = new_id
            self.update()
            await self.bot_config.write()

        async def switch_messages(self, messages_type: str, new_state: int):
            self.raw_config[messages_type]['enabled'] = new_state
            self.update()
            await self.bot_config.write()

        async def set_default_roles(self, new_roles: List[discord.Role]):
            self.raw_config['default_roles'] = list({role.id for role in new_roles})
            self.update()
            await self.bot_config.write()

        def json_config(self) -> str:
            return json.dumps(self.raw_config, sort_keys=True, indent=4)
