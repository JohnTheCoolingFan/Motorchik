from discord.ext import commands
import discord
import json
import os.path
from typing import List, Union, Iterable


class GuildConfig:
    guild: discord.Guild
    raw: dict
    commands_names: List[str]
    welcome_channel: Union[discord.TextChannel, None]
    log_channel: Union[discord.TextChannel, None]
    reports_channel: Union[discord.TextChannel, None]
    default_roles: List[discord.Role]

    def __init__(self, guild: discord.Guild):
        self.guild = guild
        with open('guild/guild_{}.json'.format(guild.id), 'r') as guild_config:
            self.raw = json.load(guild_config)
        self.commands_names = self.raw['commands'].keys()

        # Check and set for welcome, log, and reports
        if self.raw['welcome']['enabled']:
            self.welcome_channel = self.guild.get_channel(self.raw['welcome']['channel_id'])
        else:
            self.welcome_channel = None
        if self.raw['log']['enabled']:
            self.log_channel = self.guild.get_channel(self.raw['log']['channel_id'])
        else:
            self.log_channel = None
        if self.raw['reports']['enabled']:
            self.reports_channel = self.guild.get_channel(self.raw['reports']['channel_id'])
        else:
            self.reports_channel = None

        # Check and set default roles
        if self.raw['default_roles']:
            self.default_roles = [self.guild.get_role(role_id) for role_id in self.raw['default_roles']]
        else:
            self.default_roles = []

    def update_info_channels(self):
        # Exactly the same as in __init__
        if self.raw['welcome']['enabled']:
            self.welcome_channel = self.guild.get_channel(self.raw['welcome']['channel_id'])
        else:
            self.welcome_channel = None
        if self.raw['log']['enabled']:
            self.log_channel = self.guild.get_channel(self.raw['log']['channel_id'])
        else:
            self.log_channel = None
        if self.raw['reports']['enabled']:
            self.reports_channel = self.guild.get_channel(self.raw['reports']['channel_id'])
        else:
            self.reports_channel = None

    @classmethod
    def check(cls, bot: commands.Bot, guild: discord.Guild = None):
        if guild is None:
            for guild in bot.guilds:
                cls.check(bot, guild)
        else:
            if not os.path.exists('guilds/guild_{}.json'.format(guild.id)):
                cls.create_guild_config(guild)
            guild_config = cls(guild)
            print('Checking config of guild ID:{}'.format(guild.id))
            for command in bot.commands:
                if command.name not in guild_config.raw['commands'].keys():
                    print('Config for command "{0}" not found in config of guild ID:{1}'.format(command.name, guild_config.guild.id))
                    guild_config.raw['commands'][command.name] = dict(whitelist=[], blacklist=[], enabled=True)
            guild_config.write()

    @classmethod
    def create_guild_config(cls, guild: discord.Guild):
        print('Creating guild config file for ID:{}'.format(guild.id))
        with open('guilds/guild_{}.json'.format(guild.id), 'w') as new_guild_config_file:
            default_channel = guild.system_channel.id if guild.system_channel is not None else guild.text_channels[0].id
            default_info_channel = dict(channel_id=default_channel, enabled=False)
            new_guild_config = dict(name=guild.name, welcome=default_info_channel, log=default_info_channel, reports=default_info_channel, default_roles=[], commands=dict())
            json.dump(new_guild_config, new_guild_config_file, sort_keys=True, indent=4)

    def write(self):
        with open('guild_{}.json'.format(self.guild.id), 'w') as guild_config:
            json.dump(self.raw, guild_config, indent=4, sort_keys=True)

    async def switch_command(self, command_name: str, new_state: bool) -> bool:
        if command_name in self.commands_names:
            self.raw['commands'][command_name]['enabled'] = new_state
            self.write()
            return True
        else:
            return False

    async def set_command_filter(self, command_name: str, filter_name: str, new_filter: Iterable[discord.TextChannel]) -> bool:
        if command_name in self.commands_names:
            self.raw['commands'][filter_name] = list({channel.id for channel in new_filter})
            self.write()
            return True
        else:
            return False

    def set_info_channel(self, messages_type: str, new_channel: discord.TextChannel):
        self.raw[messages_type]['channel_id'] = new_channel.id
        self.update_info_channels()
        self.write()

    def switch_info_channel(self, info_channel_type: str, new_state: bool):
        self.raw[info_channel_type]['enabled'] = new_state
        self.update_info_channels()
        self.write()

    def set_default_roles(self, new_roles: Iterable[discord.Role]):
        self.raw['default_roles'] = list({role.id for role in new_roles})
        self.default_roles = list(new_roles)
        self.write()

    def dump_json(self) -> str:
        return json.dumps(self.raw, sort_keys=True, indent=4)
