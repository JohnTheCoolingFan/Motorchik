#! /usr/bin/python3.7

# TODO: make role-level system and levelup/leveldown commands
# TODO: make experience system
# TODO: make config commands output changed data
# TODO: add a report system (report user or report message)
# TODO: add setting to report with emoji

from discord.ext import commands
import discord
import json

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


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('<@{0}>'.format(bot.user.id)):
        await message.channel.send('What?')

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        pass
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send('Exception raised while executing command `{0.command.name}`:\n```\n{1}\n```'.format(ctx, error), delete_after=5)


@bot.event
async def on_member_join(member):
    if bot_config[str(member.guild.id)]['welcome_enabled']:
        await member.guild.get_channel(bot_config[str(member.guild.id)]['welcome_channel_id']).send('Welcome, {0.mention}'.format(member))
    if bot_config[str(member.guild.id)]['default_roles']:
        await member.add_roles(*[member.guild.get_role(role_id) for role_id in bot_config[str(member.guild.id)]['default_roles']], reason='Default roles given on member join.')


@bot.event
async def on_member_remove(member):
    if bot_config[str(member.guild.id)]['welcome_enabled']:
        await member.guild.get_channel(bot_config[str(member.guild.id)]['welcome_channel_id']).send('Goodbye, {0} (ID {1})'.format(str(member), member.id))


async def is_enabled(ctx):
    if bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['enabled']\
        and ctx.channel.id not in bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['blacklist']\
        and (ctx.channel.id in bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['whitelist']\
        or not bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['whitelist'])\
        or ctx.author.permissions_in(ctx.channel).administrator:
        return True
    else:
        await ctx.send('This command is disabled in this channel or on this server')

async def is_admin(ctx):
    if ctx.author.permissions_in(ctx.channel).administrator:
        return True
    else:
        await ctx.send('You are not allowed to use this command.\nOnly administrators can use this command.')


@bot.command(hidden=True, help='Returns text typed after $test')
@commands.check(is_enabled)
async def test(ctx, *, arg):
    await ctx.send(arg)

@bot.command(hidden=True, help='Returns passed arguments count and the arguments', aliases=['advtest', 'atest'])
@commands.check(is_enabled)
async def advanced_test(ctx, *args):
    await ctx.send('Passed {} argiments: {}'.format(len(args), ', '.join(args)))


@bot.command(hidden=True, description='\"Hello\" in English', brief='\"Hello\" in English', help='Returns \"Hello\" in English')
@commands.check(is_enabled)
async def hello(ctx):
    await ctx.send('Hello!')


@bot.command(hidden=True, aliases=['gutentag'], description='\"Hello\" in German', brief='\"Hello\" in German', help='Returns \"Hello\" in German')
@commands.check(is_enabled)
async def hello_german(ctx):
    await ctx.send('Guten tag')


@bot.command(hidden=True, aliases=['privet'], description='\"Hello\" in Russian', brief='\"Hello\" in Russian', help='Returns \"Hello\" in Russian')
@commands.check(is_enabled)
async def hello_russian(ctx):
    await ctx.send('Приветствую!')


@bot.command(hidden=True, help='tag')
@commands.check(is_enabled)
async def guten(ctx):
    await ctx.send('tag')


@bot.command(hidden=True, help='You spin me right round, baby, right round')
@commands.check(is_enabled)
async def spin(ctx):
    await ctx.send('https://www.youtube.com/watch?v=PGNiXGX2nLU')


@bot.command(hidden=True, aliases=['XcQ'], help='You\'ve got RICKROLLED, LUL')
@commands.check(is_enabled)
async def rickroll(ctx):
    await ctx.send('<https://www.youtube.com/watch?v=dQw4w9WgXcQ>')
    await ctx.send('<:kappa_jtcf:546748910765604875>')


@bot.command(aliases=['modstat'], description='Info about mods', brief='Info about mods', help='Prints a bunch of commands for uBot to display info about mods')
@commands.check(is_enabled)
async def mods_statistics(ctx):
    for modname in MOD_LIST:
        await ctx.send(content='>>{0}<<'.format(modname), delete_after=1)
    await ctx.message.delete()


@bot.command(hidden=True, help='pong')
@commands.check(is_enabled)
async def ping(ctx):
    await ctx.send('pong')


@bot.command(aliases=['clear'], description='Clear chat', brief='Clear chat', help='Deletes specified count of messages in this channel. Only for admins and moderators.')
@commands.check(is_enabled)
async def clearchat(ctx, arg: int):
    if ctx.author.permissions_in(ctx.channel).manage_messages:
        async for message in ctx.channel.history(limit=arg + 1):
            await message.delete()

@bot.command()
@commands.check(is_enabled)
async def report(ctx):
    await ctx.guild.get_channel(bot_config[str(ctx.guild.id)]['reports_channel_id']).send('Well, `report` command is incomplete.\n{0.author.mention} wanted to report something.'.format(ctx))


# Bot configuration commands
@bot.group(case_sensitive=True, invoke_without_command=True, brief='Configurate bot for this server')
async def config(ctx):
    pass


@config.command()
@commands.check(is_admin)
async def enable(ctx, command_name):
    if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
        bot_config[str(ctx.guild.id)]['commands'][command_name]['enabled'] = True
        await write_config()
        await ctx.send('Enabled `{0}` command'.format(command_name))
    else:
        await ctx.send('Command `{0}` not found'.format(command_name))


@config.command()
@commands.check(is_admin)
async def disable(ctx, command_name):
    if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
        bot_config[str(ctx.guild.id)]['commands'][command_name]['enabled'] = False
        await write_config()
        await ctx.send('Disabled `{0}` command'.format(command_name))
    else:
        await ctx.send('Command `{0}` not found'.format(command_name))


@config.command()
@commands.check(is_admin)
async def whitelist(ctx, command_name):
    if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
        bot_config[str(ctx.guild.id)]['commands'][command_name]['whitelist'] = list({channel.id for channel in ctx.message.channel_mentions})
        await write_config()
        await ctx.send('Whitelist channel list for `{0}` command updated'.format(command_name))
    else:
        await ctx.send('Command `{0}` not found'.format(command_name))


@config.command()
@commands.check(is_admin)
async def blacklist(ctx, command_name):
    if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
        bot_config[str(ctx.guild.id)]['commands'][command_name]['blacklist'] = list({channel.id for channel in ctx.message.channel_mentions})
        await write_config()
        await ctx.send('Blacklist channel list for `{0}` command updated'.format(command_name))
    else:
        await ctx.send('Command `{0}` not found'.format(command_name))


@config.command()
@commands.check(is_admin)
async def welcome_channel(ctx):
    if not len({channel.id for channel in ctx.message.channel_mentions}) > 1:
        bot_config[str(ctx.guild.id)]['welcome_channel_id'] = ctx.message.channel_mentions[0].id
        await write_config()
        await ctx.send('Welcome channel set to <#{0}>.'.format(bot_config[str(ctx.guild.id)]['welcome_channel_id']))
    else:
        await ctx.send('Too much channels provided. Please, provide only one channel.')


@config.command()
@commands.check(is_admin)
async def log_channel(ctx):
    if not len({channel.id for channel in ctx.message.channel_mentions}) > 1:
        bot_config[str(ctx.guild.id)]['log_channel_id'] = ctx.message.channel_mentions[0].id
        await write_config()
        await ctx.send('Log channel set to <#{0}>.'.format(bot_config[str(ctx.guild.id)]['log_channel_id']))
    else:
        await ctx.send('Too much channels provided. Please, provide only one channel.')


@config.command()
@commands.check(is_admin)
async def enable_welcome(ctx):
    bot_config[str(ctx.guild.id)]['welcome_enabled'] = True
    await write_config()
    await ctx.send('Welcome messsages in channel <#{0}> enabled.'.format(bot_config[str(ctx.guild.id)]['welcome_channel_id']))


@config.command()
@commands.check(is_admin)
async def disable_welcome(ctx):
    bot_config[str(ctx.guild.id)]['welcome_enabled'] = False
    await write_config()
    await ctx.send('Welcome messsages in channel <#{0}> disabled.'.format(bot_config[str(ctx.guild.id)]['welcome_channel_id']))


@config.command()
@commands.check(is_admin)
async def enable_log(ctx):
    bot_config[str(ctx.guild.id)]['log_enabled'] = True
    await write_config()
    await ctx.send('Log messsages in channel <#{0}> enabled.'.format(bot_config[str(ctx.guild.id)]['log_channel_id']))


@config.command()
@commands.check(is_admin)
async def disable_log(ctx):
    bot_config[str(ctx.guild.id)]['log_enabled'] = False
    await write_config()
    await ctx.send('Log messsages in channel <#{0}> disabled.'.format(bot_config[str(ctx.guild.id)]['log_channel_id']))


@config.command()
@commands.check(is_admin)
async def default_roles(ctx):
    bot_config[str(ctx.guild.id)]["default_roles"] = list({role.id for role in ctx.message.role_mentions})
    await write_config()
    await ctx.send('List of default roles updated.')

@config.command()
@commands.check(is_admin)
async def reports_channel(ctx):
    bot_config[str(ctx.guild.id)]['reports_channel_id'] = ctx.message.channel_mentions[0].id
    await write_config()
    await ctx.send('Channel for report messages is set to <#{0}>'.format(bot_config[str(ctx.guild.id)]['reports_channel_id']))


@config.group(name='list', case_sensitive=True, invoke_without_command=True)
@commands.check(is_admin)
async def list_config(ctx):
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
@commands.check(is_admin)
async def list_raw(ctx):
    await ctx.send('```json\n{0}\n```'.format(json.dumps(bot_config[str(ctx.guild.id)], sort_keys=True, indent=4)))


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
