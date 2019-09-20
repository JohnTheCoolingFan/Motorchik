from discord.ext import commands
import discord
from botconfig import BotConfig

from io import StringIO as strio

class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_config = BotConfig(bot, 'config.json')

    async def cog_check(self, ctx):
        return ctx.author.permissions_in(ctx.channel).administrator

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Only administrator can configurate bot settings')
        else:
            print(error)

    @commands.group(case_sensitive=True, invoke_without_command=True, brief='Configurate bot for this server')
    async def config(self, ctx):
        await ctx.send_help(ctx.command)

    @config.command()
    async def enable(self, ctx, command_name):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        if await guild_config.switch_command(command_name, True):
            await ctx.send('Enabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def disable(self, ctx, command_name):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        if await guild_config.switch_command(command_name, False):
            await ctx.send('Disabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def whitelist(self, ctx, command_name, *whitelist_channels: discord.TextChannel):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        if await guild_config.command_filter(command_name, 'whitelist', whitelist_channels):
            await ctx.send('New whitelist for command `{0}`:\n{1}'.format(command_name, '\n'.join({channel.mention for channel in whitelist_channels})))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def blacklist(self, ctx, command_name, *blacklist_channels: discord.TextChannel):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        if await guild_config.command_filter(command_name, 'blacklist', blacklist_channels):
            await ctx.send('New whitelist for command `{0}`:\n{1}'.format(command_name, '\n'.join({channel.mention for channel in blacklist_channels})))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def welcome_channel(self, ctx, welcome_channel: discord.TextChannel):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        await guild_config.set_messages('welcome', welcome_channel.id)
        await ctx.send('Welcome channel is set to {0.mention}'.format(welcome_channel))

    @config.command()
    async def log_channel(self, ctx, log_channel: discord.TextChannel):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        await guild_config.set_messages('log', log_channel.id)
        await ctx.send('Log channel is set to {0.mention}'.format(log_channel))

    @config.command()
    async def enable_welcome(self, ctx):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        await guild_config.switch_messages('welcome', True)
        await ctx.send('Welcome messages enabled')

    @config.command()
    async def disable_welcome(self, ctx):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        await guild_config.switch_messages('welcome', False)
        await ctx.send('Welcome messages disabled')

    @config.command()
    async def enable_log(self, ctx):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        await guild_config.switch_messages('log', True)
        await ctx.send('Log messsages enabled.')

    @config.command()
    async def disable_log(self, ctx):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        await guild_config.switch_messages('log', False)
        await ctx.send('Log messsages disabled.')

    @config.command()
    async def default_roles(self, ctx, *roles: discord.Role):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        await guild_config.set_default_roles(roles)
        await ctx.send('List of default roles updated.')

    @config.command(hidden=True)
    async def reports_channel(self, ctx, channel: discord.TextChannel):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        await guild_config.set_messages('reports', channel.id)
        await ctx.send('Channel for report messages is set to {0.mention}'.format(channel))

    @config.group(name='list', case_sensitive=True, invoke_without_command=True)
    async def list_config(self, ctx):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        config_embed = discord.Embed(title='Config for server **{0.guild.name}**'.format(ctx))
        config_embed.add_field(name='***Default roles***', value='\n'.join({role.mention for role in guild_config.default_roles}) if guild_config.default_roles else 'No default roles set', inline=False)
        config_embed.add_field(name='***Welcome messages***', value=guild_config.welcome_channel.mention if guild_config.welcome_channel else 'Disabled', inline=True)
        config_embed.add_field(name='***Log messages***', value=guild_config.log_channel.mention if guild_config.log_channel else 'Disabled')

        # A VERY long line
        config_commands_embed = '\n'.join([('**`'+command.name+'`**:\n'+((('Whitelisted in:\n'+'\n'.join(['<#'+str(whitelist_id)+'>' for whitelist_id in guild_config.raw_config['commands'][command.name]['whitelist']])) if guild_config.raw_config['commands'][command.name]['whitelist'] else (('Blacklisted in:\n'+'\n'.join(['<#'+str(blacklist_id)+'>' for blacklist_id in guild_config.raw_config['commands'][command.name]['blacklist']])) if guild_config.raw_config['commands'][command.name]['blacklist'] else 'Enabled')) if guild_config.raw_config['commands'][command.name]['enabled'] else 'Disabled')+'\n') for command in self.bot.commands])
        config_embed.add_field(name = '***Commands***', value = config_commands_embed, inline = False)
        await ctx.send(embed=config_embed)

    @list_config.command(name='raw', hidden=True)
    async def list_config_raw(self, ctx):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        await ctx.send(file=discord.File(strio(guild_config.json_config()), filename='GuildConfig'+str(guild_config.guild.id)+'.json'))

def setup(bot):
    bot.add_cog(Configuration(bot))
