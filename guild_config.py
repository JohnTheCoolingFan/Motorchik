from discord.ext import commands
import discord
import json
import os.path
import datetime
import math
from typing import List, Iterable, Optional

def info_channels_t():
    return dict(log=dict(), welcome=dict())

GUILD_CONFIG_ENTRIES_TYPES = dict(commands=dict,
                                  default_roles=list,
                                  levels=dict,
                                  members=dict,
                                  name=str,
                                  info_channels=info_channels_t)

class GuildLevel:
    index: int
    role: discord.Role
    auto_level_up: bool

    def __init__(self, index: int, role: discord.Role, auto_level_up: bool):
        self.index = index
        self.role = role
        self.auto_level_up = auto_level_up

class CommandFilter:
    name: str
    blacklist: List[discord.TextChannel]
    whitelist = List[discord.TextChannel]
    enabled: bool

    # If anyone wants me to change balcklist and whitelist terms, you can do it yourself and make a PR.
    def __init__(self, guild: discord.Guild, name: str, blacklist: Iterable[int], whitelist: Iterable[int], enabled: bool):
        self.name = name
        self.blacklist = [guild.get_channel(ch_id) for ch_id in blacklist]
        self.whitelist = [guild.get_channel(ch_id) for ch_id in whitelist]
        self.enabled = enabled

    # Black- and Whitelist
    def set_blacklist(self, blacklist: List[discord.TextChannel]):
        self.blacklist = blacklist

    def add_blacklist_channel(self, channel: discord.TextChannel):
        self.blacklist.append(channel)

    def rmv_blacklist_channel(self, channel: discord.TextChannel):
        self.blacklist.remove(channel)

    def set_whitelist(self, whitelist: List[discord.TextChannel]):
        self.whitelist = whitelist

    def add_whitelist_channel(self, channel: discord.TextChannel):
        self.whitelist.append(channel)

    def rmv_whitelist_channel(self, channel: discord.TextChannel):
        self.whitelist.remove(channel)

    # Enabled/Disabled state
    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def enabled_flip(self):
        self.enabled = not self.enabled

class InfoChannelSpecs:
    name: str
    channel: discord.TextChannel
    enabled: bool

    def __init__(self, guild: discord.Guild, name: str, channel_id: int, enabled: bool):
        self.name = name
        self.channel = guild.get_channel(channel_id)
        self.enabled = enabled

    def set_channel(self, channel: discord.TextChannel):
        self.channel = channel

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def enabled_flip(self):
        self.enabled = not self.enabled

# TODO: Test new format and migrate guild configs to new format
class GuildConfig:
    guild: discord.Guild
    command_filters: List[CommandFilter]
    default_roles: List[discord.Role]
    info_channels: List[InfoChannelSpecs]
    members: dict

    def __init__(self, guild: discord.Guild):
        self.guild = guild
        with open('guilds/guild_{}.json'.format(guild.id), 'r') as guild_config_file:
            raw_config = json.load(guild_config_file)
        for command_name, command_filters in raw_config['commands'].items():
            self.command_filters.append(CommandFilter(guild, command_name, command_filters['blacklist'], command_filters['whitelist'], command_filters['enabled']))
        self.default_roles = [guild.get_role(role_id) for role_id in raw_config['default_roles']]
        log_channel_specs = InfoChannelSpecs(guild, 'log', raw_config['info_channels']['log']['channel_id'], raw_config['info_channels']['log']['enabled'])
        welcome_channel_specs = InfoChannelSpecs(guild, 'welcome', raw_config['info_channels']['welcome']['channel_id'], raw_config['info_channels']['welcome']['enabled'])
        self.info_channels.append(log_channel_specs)
        self.info_channels.append(welcome_channel_specs)
        self.members = raw_config['members']

    def get_command_filter_index(self, name: str) -> int:
        for i, command_filter in enumerate(self.command_filters):
            if command_filter.name == name:
                return i
        return None

    def get_info_channel_index(self, name: str) -> int:
        for i, info_channel in enumerate(self.info_channels):
            if info_channel.name == name:
                return i
        return None

    def create_command_filter(self, name: str):
        self.command_filters.append(CommandFilter(self.guild, name, [], [], True))

    def create_info_channel(self, name: str, channel: discord.TextChannel):
        self.info_channels.append(InfoChannelSpecs(self.guild, name, channel.id, True))

    def switch_info_channel(self, info_channel_type: str, new_state: bool) -> bool:
        info_channel_spec = self.info_channels[self.get_info_channel_index(info_channel_type)]
        if info_channel_spec is not None:
            info_channel_spec.enabled = new_state
            return True
        else:
            return False

    def switch_command(self, command_name: str, new_state: bool):
        command_filter = self.command_filters[self.get_command_filter_index(command_name)]
        command_filter.enabled = new_state

    def set_command_whitelist(self, command_name: str, new_filter: Iterable[discord.TextChannel]) -> bool:
        command_filter = self.command_filters[self.get_command_filter_index(command_name)]
        if command_filter is not None:
            command_filter.set_whitelist(new_filter)
            return True
        else:
            return False

    def set_command_blacklist(self, command_name: str, new_filter: Iterable[discord.TextChannel]) -> bool:
        command_filter = self.command_filters[self.get_command_filter_index(command_name)]
        if command_filter is not None:
            command_filter.set_blacklist(new_filter)
            return True
        else:
            return False

    # More for backwards compatibility (lol) than for practical use. Using set_blacklist and set_whitelist is encouraged
    def set_command_filter(self, command_name: str, filter_name: str, new_filter: Iterable[discord.TextChannel]) -> bool:
        if filter_name == 'whitelist':
            return self.set_command_whitelist(command_name, new_filter)
        elif filter_name == 'blacklist':
            return self.set_command_blacklist(command_name, new_filter)
        else:
            return False # Not blacklist and not whitelist. WTF

    @property
    def welcome_channel(self) -> Optional[discord.TextChannel]:
        channel_spec = self.info_channels[self.get_info_channel_index('welcome')]
        if channel_spec is not None and channel_spec.enabled:
            return channel_spec.channel
        return None

    @welcome_channel.setter
    def welcome_channel(self, new_channel: discord.TextChannel):
        channel_spec = self.info_channels[self.get_info_channel_index('log')]
        if channel_spec is not None:
            channel_spec.set_channel(new_channel)

    @property
    def log_channel(self) -> Optional[discord.TextChannel]:
        channel_spec = self.info_channels[self.get_info_channel_index('log')]
        if channel_spec is not None and channel_spec.enabled:
            return channel_spec.channel
        return None

    @log_channel.setter
    def log_channel(self, new_channel: discord.TextChannel):
        channel_spec = self.info_channels[self.get_info_channel_index('log')]
        if channel_spec is not None:
            channel_spec.set_channel(new_channel)

    def add_xp(self, member: discord.Member, xp_count: int):
        if str(member.id) not in self.members:
            self.members[str(member.id)] = 0
        self.members[str(member.id)] += xp_count

    def get_xp(self, member: discord.Member) -> int:
        return self.members[str(member.id)]

    def process_message(self, message: discord.Message):
        if not message.author.bot:
            self.add_xp(message.author, len(message.content) // 10 + 1)
            XpLog.log_message_raw(message.created_at, message.id, message.author.id, (len(message.content)//10)+1, message.guild.id)

    @staticmethod
    def create(guild: discord.Guild):
        default_channel = guild.system_channel.id if guild.system_channel is not None else guild.text_channels[0].id
        gc = dict(commands=[], default_roles=[],
                  info_channels=[dict(name='welcome', channel_id=default_channel, enabled=False),
                                 dict(name='log', channel_id=default_channel, enabled=False)],
                  members=dict(),
                  name=guild.name)
        with open('guilds/guild_{}.json'.format(guild.id), 'w') as new_gc_file:
            json.dump(new_gc_file, gc, sort_keys=True, indent=4)

    @property
    def minimal_dict(self) -> dict:
        command_filters = [dict(blacklist=[channel.id for channel in cf.blacklist], whitelist=[channel.id for channel in cf.whitelist], enabled=cf.enabled) for cf in self.command_filters]
        default_roles = [role.id for role in self.default_roles]
        info_channels = [dict(channel_id=ics.channel.id, enabled=ics.enabled) for ics in self.info_channels]
        levels = []
        members = self.members
        name = self.guild.name
        return dict(command_filters=command_filters,
                          default_roles=default_roles,
                          info_channels=info_channels,
                          levels=levels,
                          members=members,
                          name=name)

    @property
    def json(self) -> str:
        return json.dumps(self.minimal_dict)

    def write(self):
        with open('guilds/guild_{}.json'.format(self.guild.id), 'w') as guild_config:
            json.dump(self.minimal_dict, guild_config, indent=4, sort_keys=True)


class XpLogEntry:
    def __init__(self, line: dict):
        self.timestamp = datetime.datetime.fromtimestamp(line['timestamp'])
        self.message_id = line['message_id']
        self.author_id = line['autthor_id']
        self.xp = line['xp']

class XpLog:
    entries: List[XpLogEntry]

    def __init__(self, guild: discord.Guild):
        self.guild = guild
        with open('xplog/log_{}.txt'.format(guild.id), 'r') as xplog_file:
            parsed_file = self.parse_str(xplog_file.read())
            self.entries = []
            for line in parsed_file:
                self.entries.append(XpLogEntry(line))

    def log_message(self, message: discord.Message, xp):
        self.entries.append(XpLogEntry(dict(
            timestamp = math.floor(message.created_at.timestamp()),
            message_id = message.id,
            author_id = message.author.id,
            xp = xp)))
        self.log_message_raw(
            message.created_at,
            message.id,
            message.author.id,
            xp,
            message.guild.id)

    def remove_entries(self, message_ids: Optional[List[int]]):
        pass

    def edit_entry(self, message_id: int):
        pass

    def write(self):
        result = ['#timestamp message id         author id          earned xp']
        for entry in self.entries:
            result.append('{timestamp} {message_id} {author_id} {xp}'.format(
                timestamp = entry.timestamp.timestamp(),
                message_id = entry.message_id,
                author_id = entry.author_id,
                xp = entry.xp))
        result_str = '\n'.join(result)
        with open('xplog/log_{}.txt'.format(self.guild.id), 'w') as xplog_file:
            xplog_file.write(result_str)

    @classmethod
    def log_message_raw(cls, created_at: datetime.datetime, message_id: int, author_id: int, xp_count: int, guild_id: int):
        log_line = '{timestamp} {message_id} {author_id} {xp_count}\n'.format(
                timestamp=math.floor(created_at.timestamp()),
                message_id=message_id,
                author_id=author_id,
                xp_count=xp_count)
        with open('xplog/log_{}.txt'.format(guild_id), 'a+') as xplog_file:
            xplog_file.write(log_line)

    @staticmethod
    def parse_str(input_str: str) -> List[dict]:
        lines = input_str.split('\n')
        clear_lines = [x for x in lines if not x.startswith('#')]
        result = []
        for _, line in enumerate(clear_lines):
            split_line = line.split(' ')
            result.append(dict(
                timestamp = int(split_line[0]),
                message_id = int(split_line[1]),
                author_id = int(split_line[2]),
                xp = int(split_line[3])
                ))
        return result

class GuildConfigCog(commands.Cog):
    _guilds: dict

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        GuildConfig.check(bot)
        for guild in bot.guilds:
            self._guilds[str(guild.id)] = GuildConfig(guild)

    def get_guild_config(self, guild_id: int):
        return self._guilds[str(guild_id)]

def setup(bot: commands.Bot):
    bot.add_cog(GuildConfigCog(bot))
