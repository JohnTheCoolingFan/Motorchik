# TODO: make role-level system and levelup/leveldown commands
# TODO: make experience system
# TODO: make config commands output changed data
# TODO: make config list command

from discord.ext import commands
import discord
import json
tokenfile = open('token.txt', 'r')
TOKEN = tokenfile.read().rstrip()
tokenfile.close()

MOD_LIST = ['Random Factorio Things', 'Plutonium Energy', 'RealisticReactors Ingo', 'Placeable-off-grid', 'No Artillery Map Reveal']
DEFAULT_GUILD_CONFIG = {'name': '', 'welcome_channel_id': 0, 'welcome_enabled': True, 'log_channel_id': 0, 'log_enabled': True, 'default_roles': [], 'commands': {}}


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
        await ctx.send('**{0.author.mention}, this command is disabled in this channel or on this server.**'.format(ctx), delete_after=5)
    else:
        await ctx.send('Exception raised while executing command `{0.command.name}`:\n```\n{1}\n```'.format(ctx, error), delete_after=5)


@bot.event
async def on_member_join(member):
    if bot_config[str(member.guild.id)]['welcome_enabled']:
        await member.guild.get_channel(bot_config[str(member.guild.id)]['welcome_channel_id']).send('Welcome, {0.mention}'.format(member))
    if len(bot_config[str(member.guild.id)]['default_roles']) != 0:
        await member.add_roles(*[member.guild.get_role(role_id) for role_id in bot_config[str(member.guild.id)]['default_roles']], reason='Default roles given on member join.')


@bot.event
async def on_member_remove(member):
    if bot_config[str(member.guild.id)]['welcome_enabled']:
        await member.guild.get_channel(bot_config[str(member.guild.id)]['welcome_channel_id']).send('Goodbye, {0.mention}!'.format(member))


async def is_enabled(ctx):
    return bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['enabled']\
        and ctx.channel.id not in bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['blacklist']\
        and (ctx.channel.id in bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['whitelist']
             or len(bot_config[str(ctx.guild.id)]['commands'][ctx.command.name]['whitelist']) == 0)


@bot.command(hidden=True, help='Returns text typed after $test')
@commands.check(is_enabled)
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command(description='\"Hello\" in English', brief='\"Hello\" in English', help='Returns \"Hello\" in English')
@commands.check(is_enabled)
async def hello(ctx):
    await ctx.send('Hello!')


@bot.command(aliases=['gutentag'], description='\"Hello\" in German', brief='\"Hello\" in German', help='Returns \"Hello\" in German')
@commands.check(is_enabled)
async def hello_german(ctx):
    await ctx.send('Guten tag')


@bot.command(aliases=['privet'], description='\"Hello\" in Russian', brief='\"Hello\" in Russian', help='Returns \"Hello\" in Russian')
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

# Bot configuration commands
@bot.group(case_sensitive=True, invoke_without_command=True)
async def config(ctx):
    return


@config.command()
async def enable(ctx, command_name):
    if ctx.author.permissions_in(ctx.channel).administrator:
        if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
            bot_config[str(ctx.guild.id)]['commands'][command_name]['enabled'] = True
            await write_config()
            await ctx.send('Enabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))
    else:
        await ctx.send('You are not allowed to use `config` command')


@config.command()
async def disable(ctx, command_name):
    if ctx.author.permissions_in(ctx.channel).administrator:
        if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
            bot_config[str(ctx.guild.id)]['commands'][command_name]['enabled'] = False
            await write_config()
            await ctx.send('Disabled `{0}` command'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))
    else:
        await ctx.send('You are not allowed to use `config` command')


@config.command()
async def whitelist(ctx, command_name):
    if ctx.author.permissions_in(ctx.channel).administrator:
        if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
            bot_config[str(ctx.guild.id)]['commands'][command_name]['whitelist'] = list(set([channel.id for channel in ctx.message.channel_mentions]))
            await write_config()
            await ctx.send('Whitelist channel list for `{0}` command updated'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))
    else:
        await ctx.send('You are not allowed to use `config` command')


@config.command()
async def blacklist(ctx, command_name):
    if ctx.author.permissions_in(ctx.channel).administrator:
        if bot_config[str(ctx.guild.id)]['commands'].get(command_name):
            bot_config[str(ctx.guild.id)]['commands'][command_name]['blacklist'] = list(set([channel.id for channel in ctx.message.channel_mentions]))
            await write_config()
            await ctx.send('Blacklist channel list for `{0}` command updated'.format(command_name))
        else:
            await ctx.send('Command `{0}` not found'.format(command_name))
    else:
        await ctx.send('You are not allowed to use `config` command')


@config.command()
async def welcome_channel(ctx):
    if ctx.author.permissions_in(ctx.channel).administrator:
        if not len(list(set([channel.id for channel in ctx.message.channel_mentions]))) > 1:
            bot_config[str(ctx.guild.id)]['welcome_channel_id'] = list(set([channel.id for channel in ctx.message.channel_mentions]))[0]
            await write_config()
            await ctx.send('Welcome channel set to <#{0}>.'.format(bot_config[str(ctx.guild.id)]['welcome_channel_id']))
        else:
            await ctx.send('Too much channels provided. Please, provide only one channel.')
    else:
        await ctx.send('You are not allowed to use `config` command')


@config.command()
async def log_channel(ctx):
    if ctx.author.permissions_in(ctx.channel).administrator:
        if not len(list(set([channel.id for channel in ctx.message.channel_mentions]))) > 1:
            bot_config[str(ctx.guild.id)]['log_channel_id'] = list(set([channel.id for channel in ctx.message.channel_mentions]))[0]
            await write_config()
            await ctx.send('Log channel set to <#{0}>.'.format(bot_config[str(ctx.guild.id)]['log_channel_id']))
        else:
            await ctx.send('Too much channels provided. Please, provide only one channel.')
    else:
        await ctx.send('You are not allowed to use `config` command')


@config.command()
async def enable_welcome(ctx):
    if ctx.author.permissions_in(ctx.channel).administrator:
        bot_config[str(ctx.guild.id)]['welcome_enabled'] = True
        await write_config()
        await ctx.send('Welcome messsages in channel <#{0}> enabled.'.format(bot_config[str(ctx.guild.id)]['welcome_channel_id']))
    else:
        await ctx.send('You are not allowed to use `config` command')


@config.command()
async def disable_welcome(ctx):
    if ctx.author.permissions_in(ctx.channel).administrator:
        bot_config[str(ctx.guild.id)]['welcome_enabled'] = False
        await write_config()
        await ctx.send('Welcome messsages in channel <#{0}> disabled.'.format(bot_config[str(ctx.guild.id)]['welcome_channel_id']))
    else:
        await ctx.send('You are not allowed to use `config` command')


@config.command()
async def enable_log(ctx):
    if ctx.author.permissions_in(ctx.channel).administrator:
        bot_config[str(ctx.guild.id)]['log_enabled'] = True
        await write_config()
        await ctx.send('Log messsages in channel <#{0}> enabled.'.format(bot_config[str(ctx.guild.id)]['log_channel_id']))
    else:
        await ctx.send('You are not allowed to use `config` command')


@config.command()
async def disable_log(ctx):
    if ctx.author.permissions_in(ctx.channel).administrator:
        bot_config[str(ctx.guild.id)]['log_enabled'] = False
        await write_config()
        await ctx.send('Log messsages in channel <#{0}> disabled.'.format(bot_config[str(ctx.guild.id)]['log_channel_id']))
    else:
        await ctx.send('You are not allowed to use `config` command')


@config.command()
async def default_roles(ctx):
    if ctx.author.permissions_in(ctx.channel).administrator:
        bot_config[str(ctx.guild.id)]["default_roles"] = list(set([role.id for role in ctx.message.role_mentions]))
        await write_config()
        await ctx.send('List of default roles updated.')
    else:
        await ctx.send('You are not allowed to use `config` command')


@config.group(name='list', case_sensitive=True, invoke_without_command=True)
async def list_config(ctx):
    bot_guild_cfg = bot_config[str(ctx.guild.id)]
    bot_guild_com_cfg = bot_guild_cfg['commands']
    config_embed = discord.Embed(title='Config for server **{0.guild.name}**'.format(ctx))
    config_embed.add_field(name='Default roles', value='\n'.join(['<@&{0}>'.format(roleid) for roleid in bot_guild_cfg['default_roles']]), inline=False)
    config_embed.add_field(name='Welcome messages', value='<#{0}>'.format(bot_guild_cfg['welcome_channel_id']) if bot_guild_cfg['welcome_enabled'] else 'Disabled', inline=True)
    config_embed.add_field(name='Log messages', value='<#{0}>'.format(bot_guild_cfg['log_channel_id']) if bot_guild_cfg['log_enabled'] else 'Disabled')
    config_commands_embed = '\n'.join([('**`'+command.name+'`**\n'+((('Whitelisted in:\n'+'\n'.join(['<#'+whitelist_id+'>' for whitelist_id in bot_guild_com_cfg[command.name]['whitelist']])) if len(bot_guild_com_cfg[command.name]['whitelist']) != 0 else (('Blacklisted in:\n'+'\n'.join(['<#'+blacklist_id+'>' for blacklist_id in bot_guild_com_cfg[command.name]['blacklist']])) if len(bot_guild_com_cfg[command.name]['blacklist']) != 0 else 'No channel filter')) if bot_guild_com_cfg[command.name]['enabled'] else 'Disabled')) for command in bot.commands])
    config_embed.add_field(name='Commands', value=config_commands_embed, inline=False)
    await ctx.send(embed=config_embed)


@list_config.command(name='raw')
async def list_raw(ctx):
    await ctx.send('```json\n{0}\n```'.format(json.dumps(bot_config[str(ctx.guild.id)], sort_keys=True, indent=4)))


# Config file load
config_file = open('config.json', 'r')
bot_config = json.loads(config_file.read())
config_file.close()


async def check_config():
    # Check for all guilds where bot is in are in config
    for guild in bot.guilds:
        if not str(guild.id) in bot_config.keys():
            print('Guild "{0.name}" ({0.id}) not found in config.'.format(guild))
            await add_guild_to_config(guild)

    # Check that all guild configs have entries for all commands
    for guild_id, guild_config in bot_config.items():
        for command in bot.commands:
            if command.name not in guild_config['commands'].keys():
                print('Config for command "%s" not found in config of guild "%s"' % (command.name, guild_config['name']))
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

TOKEN = None
