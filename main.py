#! /usr/bin/python3.7
# TabNine::sem

# TODO: make role-level system and levelup/leveldown commands
# TODO: make experience system
# TODO: add a report system (report user or report message)
# TODO: add setting to report with emoji
# TODO: split code into a number of files

from discord.ext import commands
import discord
from botconfig import BotConfig

MOD_LIST = ['Placeable-off-grid', 'No Artillery Map Reveal', 'Random Factorio Things', 'Plutonium Energy', 'RealisticReactors Ingo']
DEFAULT_GUILD_CONFIG = {'name': '', 'welcome_channel_id': 0, 'welcome_enabled': True, 'log_channel_id': 0, 'log_enabled': True, 'reports_channel_id': 0, 'default_roles': [], 'commands': {}}

bot = commands.Bot(command_prefix='$')

bot_config = BotConfig(bot, 'config_new.json')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    await bot_config.check(bot)

bot.load_extension('greetings')
bot.load_extension('testcommands')

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

tokenfile = open('token.txt', 'r')
TOKEN = tokenfile.read().rstrip()
tokenfile.close()

bot.run(TOKEN)

del TOKEN
