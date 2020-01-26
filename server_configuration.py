import discord
from discord.ext import commands
from guild_config import GuildConfig
from io import StringIO as StrIO


class ServerConfiguration(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return ctx.author.permissions_in(ctx.channel).administrator

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Only server administrator can configure bot settings')
        else:
            print(error)

    # Command filters configuration
    @commands.group(name='command')
    async def config_commands(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @config_commands.command()
    async def enable(self, ctx: commands.Context, command_name: str):
        guild_config = GuildConfig(ctx.guild)
        if guild_config.switch_command(command_name, True):
            await ctx.send('Enabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config_commands.command()
    async def disable(self, ctx: commands.Context, command_name: str):
        guild_config = GuildConfig(ctx.guild)
        if guild_config.switch_command(command_name, False):
            await ctx.send('Disabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config_commands.command()
    async def whitelist(self, ctx: commands.Context, command_name: str, *whitelist_channels: discord.TextChannel):
        guild_config = GuildConfig(ctx.guild)
        if guild_config.set_command_filter(command_name, 'whitelist', whitelist_channels):
            if whitelist_channels:
                await ctx.send('New whitelist for command `{0}`:\n{1}'.format(command_name, '\n'.join({channel.mention for channel in whitelist_channels})))
            else:
                await ctx.send('Whitelist for command `{}` is now empty'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    @config_commands.command()
    async def blacklist(self, ctx: commands.Context, command_name: str, *blacklist_channels: discord.TextChannel):
        guild_config = GuildConfig(ctx.guild)
        if guild_config.set_command_filter(command_name, 'blacklist', blacklist_channels):
            if blacklist_channels:
                await ctx.send('New blacklist for command `{0}`:\n{1}'.format(command_name, '\n'.join({channel.mention for channel in blacklist_channels})))
            else:
                await ctx.send('Blacklist for command `{}` is now empty'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))

    # Info channels configuration
    @commands.group(invoke_without_command=True)
    async def info_channels(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @info_channels.command(name='set')
    async def set_channel(self, ctx: commands.Context, channel_type: str, new_channel: discord.TextChannel):
        guild_config = GuildConfig(ctx.guild)
        if channel_type == 'welcome':
            guild_config.welcome_channel = new_channel
            await ctx.send('Info channel for welcome messages is now set to {}'.format(new_channel.mention))
        elif channel_type == 'log':
            guild_config.log_channel = new_channel
            await ctx.send('Info channel for log messages is now set to {}'.format(new_channel.mention))
        elif channel_type == 'reports':
            guild_config.reports_channel = new_channel
            await ctx.send('Info channel for reports messages is now set to {}'.format(new_channel.mention))
        else:
            await ctx.send('Info channel `{}` not found'.format(channel_type))

    @info_channels.command(name='enable')
    async def enable_info_channel(self, ctx: commands.Context, channel_type: str):
        guild_config = GuildConfig(ctx.guild)
        if guild_config.switch_info_channel(channel_type, True):
            await ctx.send('Enabled {} info channel'.format(channel_type))
        else:
            await ctx.send('Info channel `{}` not found'.format(channel_type))

    @info_channels.command(name='disable')
    async def disable_info_channel(self, ctx: commands.Context, channel_type: str):
        guild_config = GuildConfig(ctx.guild)
        if guild_config.switch_info_channel(channel_type, False):
            await ctx.send('Disabled {} info channel'.format(channel_type))
        else:
            await ctx.send('Info channel `{}` not found'.format(channel_type))

    # General configuration
    @commands.group(invoke_without_command=True, brief='Configure bot for this server')
    async def config(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @config.command()
    async def default_roles(self, ctx: commands.Context, *roles: discord.Role):
        guild_config = GuildConfig(ctx.guild)
        guild_config.default_roles = roles
        await ctx.send('List of default roles updated.')

    @config.group(name='list', case_sensitive=True, invoke_without_command=True)
    async def list_config(self, ctx: commands.Context):
        guild_config = GuildConfig(ctx.guild)
        config_embed = discord.Embed(title='Config for server **{0.guild.name}**'.format(ctx))
        config_embed.add_field(name='**Default roles**', value='\n'.join({role.mention for role in guild_config.default_roles}) if guild_config.default_roles else 'No default roles set', inline=False)
        config_embed.add_field(name='**Welcome messages**', value=guild_config.welcome_channel.mention if guild_config.welcome_channel else 'Disabled', inline=False)
        config_embed.add_field(name='**Log messages**', value=guild_config.log_channel.mention if guild_config.log_channel else 'Disabled', inline=False)

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
    bot.add_cog(ServerConfiguration(bot))
