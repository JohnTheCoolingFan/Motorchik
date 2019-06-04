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

    if message.content.startswith('<@551085000775172096>'):
        await message.channel.send('What?')

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    if member.guild.id == 370167294439063564:
        await member.add_roles(member.guild.get_role(527382415014887424))
        await member.guild.get_channel(525772525045809152).send('Welcome, {0.mention}!'.format(member))

@bot.event
async def on_member_remove(member):
    if member.guild.id == 370167294439063564:
        await member.guild.get_channel(525772525045809152).send('Goodbye, {0.mention}!'.format(member))

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
    if ctx.guild.id == 574559408894377984 or ctx.channel.id == 569108021238824991 or ctx.channel.id == 574920316057419827:
        await ctx.send(content = '>>Random Factorio Things<<', delete_after = 1)
        await ctx.send(content = '>>Plutonium Energy<<', delete_after = 1)
        await ctx.send(content = '>>RealisticReactors Ingo<<', delete_after = 1)
        await ctx.send(content = '>>Placeable-off-grid<<', delete_after = 1)
        await ctx.message.delete()
    else:
        await ctx.send(content = '{0.author.mention}, This command cannot be used in this channel'.format(ctx), delete_after = 5)

@bot.command(hidden = True, help = 'pong')
async def ping(ctx):
    await ctx.send('pong')

@bot.command(aliases = ['clear'], description = 'Clear chat', brief = 'Clear chat', help = 'Deletes specified count of messages in this channel. Only for admins and moderators.')
async def clearchat(ctx, arg: int):
    if ctx.author.permissions_in(ctx.channel).administrator or ctx.author.permissions_in(ctx.channel).manage_messages:
        async for message in ctx.channel.history(limit = arg + 1):
            await message.delete()

bot.run('token') #nope
