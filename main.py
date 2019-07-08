#! /usr/bin/python3.7

# TODO: make role-level system and levelup/leveldown commands
# TODO: make experience system
# TODO: make config commands output changed data
# TODO: add a report system (report user or report message)
# TODO: add setting to report with emoji

from discord.ext import commands
import discord
import json
import random

tokenfile = open('token.txt', 'r')
TOKEN = tokenfile.read().rstrip()
tokenfile.close()

MOD_LIST = ['Placeable-off-grid', 'No Artillery Map Reveal', 'Random Factorio Things', 'Plutonium Energy', 'RealisticReactors Ingo']
DEFAULT_GUILD_CONFIG = {'name': '', 'welcome_channel_id': 0, 'welcome_enabled': True, 'log_channel_id': 0, 'log_enabled': True, 'report_channel_id': 0, 'default_roles': [], 'commands': {}}

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    print('Checking config...')
    await check_config()


class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.id in message.raw_mentions:
            await message.channel.send(random.choice(['Yeah?', 'What?', 'Yeah, I\'m here.', 'Did I missed something?', 'Yep', 'Nah', 'Uhm...']))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if bot_config[str(member.guild.id)]['welcome_enabled']:
            await member.guild.get_channel(bot_config[str(member.guild.id)]['welcome_channel_id']).send('Welcome, {0.mention}'.format(member))
        if bot_config[str(member.guild.id)]['default_roles']:
            await member.add_roles(*[member.guild.get_role(role_id) for role_id in bot_config[str(member.guild.id)]['default_roles']], reason='New member join.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if bot_config[str(member.guild.id)]['welcome_enabled']:
            await member.guild.get_channel(bot_config[str(member.guild.id)]['welcome_channel_id']).send('Goodbye, {0} (ID:{1})'.format(str(member), member.id))

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
        await ctx.guild.get_channel(bot_config[str(ctx.guild.id)]['reports_channel_id']).send('Well, `report` command is incomplete.\n{0.author.mention} wanted to report something.'.format(ctx))

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
        if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
            bot_config[str(ctx.guild.id)]['commands'][command_name]['enabled'] = True
            await write_config()
            await ctx.send('Enabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def disable(self, ctx, command_name):
        if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
            bot_config[str(ctx.guild.id)]['commands'][command_name]['enabled'] = False
            await write_config()
            await ctx.send('Disabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def whitelist(self, ctx, command_name, *whitelist_channels: discord.TextChannel):
        if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
            bot_config[str(ctx.guild.id)]['commands'][command_name]['whitelist'] = {channel.id for channel in whitelist_channels}
            await write_config()
            await ctx.send('Whitelist channel list for `{0}` command updated'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def blacklist(self, ctx, command_name, *blacklist_channels: discord.TextChannel):
        if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
            bot_config[str(ctx.guild.id)]['commands'][command_name]['blacklist'] = {channel.id for channel in blacklist_channels}
            await write_config()
            await ctx.send('Blacklist channel list for `{0}` command updated'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def welcome_channel(self, ctx, welcome_channel: discord.TextChannel):
        bot_config[str(ctx.guild.id)]['welcome_channel_id'] = welcome_channel.id
        await write_config()
        await ctx.send('Welcome channel is set to <#{0.id}>'.format(welcome_channel))

    @config.command()
    async def log_channel(self, ctx, log_channel: discord.TextChannel):
        bot_config[str(ctx.guild.id)]['log_channel_id'] = log_channel.id
        await write_config()
        await ctx.send('Log channel is set to <#{0.id}>'.format(log_channel))

    @config.command()
    async def enable_welcome(self, ctx):
        bot_config[str(ctx.guild.id)]['welcome_enabled'] = True
        await write_config()
        await ctx.send('Welcome messages enabled')

    @config.command()
    async def disable_welcome(self, ctx):
        bot_config[str(ctx.guild.id)]['welcome_enabled'] = False
        await write_config()
        await ctx.send('Welcome messages disabled')

    @config.command()
    async def enable_log(self, ctx):
        bot_config[str(ctx.guild.id)]['log_enabled'] = True
        await write_config()
        await ctx.send('Log messsages enabled.')

    @config.command()
    async def disable_log(self, ctx):
        bot_config[str(ctx.guild.id)]['log_enabled'] = False
        await write_config()
        await ctx.send('Log messsages disabled.')

    @config.command()
    async def default_roles(self, ctx, *roles: discord.Role):
        bot_config[str(ctx.guild.id)]['default_roles'] = {role.id for role in roles}
        await write_config()
        await ctx.send('List of default roles updated.')

    @config.command(hidden=True)
    async def reports_channel(self, ctx, channel: discord.TextChannel):
        bot_config[str(ctx.guild.id)]['reports_channel_id'] = channel.id
        await write_config()
        await ctx.send('Channel for report messages is set to <#{0.id}>'.format(channel))

    @config.group(name='list', case_sensitive=True, invoke_without_command=True)
    async def list_config(self, ctx):
        bot_guild_cfg = bot_config[str(ctx.guild.id)]
        bot_guild_com_cfg = bot_guild_cfg['commands']
        config_embed = discord.Embed(title='Config for server **{0.guild.name}**'.format(ctx))
        config_embed.add_field(name='***Default roles***', value='\n'.join(['<@&{0}>'.format(roleid) for roleid in bot_guild_cfg['default_roles']]), inline=False)
        config_embed.add_field(name='***Welcome messages***', value='<#{0}>'.format(bot_guild_cfg['welcome_channel_id']) if bot_guild_cfg['welcome_enabled'] else 'Disabled', inline=True)
        config_embed.add_field(name='***Log messages***', value='<#{0}>'.format(bot_guild_cfg['log_channel_id']) if bot_guild_cfg['log_enabled'] else 'Disabled')

        """
        config_embed.add_field(name = '***Commands***', value = 'Commands settings on this server', inline = False)
        for command in bot.commands:
            command_filters_state = ''
            command_filters = 'Not filtered by channel'
            command_brief = command.brief
            if not command_brief:
                command_brief = 'No brief description'
            if bot_guild_com_cfg[command.name]['enabled']:
                if bot_guild_com_cfg[command.name]['whitelist']:
                    command_filters_state = 'Whitelisted in:'
                    command_filters = '\n'.join({'<#'+str(whitelist_id)+'>' for whitelist_id in bot_guild_com_cfg[command.name]['whitelist']})
                elif bot_guild_com_cfg[command.name]['blacklist']:
                    command_filters_state = 'Blacklisted in:'
                    command_filters = '\n'.join({'<#'+str(blacklist_id)+'>' for blacklist_id in bot_guild_com_cfg[command.name]['blacklist']})
                else:
                    command_filters_state = 'Enabled'
            else:
                command_filters_state = 'Disabled'
            config_embed.add_field(name = '**`'+command.name+'`**', value = command_brief, inline = True)
            config_embed.add_field(name = '**'+command_filters_state+'**', value = command_filters, inline = False)
        """

        config_commands_embed = '\n'.join([('**`'+command.name+'`**:\n'+((('Whitelisted in:\n'+'\n'.join(['<#'+str(whitelist_id)+'>' for whitelist_id in bot_guild_com_cfg[command.name]['whitelist']])) if bot_guild_com_cfg[command.name]['whitelist'] else (('Blacklisted in:\n'+'\n'.join(['<#'+str(blacklist_id)+'>' for blacklist_id in bot_guild_com_cfg[command.name]['blacklist']])) if bot_guild_com_cfg[command.name]['blacklist'] else 'Enabled')) if bot_guild_com_cfg[command.name]['enabled'] else 'Disabled')+'\n') for command in bot.commands])
        config_embed.add_field(name = '***Commands***', value = config_commands_embed, inline = False)
        await ctx.send(embed=config_embed)

    @list_config.command(name='raw')
    async def list_config_raw(self, ctx):
        await ctx.send('```json\n{0}\n```'.format(json.dumps(bot_config[str(ctx.guild.id)], sort_keys=True, indent=4)))

bot.add_cog(Configuration(bot))


async def is_enabled(ctx):
    return bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['enabled']\
        and ctx.channel.id not in bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['blacklist']\
        and (ctx.channel.id in bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['whitelist']\
        or not bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['whitelist'])\
        or ctx.author.permissions_in(ctx.channel).administrator


# Config file load
config_file = open('config.json', 'r')
bot_config = json.loads(config_file.read())
config_file.close()


async def check_config():
    # Check for all guilds where bot is in are in config
    for guild in bot.guilds:
        if str(guild.id) not in bot_config.keys():
            print('Guild "{0.name}" ({0.id}) not found in config.'.format(guild))
            await add_guild_to_config(guild)

    # Check that all guild configs have entries for all commands
    for guild_id, guild_config in bot_config.items():
        for command in bot.commands:
            if command.name not in guild_config['commands'].keys():
                print('Config for command "%s" not found in config of guild "%s"' % (command.name, guild_config['name']+' (ID: '+str(guild_id)+')'))
                guild_config['commands'][command.name] = {'whitelist': [], 'blacklist': [], 'enabled': True}

    await write_config()
    print('Config check succesful')


async def write_config():
    config_file = open('config.json', 'w')
    config_file.write(json.dumps(bot_config, sort_keys=True, indent=4))
    config_file.close()


async def add_guild_to_config(guild):
    bot_config[str(guild.id)] = DEFAULT_GUILD_CONFIG
    bot_config[str(guild.id)]['name'] = guild.name
    bot_config[str(guild.id)]['welcome_channel_id'] = guild.text_channels[0].id
    bot_config[str(guild.id)]['log_channel_id'] = guild.text_channels[0].id


bot.run(TOKEN)

TOKEN = ''
