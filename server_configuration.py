import sys
import traceback
from typing import Optional

import discord
from discord.ext import commands

from guild_config import (CommandDisability,
                                       CommandImmutableError,
                                       CommandNotFoundError,
                                       InfoChannelNotFoundError)


class ServerConfiguration(commands.Cog, name='Server Configuration'):
    def __init__(self, bot: commands.Bot):
        print('Loading Server Configuration module...', end='')
        self.bot = bot
        self.guild_config_cog = bot.get_cog('GuildConfigCog')
        print(' Done')

    async def cog_check(self, ctx: commands.Context) -> bool:
        return ctx.author.permissions_in(ctx.channel).administrator

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Only server administrator can configure bot settings')
        elif isinstance(error, CommandImmutableError):
            await ctx.send('This command can\'t be filtered')
        elif isinstance(error, CommandNotFoundError):
            await ctx.send('Command not found')
        elif isinstance(error, InfoChannelNotFoundError):
            await ctx.send('Info channel not found: {}'.format(error.ic_name))
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    # Command filters configuration
    @commands.group(name='command', invoke_without_command=True)
    async def config_commands(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @config_commands.command()
    async def enable(self, ctx: commands.Context, command_name: str):
        await self.guild_config_cog.update_command_filter(ctx.guild, command_name, enabled=True)
        await ctx.send('Successfully enabled command {}'.format(command_name))

    @config_commands.command()
    async def disable(self, ctx: commands.Context, command_name: str):
        await self.guild_config_cog.update_command_filter(ctx.guild, command_name, enabled=False)
        await ctx.send('Successfully disabled command {}'.format(command_name))

    @config_commands.command()
    async def whitelist(self, ctx: commands.Context, command_name: str, *whitelist_channels: discord.TextChannel):
        await self.guild_config_cog.update_command_filter(ctx.guild, command_name, new_channels=whitelist_channels, filter_type=CommandDisability.WHITELISTED)
        if not whitelist_channels:
            await ctx.send('Filter list set to empty\nFilter type set to "whitelist"')
        else:
            await ctx.send('Filter list set successfully ({} channels)\nFilter type set to "whitelist"'.format(len(whitelist_channels)))

    @config_commands.command()
    async def blacklist(self, ctx: commands.Context, command_name: str, *blacklist_channels: discord.TextChannel):
        await self.guild_config_cog.update_command_filter(ctx.guild, command_name, new_channels=blacklist_channels, filter_type=CommandDisability.BLACKLISTED)
        if not blacklist_channels:
            await ctx.send('Filter list set to empty\nFilter type set to "blacklist"')
        else:
            await ctx.send('Filter list set successfully ({} channels)\nFilter type set to "blacklist"'.format(len(blacklist_channels)))

    # Info channels configuration
    @commands.group(invoke_without_command=True, aliases=['ich'])
    async def info_channels(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @info_channels.command(name='set')
    async def set_channel(self, ctx: commands.Context, channel_type: str, new_channel: discord.TextChannel):
        guild_config = await self.guild_config_cog.get_config(ctx.guild)
        await guild_config.update_info_channel(channel_type, new_channel=new_channel)
        await ctx.send('Sucessfully set channel for "{}" info channel'.format(channel_type))

    @info_channels.command(name='enable')
    async def enable_info_channel(self, ctx: commands.Context, channel_type: str):
        guild_config = await self.guild_config_cog.get_config(ctx.guild)
        await guild_config.update_info_channel(channel_type, state=True)
        await ctx.send('Sucessfully enabled "{}" info channel'.format(channel_type))

    @info_channels.command(name='disable')
    async def disable_info_channel(self, ctx: commands.Context, channel_type: str):
        guild_config = await self.guild_config_cog.get_config(ctx.guild)
        await guild_config.update_info_channel(channel_type, state=False)
        await ctx.send('Sucessfully disabled "{}" info channel'.format(channel_type))

    # General configuration
    @commands.group(invoke_without_command=True, brief='Configure bot for this server')
    async def config(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @config.command()
    async def default_roles(self, ctx: commands.Context, *roles: Optional[discord.Role]):
        guild_config = await self.guild_config_cog.get_config(ctx.guild)
        await guild_config.set_default_roles(roles)
        await ctx.send('Default roles set successfully')

    # TODO: new config list
    # @config.group(name='list', case_sensitive=True, invoke_without_command=True)
    # async def list_config(self, ctx: commands.Context):
        # guild_config = GuildConfig(ctx.guild)
        # config_embed = discord.Embed(title='Config for server **{0.guild.name}**'.format(ctx))
        # config_embed.add_field(name='**Default roles**', value='\n'.join({role.mention for role in guild_config.default_roles}) if guild_config.default_roles else 'No default roles set', inline=False)
        # config_embed.add_field(name='**Welcome messages**', value=guild_config.welcome_channel.mention if guild_config.welcome_channel else 'Disabled', inline=False)
        # config_embed.add_field(name='**Log messages**', value=guild_config.log_channel.mention if guild_config.log_channel else 'Disabled', inline=False)

        # # A VERY long line
        # # config_commands_embed = '\n'.join([('**`'+command.name+'`**:\n'+((('Whitelisted in:\n'+'\n'.join(['<#'+str(whitelist_id)+'>' for whitelist_id in guild_config.raw['commands'][command.name]['whitelist']])) if guild_config.raw['commands'][command.name]['whitelist'] else (('Blacklisted in:\n'+'\n'.join(['<#'+str(blacklist_id)+'>' for blacklist_id in guild_config.raw['commands'][command.name]['blacklist']])) if guild_config.raw['commands'][command.name]['blacklist'] else 'Enabled')) if guild_config.raw['commands'][command.name]['enabled'] else 'Disabled')+'\n') for command in self.bot.commands])
        # is_first = False
        # for command in self.bot.commands:
            # command_config_entry = guild_config.raw['commands'][command.name]
            # if command_config_entry['enabled']:
                # if command_config_entry['whitelist']:
                    # command_filters_list = ['<#{}>'.format(channel_id) for channel_id in command_config_entry['whitelist']]
                    # command_filters_text = '**Whitelisted in:**\n{}'.format('\n'.join(command_filters_list))
                # elif command_config_entry['blacklist']:
                    # command_filters_list = ['<#{}>'.format(channel_id) for channel_id in command_config_entry['blacklist']]
                    # command_filters_text = '**Blacklisted in:**\n{}'.format('\n'.join(command_filters_list))
                # else:
                    # command_filters_text = '**Enabled**'
                # config_embed.add_field(name='**`{}`**'.format(command.name), value=command_filters_text, inline=is_first)
            # else:
                # config_embed.add_field(name='**`{}`**'.format(command.name), value='**Disabled**', inline=is_first)
            # is_first = True
        # await ctx.send(embed=config_embed)

    # @list_config.command(name='raw', hidden=True)
    # async def list_config_raw(self, ctx: commands.Context):
        # guild_config = GuildConfig(ctx.guild)
        # await ctx.send(file=discord.File(StrIO(guild_config.json), filename='GuildConfig' + str(guild_config.guild.id) + '.json'))


def setup(bot: commands.Bot):
    bot.add_cog(ServerConfiguration(bot))
