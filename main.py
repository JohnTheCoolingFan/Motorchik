tokenfile = open('token.txt', 'r')
TOKEN = tokenfile.read().rstrip()
tokenfile.close()

BOT_USER_ID = 551085000775172096
TEST_SERVER_ID = 574559408894377984
JTCF_SERVER_ID = 370167294439063564
JTCF_DEFAULT_ROLE = 527382415014887424
JTCF_WELCOME_CHANNEL = 525772525045809152
JTCF_MODSTAT_CHANNEL = 569108021238824991
JTCF_BOTFLOOD_CHANNEL = 574920316057419827
MOD_LIST = ['Random Factorio Things', 'Plutonium Energy', 'RealisticReactors Ingo', 'Placeable-off-grid', 'No Artillery Map Reveal']

import json
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix = '$')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('<@{0}>'.format(BOT_USER_ID)):
        await message.channel.send('What?')

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    if member.guild.id == JTCF_SERVER_ID:
        await member.add_roles(member.guild.get_role(JTCF_DEFAULT_ROLE))
        await member.guild.get_channel(JTCF_WELCOME_CHANNEL).send('Welcome, {0.mention}!'.format(member))

@bot.event
async def on_member_remove(member):
    if member.guild.id == JTCF_SERVER_ID:
        await member.guild.get_channel(JTCF_WELCOME_CHANNEL).send('Goodbye, {0.mention}!'.format(member))

@bot.command(hidden = True, help = 'Returns text typed after $test')
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command(description = '\"Hello\" in English', brief = '\"Hello\" in English', help = 'Returns \"Hello\" in English')
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command(aliases = ['gutentag'], description = '\"Hello\" in German', brief = '\"Hello\" in German', help = 'Returns \"Hello\" in German')
async def hello_german(ctx):
    await ctx.send('Guten tag')

@bot.command(aliases = ['privet'], description = '\"Hello\" in Russian', brief = '\"Hello\" in Russian', help = 'Returns \"Hello\" in Russian')
async def hello_russian(ctx):
    await ctx.send('Приветствую!')

@bot.command(hidden = True, help = 'tag')
async def guten(ctx):
    await ctx.send('tag')

@bot.command(hidden = True, help = 'You spin me right round, baby, right round')
async def spin(ctx):
    await ctx.send('https://www.youtube.com/watch?v=PGNiXGX2nLU')

@bot.command(hidden = True, aliases = ['XcQ'], help = 'You\'ve got RICKROLLED, LUL')
async def rickroll(ctx):
    await ctx.send('<https://www.youtube.com/watch?v=dQw4w9WgXcQ>')
    await ctx.send('<:kappa_jtcf:546748910765604875>')

@bot.command(aliases = ['modstat'], description = 'Info about mods', brief = 'Info about mods', help = 'Prints a bunch of commands for uBot to display info about mods')
async def mods_statistics(ctx):
    if ctx.guild.id == TEST_SERVER_ID or ctx.channel.id == JTCF_MODSTAT_CHANNEL or ctx.channel.id == JTCF_BOTFLOOD_CHANNEL:
        for modname in MOD_LIST:
            await ctx.send(content = '>>{0}<<'.format(modname), delete_after = 1)
        await ctx.message.delete()
    else:
        await ctx.send(content = '{0.author.mention}, This command cannot be used in this channel'.format(ctx), delete_after = 5)

@bot.command(hidden = True, help = 'pong')
async def ping(ctx):
    await ctx.send('pong')

@bot.command(name = 'f', help = 'F')
async def bigemojif(ctx):
    await ctx.send('** **\n:regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f:\n:regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f:\n:regional_indicator_f::regional_indicator_f:\n:regional_indicator_f::regional_indicator_f:\n:regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f:\n:regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f::regional_indicator_f:\n:regional_indicator_f::regional_indicator_f:\n:regional_indicator_f::regional_indicator_f:\n:regional_indicator_f::regional_indicator_f:\n:regional_indicator_f::regional_indicator_f:')

@bot.command(aliases = ['clear'], description = 'Clear chat', brief = 'Clear chat', help = 'Deletes specified count of messages in this channel. Only for admins and moderators.')
async def clearchat(ctx, arg: int):
    if ctx.author.permissions_in(ctx.channel).administrator or ctx.author.permissions_in(ctx.channel).manage_messages:
        async for message in ctx.channel.history(limit = arg + 1):
            await message.delete()

bot.run(TOKEN)
