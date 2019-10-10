from discord.ext import commands
import discord
import json
import os.path
from typing import List, Iterable, Optional


class GuildConfig:
    guild: discord.Guild
    raw: dict
    commands_names: List[str]
    welcome_channel: Optional[discord.TextChannel]
    log_channel: Optional[discord.TextChannel]
    reports_channel: Optional[discord.TextChannel]
    default_roles: List[discord.Role]

    def __init__(self, guild: discord.Guild):
        self.guild = guild
        with open('guilds/guild_{}.json'.format(guild.id), 'r') as guild_config:
            self.raw = json.load(guild_config)
        self.commands_names = self.raw['commands'].keys()

    @property
    def welcome_channel(self) -> Optional[discord.TextChannel]:
        if self.raw['welcome']['enabled']:
            return self.guild.get_channel(self.raw['welcome']['channel_id'])
        else:
            return None

    @welcome_channel.setter
    def welcome_channel(self, new_channel: discord.TextChannel):
        self.raw['welcome']['channel_id'] = new_channel.id

    @property
    def log_channel(self) -> Optional[discord.TextChannel]:
        if self.raw['log']['enabled']:
            return self.guild.get_channel(self.raw['log']['channel_id'])
        else:
            return None

    @log_channel.setter
    def log_channel(self, new_channel: discord.TextChannel):
        self.raw['log']['channel_id'] = new_channel.id

    @property
    def reports_channel(self) -> Optional[discord.TextChannel]:
        if self.raw['reports']['enabled']:
            return self.guild.get_channel(self.raw['welcome']['channel_id'])
        else:
            return None

    @reports_channel.setter
    def reports_channel(self, new_channel: discord.TextChannel):
        self.raw['reports']['channel_id'] = new_channel.id

    @property
    def default_roles(self) -> List[discord.Role]:
        return [self.guild.get_role(role_id) for role_id in self.raw['default_roles']]

    @default_roles.setter
    def default_roles(self, new_roles: Iterable[discord.Role]):
        self.raw['default_roles'] = list({role.id for role in new_roles})

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
        with open('guilds/guild_{}.json'.format(self.guild.id), 'w') as guild_config:
            json.dump(self.raw, guild_config, indent=4, sort_keys=True)

    def switch_command(self, command_name: str, new_state: bool) -> bool:
        if command_name in self.commands_names:
            self.raw['commands'][command_name]['enabled'] = new_state
            self.write()
            return True
        else:
            return False

    def set_command_filter(self, command_name: str, filter_name: str, new_filter: Iterable[discord.TextChannel]) -> bool:
        if command_name in self.commands_names:
            self.raw['commands'][command_name][filter_name] = list({channel.id for channel in new_filter})
            self.write()
            return True
        else:
            return False

    def switch_info_channel(self, info_channel_type: str, new_state: bool) -> bool:
        if info_channel_type in ['welcome', 'log', 'reports']:
            self.raw[info_channel_type]['enabled'] = new_state
            self.write()
            return True
        else:
            return False

    @property
    def json(self) -> str:
        return json.dumps(self.raw, sort_keys=True, indent=4)
