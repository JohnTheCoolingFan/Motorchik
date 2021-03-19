import pymongo
from enum import Enum
from discord.ext import commands
import discord
import json
import os.path
import asyncio
from typing import List, Iterable, Optional

def info_channels():
    return dict(log=dict(), welcome=dict())

GUILD_CONFIG_ENTRIES_TYPES = dict(commands=dict,
                                  default_roles=list,
                                  levels=dict,
                                  members=dict,
                                  name=str,
                                  info_channels=info_channels)


class CommandDisability(Enum):
    NONE = 0
    GLOBAL = 1
    BLACKLISTED = 2
    WHITELISTED = 3

class CommandDisabledException(discord.DiscordException):
    def __init__(self, guild: discord.Guild, command_name: str, channel: discord.TextChannel, disability: CommandDisability):
        self.guild = guild
        self.command_name = command_name
        self.channel = channel
        self.disability = disability

class GuildConfig:
    guild: discord.Guild
    raw: dict
    commands_names: List[str]

    def __init__(self, guild: discord.Guild):
        self.guild = guild
        with open('guilds/guild_{}.json'.format(guild.id), 'r') as guild_config_file:
            self.raw = json.load(guild_config_file)
        self.commands_names = self.raw['commands'].keys()

    @property
    def welcome_channel(self) -> Optional[discord.TextChannel]:
        if self.raw['info_channels']['welcome']['enabled']:
            return self.guild.get_channel(self.raw['info_channels']['welcome']['channel_id'])
        else:
            return None

    @welcome_channel.setter
    def welcome_channel(self, new_channel: discord.TextChannel):
        self.raw['info_channels']['welcome']['channel_id'] = new_channel.id

    @property
    def log_channel(self) -> Optional[discord.TextChannel]:
        if self.raw['info_channels']['log']['enabled']:
            return self.guild.get_channel(self.raw['info_channels']['log']['channel_id'])
        else:
            return None

    @log_channel.setter
    def log_channel(self, new_channel: discord.TextChannel):
        self.raw['info_channels']['log']['channel_id'] = new_channel.id

    @property
    def default_roles(self) -> List[discord.Role]:
        return [self.guild.get_role(role_id) for role_id in self.raw['default_roles']]

    @default_roles.setter
    def default_roles(self, new_roles: Iterable[discord.Role]):
        self.raw['default_roles'] = list({role.id for role in new_roles})

    @classmethod
    async def check(cls, bot: commands.Bot, guild: discord.Guild = None):
        def check_for_entry(entry: str, guild_config_to_check: cls, entry_type):
            if entry not in guild_config_to_check.raw:
                guild_config_to_check.raw[entry] = entry_type()
        if guild is None:
            await asyncio.wait([cls.check(bot, _guild) for _guild in bot.guilds])
        else:
            if not os.path.exists('guilds/guild_{}.json'.format(guild.id)):
                cls.create_guild_config(guild)
            guild_config = cls(guild)
            print('Checking config of guild ID:{}'.format(guild.id))
            for entry_name in GUILD_CONFIG_ENTRIES_TYPES:
                check_for_entry(entry_name, guild_config, GUILD_CONFIG_ENTRIES_TYPES[entry_name])
            for command in bot.commands:
                if command.name not in guild_config.raw['commands'].keys():
                    print('Config for command "{0}" not found in config of guild ID:{1}'.format(command.name, guild_config.guild.id))
                    guild_config.raw['commands'][command.name] = dict(whitelist=[], blacklist=[], enabled=True)
            guild_config.write()

    def add_xp(self, member: discord.Member, xp_count: int):
        if str(member.id) not in self.raw['members']:
            self.raw['members'][str(member.id)] = 0
        self.raw['members'][str(member.id)] += xp_count
        self.write()

    def get_xp(self, member: discord.Member) -> int:
        return self.raw['members'][str(member.id)]

    @staticmethod
    def create_guild_config(guild: discord.Guild):
        print('Creating guild config file for ID:{}'.format(guild.id))
        with open('guilds/guild_{}.json'.format(guild.id), 'w') as new_guild_config_file:
            default_channel = guild.system_channel.id if guild.system_channel is not None else guild.text_channels[0].id
            default_info_channel = dict(channel_id=default_channel, enabled=False)
            new_guild_config = dict(name=guild.name,
                                    default_roles=[],
                                    commands=dict(),
                                    members=dict(),
                                    levels=dict(),
                                    info_channels=dict(log=default_info_channel,
                                                       welcome=default_info_channel))
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
            self.raw['info_channels'][info_channel_type]['enabled'] = new_state
            self.write()
            return True
        else:
            return False

    @property
    def json(self) -> str:
        return json.dumps(self.raw, sort_keys=True, indent=4)

class GuildConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.mongo_client = pymongo.MongoClient('localhost', 27017) # TODO with BotConfig
        self.bot = bot
        self.mongo_db = self.mongo_client['motorchik_guild_config']

    # TODO
    async def get_config(self, guild: discord.Guild) -> GuildConfig:
        pass

class MotorchikBot(commands.Bot):
    async def guild_config(self, guild: discord.Guild) -> GuildConfig:
        return self.get_cog('GuildConfigCog').get_config(guild)
