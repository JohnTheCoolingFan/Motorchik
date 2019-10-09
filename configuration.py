from discord.ext import commands
import discord
from guild_config import GuildConfig

from io import StringIO as StrIO


# TODO: remake configuration to be more convenient and user-friendly

class Configuration(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return ctx.author.permissions_in(ctx.channel).administrator

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Only server administrator can configure bot settings')
        else:
            print(error)

    @commands.group(case_sensitive=True, invoke_without_command=True, brief='Configure bot for this server')
    async def config(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @config.command()
    async def enable(self, ctx: commands.Context, command_name: str):
        guild_config = GuildConfig(ctx.guild)
        if await guild_config.switch_command(command_name, True):
            await ctx.send('Enabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def disable(self, ctx: commands.Context, command_name: str):
        guild_config = GuildConfig(ctx.guild)
        if await guild_config.switch_command(command_name, False):
            await ctx.send('Disabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def whitelist(self, ctx: commands.Context, command_name: str, *whitelist_channels: discord.TextChannel):
        guild_config = GuildConfig(ctx.guild)
        if await guild_config.set_command_filter(command_name, 'whitelist', whitelist_channels):
            if whitelist_channels:
                await ctx.send('New whitelist for command `{0}`:\n{1}'.format(command_name, '\n'.join({channel.mention for channel in whitelist_channels})))
            else:
                await ctx.send('Whitelist for command `{}` is now empty'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def blacklist(self, ctx: commands.Context, command_name: str, *blacklist_channels: discord.TextChannel):
        guild_config = GuildConfig(ctx.guild)
        if await guild_config.set_command_filter(command_name, 'blacklist', blacklist_channels):
            if blacklist_channels:
                await ctx.send('New blacklist for command `{0}`:\n{1}'.format(command_name, '\n'.join({channel.mention for channel in blacklist_channels})))
            else:
                await ctx.send('Blacklist for command `{}` is now empty'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config.command()
    async def welcome_channel(self, ctx: commands.Context, welcome_channel: discord.TextChannel):
        guild_config = GuildConfig(ctx.guild)
        guild_config.welcome_channel = welcome_channel
        await ctx.send('Welcome channel is set to {0.mention}'.format(welcome_channel))

    @config.command()
    async def log_channel(self, ctx: commands.Context, log_channel: discord.TextChannel):
        guild_config = GuildConfig(ctx.guild)
        guild_config.log_channel = log_channel
        await ctx.send('Log channel is set to {0.mention}'.format(log_channel))

    @config.command(hidden=True)
    async def reports_channel(self, ctx: commands.Context, reports_channel: discord.TextChannel):
        guild_config = GuildConfig(ctx.guild)
        guild_config.reports_channel = reports_channel
        await ctx.send('Channel for report messages is set to {0.mention}'.format(reports_channel))

    @config.command()
    async def enable_welcome(self, ctx: commands.Context):
        guild_config = GuildConfig(ctx.guild)
        await guild_config.switch_info_channel('welcome', True)
        await ctx.send('Welcome messages enabled')

    @config.command()
    async def disable_welcome(self, ctx: commands.Context):
        guild_config = GuildConfig(ctx.guild)
        await guild_config.switch_info_channel('welcome', False)
        await ctx.send('Welcome messages disabled')

    @config.command()
    async def enable_log(self, ctx: commands.Context):
        guild_config = GuildConfig(ctx.guild)
        await guild_config.switch_info_channel('log', True)
        await ctx.send('Log messages enabled.')

    @config.command()
    async def disable_log(self, ctx: commands.Context):
        guild_config = GuildConfig(ctx.guild)
        await guild_config.switch_info_channel('log', False)
        await ctx.send('Log messages disabled.')

    @config.command()
    async def default_roles(self, ctx: commands.Context, *roles: discord.Role):
        guild_config = GuildConfig(ctx.guild)
        guild_config.default_roles = roles
        await ctx.send('List of default roles updated.')

    @config.group(name='list', case_sensitive=True, invoke_without_command=True)
    async def list_config(self, ctx: commands.Context):
        guild_config = GuildConfig(ctx.guild)
        config_embed = discord.Embed(title='Config for server **{0.guild.name}**'.format(ctx))
        config_embed.add_field(name='***Default roles***', value='\n'.join({role.mention for role in guild_config.default_roles}) if guild_config.default_roles else 'No default roles set', inline=False)
        config_embed.add_field(name='***Welcome messages***', value=guild_config.welcome_channel.mention if guild_config.welcome_channel else 'Disabled', inline=False)
        config_embed.add_field(name='***Log messages***', value=guild_config.log_channel.mention if guild_config.log_channel else 'Disabled', inline=False)

        # A VERY long line
        # config_commands_embed = '\n'.join([('**`'+command.name+'`**:\n'+((('Whitelisted in:\n'+'\n'.join(['<#'+str(whitelist_id)+'>' for whitelist_id in guild_config.raw['commands'][command.name]['whitelist']])) if guild_config.raw['commands'][command.name]['whitelist'] else (('Blacklisted in:\n'+'\n'.join(['<#'+str(blacklist_id)+'>' for blacklist_id in guild_config.raw['commands'][command.name]['blacklist']])) if guild_config.raw['commands'][command.name]['blacklist'] else 'Enabled')) if guild_config.raw['commands'][command.name]['enabled'] else 'Disabled')+'\n') for command in self.bot.commands])
        is_first = False
        for command in self.bot.commands:
            command_config_entry = guild_config.raw['commands'][command.name]
            if command_config_entry['enabled']:
                if command_config_entry['whitelist']:
                    command_filters_list = ['<#{}>'.format(channel_id) for channel_id in command_config_entry['whitelist']]
                    command_filters_text = '**Whitelisted in:**\n{}'.format('\n'.join(command_filters_list))
                elif command_config_entry['blacklist']:
                    command_filters_list = ['<#{}>'.format(channel_id) for channel_id in command_config_entry['blacklist']]
                    command_filters_text = '**Blacklisted in:**\n{}'.format('\n'.join(command_filters_list))
                else:
                    command_filters_text = '**Enabled**'
                config_embed.add_field(name='**`{}`**'.format(command.name), value=command_filters_text, inline=is_first)
            else:
                config_embed.add_field(name='**`{}`**'.format(command.name), value='**Disabled**', inline=is_first)
            is_first = True
        await ctx.send(embed=config_embed)

    @list_config.command(name='raw', hidden=True)
    async def list_config_raw(self, ctx: commands.Context):
        guild_config = GuildConfig(ctx.guild)
        await ctx.send(file=discord.File(StrIO(guild_config.json), filename='GuildConfig' + str(guild_config.guild.id) + '.json'))


def setup(bot: commands.Bot):
    bot.add_cog(Configuration(bot))
