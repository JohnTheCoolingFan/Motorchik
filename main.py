#! /usr/bin/python3.7
# TabNine::sem

# TODO: make role-level system and levelup/leveldown commands
# TODO: make experience system
# TODO: add a report system (report user or report message)
# TODO: add setting to report with emoji
# TODO: split code into a number of files

from discord.ext import commands
import discord
import json
import random


tokenfile = open('token.txt', 'r')
TOKEN = tokenfile.read().rstrip()
tokenfile.close()

MOD_LIST = ['Placeable-off-grid', 'No Artillery Map Reveal', 'Random Factorio Things', 'Plutonium Energy', 'RealisticReactors Ingo']
DEFAULT_GUILD_CONFIG = {'name': '', 'welcome_channel_id': 0, 'welcome_enabled': True, 'log_channel_id': 0, 'log_enabled': True, 'reports_channel_id': 0, 'default_roles': [], 'commands': {}}

bot = commands.Bot(command_prefix='$')


class BotConfig():
    def __init__(self, bot, filename):
        self.bot = bot
        config_file = open(filename, 'r')
        self.raw_config = json.loads(config_file.read())
        config_file.close()
        self.filename = filename

    async def write(self):
        config_file = open(self.filename, 'w')
        config_file.write(json.dumps(self.raw_config, sort_keys=True, indent=4))
        config_file.close()

    async def check(self):
        print('Checking config')
        # Check that all guild where bot is are in config
        for guild in self.bot.guilds:
            if str(guild.id) not in self.raw_config.keys():
                print('Guild "{0.name}" ({0.id}) not found in config.'.format(guild))
                await self.add_guild(guild)

        # Check guild configs
        for guild_id, guild_config in self.raw_config.items():
            for command in bot.commands:
                if command.name not in guild_config['commands'].keys():
                    print('Config for command "{0}" not found in config of guild "{1}"'.format(command.name, guild_config['name']+'(ID '+guild_id+')'))
                    guild_config['commands'][command.name] = {'whitelist': [], 'blacklist': [], 'enabled': True}

        # Write config
        await self.write()
        print('Config check succesful')

    async def add_guild(self, guild):
        default_channel = guild.system_channel.id if guild.system_channel is not None else guild.text_channels[0].id
        self.raw_config[str(guild.id)] = {'name': guild.name, 'welcome_channel_id': default_channel, 'log_channel_id': default_channel, 'welcome_enabled': False, 'log_enabled': False, 'report_channel_id': default_channel, 'default_roles': [], 'commands': {}}

    class GuildConfig():
        def __init__(self, guild, bot_config):
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
            await self.bot_config.write()

        async def switch_command(self, command_name, new_state):
            if command_name in self.commands:
                self.raw_config['commands'][command_name]['enabled'] = new_state
                self.update()
                return True
            else:
                return False

        async def command_filter(self, command_name, filter_name, new_filter):
            if command_name in self.commands:
                self.raw_config['commands'][command_name][filter_name] = {channel.id for channel in new_filter}
                self.update()
                return True
            else:
                return False

        async def set_messages(self, messages_type, new_id):
            self.raw_config[messages_type+'_channel_id'] = new_id
            self.update()

        async def switch_messages(self, messages_type, new_state):
            self.raw_config[messages_type+'_enabled'] = new_state
            self.update()

        async def set_default_roles(self, new_roles):
            self.raw_config['default_roles'] = {role.id for role in new_roles}
            self.update()

        def json_config(self):
            return json.dumps(self.raw_config, sort_keys=True, indent=4)

bot_config = BotConfig(bot, 'config.json')


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    await bot_config.check()

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.id in message.raw_mentions:
            await message.channel.send(random.choice(['Yeah?', 'What?', 'Yeah, I\'m here.', 'Did I missed something?', 'Yep', 'Nah', 'Uhm...']))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_config = bot_config.GuildConfig(member.guild, bot_config)
        if guild_config.raw_config['welcome_enabled']:
            await guild_config.welcome_channel.send('Welcome, {0.mention}'.format(member))
        if guild_config.raw_config['default_roles']:
            await member.add_roles(*guild_config.default_roles, reason='New member join.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_config = bot_config.GuildConfig(member.guild, bot_config)
        if guild_config.raw_config['welcome_enabled']:
            await guild_config.welcome_channel.send('Goodbye, {0} (ID:{1})'.format(str(member), member.id))

    @commands.command(description='\"Hello\" in English', brief='\"Hello\" in English', help='Returns \"Hello\" in English')
    async def hello(self, ctx):
        await ctx.send('Hello!')

    @commands.command(aliases=['gutentag'], description='\"Hello\" in German', brief='\"Hello\" in German', help='Returns \"Hello\" in German')
    async def hello_german(self, ctx):
        await ctx.send('Guten tag')

    @commands.command(aliases=['privet'], description='\"Hello\" in Russian', brief='\"Hello\" in Russian', help='Returns \"Hello\" in Russian')
    async def hello_russian(self, ctx):
        await ctx.send('Приветствую!')

    @commands.command(hidden=True, help='tag')
    async def guten(self, ctx):
        await ctx.send('tag')

bot.add_cog(Greetings(bot))


class TestCommands(commands.Cog, name='Test Commands', command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Returns text typed after $test')
    async def test(self, ctx, *, text):
        await ctx.send(text)

    @commands.command(help='Returns passed arguments count and the arguments', aliases=['advtest', 'atest'])
    async def advanced_test(self, ctx, *args):
        await ctx.send('Passed {} arguments: {}'.format(len(args), ', '.join(args)))

bot.add_cog(TestCommands(bot))


class FunCommands(commands.Cog, name='Fun'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='You spin me right round, baby, right round')
    async def spin(self, ctx):
        await ctx.send('https://www.youtube.com/watch?v=PGNiXGX2nLU')

    @commands.command(aliases=['XcQ'], help='You\'ve got RICKROLLED, LUL')
    async def rickroll(self, ctx):
        await ctx.send('<https://www.youtube.com/watch?v=dQw4w9WgXcQ>')
        await ctx.send('<:kappa_jtcf:546748910765604875>')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

bot.add_cog(FunCommands(bot))


class FactorioCog(commands.Cog, name='Factorio'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['modstat'], description='Info about mods', brief='Info about mods', help='Prints a bunch of commands for uBot to display info about mods')
    async def mods_statistics(self, ctx):
        for modname in MOD_LIST:
            await ctx.send(content='>>{0}<<'.format(modname), delete_after=1)
        await ctx.message.delete()

bot.add_cog(FactorioCog(bot))


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['clear'], description='Clear chat', brief='Clear chat', help='Deletes specified count of messages in this channel. Only for admins and moderators.')
    @commands.has_permissions(manage_messages=True)
    async def clearchat(self, ctx, message_count: int):
        await ctx.message.delete()
        async for message in ctx.channel.history(limit=message_count):
            await message.delete()

bot.add_cog(Moderation(bot))


class Reports(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def report(self, ctx):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        await guild_config.reports_channel.send('Well, `report` command is incomplete.\n{0.author.mention} wanted to report something.'.format(ctx))

bot.add_cog(Reports(bot))


class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.permissions_in(ctx.channel).administrator

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Only administrator can configurate bot settings')

    @commands.group(case_sensitive=True, invoke_without_command=True, brief='Configurate bot for this server')
    async def config(self, ctx):
        await ctx.send_help(ctx.command)

    @config.command()
    async def enable(self, ctx, command_name):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        if await guild_config.switch_command(command_name, True):
            await ctx.send('Enabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def disable(self, ctx, command_name):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        if await guild_config.switch_command(command_name, False):
            await ctx.send('Disabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def whitelist(self, ctx, command_name, *whitelist_channels: discord.TextChannel):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        if await guild_config.command_filter(command_name, 'whitelist', whitelist_channels):
            await ctx.send('New whitelist for command `{0}`:\n{1}'.format(command_name, '\n'.join({channel.mention for channel in whitelist_channels})))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def blacklist(self, ctx, command_name, *blacklist_channels: discord.TextChannel):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        if await guild_config.command_filter(command_name, 'blacklist', blacklist_channels):
            await ctx.send('New whitelist for command `{0}`:\n{1}'.format(command_name, '\n'.join({channel.mention for channel in blacklist_channels})))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def welcome_channel(self, ctx, welcome_channel: discord.TextChannel):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        await guild_config.set_messages('welcome', welcome_channel.id)
        await ctx.send('Welcome channel is set to {0.mention}'.format(welcome_channel))

    @config.command()
    async def log_channel(self, ctx, log_channel: discord.TextChannel):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        await guild_config.set_messages('log', log_channel.id)
        await ctx.send('Log channel is set to {0.mention}'.format(log_channel))

    @config.command()
    async def enable_welcome(self, ctx):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        await guild_config.switch_messages('welcome', True)
        await ctx.send('Welcome messages enabled')

    @config.command()
    async def disable_welcome(self, ctx):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        await guild_config.switch_messages('welcome', True)
        await ctx.send('Welcome messages disabled')

    @config.command()
    async def enable_log(self, ctx):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        await guild_config.switch_messages('log', True)
        await ctx.send('Log messsages enabled.')

    @config.command()
    async def disable_log(self, ctx):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        await guild_config.switch_messages('log', False)
        await ctx.send('Log messsages disabled.')

    @config.command()
    async def default_roles(self, ctx, *roles: discord.Role):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        await guild_config.set_default_roles(roles)
        await ctx.send('List of default roles updated.')

    @config.command(hidden=True)
    async def reports_channel(self, ctx, channel: discord.TextChannel):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        await guild_config.set_messages('reports', channel.id)
        await ctx.send('Channel for report messages is set to {0.mention}'.format(channel))

    @config.group(name='list', case_sensitive=True, invoke_without_command=True)
    async def list_config(self, ctx):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        config_embed = discord.Embed(title='Config for server **{0.guild.name}**'.format(ctx))
        config_embed.add_field(name='***Default roles***', value='\n'.join({role.mention for role in guild_config.default_roles}), inline=False)
        config_embed.add_field(name='***Welcome messages***', value=guild_config.welcome_channel.mention if guild_config.raw_config['welcome_enabled'] else 'Disabled', inline=True)
        config_embed.add_field(name='***Log messages***', value=guild_config.log_channel.mention if guild_config.raw_config['log_enabled'] else 'Disabled')

        # A VERY long line
        config_commands_embed = '\n'.join([('**`'+command.name+'`**:\n'+((('Whitelisted in:\n'+'\n'.join(['<#'+str(whitelist_id)+'>' for whitelist_id in guild_config.raw_config['commands'][command.name]])) if guild_config.raw_config['commands'][command.name]['whitelist'] else (('Blacklisted in:\n'+'\n'.join(['<#'+str(blacklist_id)+'>' for blacklist_id in guild_config.raw_config['commands'][command.name]['blacklist']])) if guild_config.raw_config['commands'][command.name]['blacklist'] else 'Enabled')) if guild_config.raw_config['commands'][command.name]['enabled'] else 'Disabled')+'\n') for command in bot.commands])
        config_embed.add_field(name = '***Commands***', value = config_commands_embed, inline = False)
        await ctx.send(embed=config_embed)

    @list_config.command(name='raw')
    async def list_config_raw(self, ctx):
        guild_config = bot_config.GuildConfig(ctx.guild, bot_config)
        await ctx.send('```json\n'+guild_config.json_config()+'\n```')

bot.add_cog(Configuration(bot))


bot.run(TOKEN)

del TOKEN
