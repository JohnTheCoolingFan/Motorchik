import discord
from discord.ext import commands

bot = commands.Bot(command_prefix = '$')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.content.startswith('<@551085000775172096>'):
        await message.channel.send('What?')

    await bot.process_commands(message)

@bot.command(hidden = True)
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()
async def gutentag(ctx):
    await ctx.send('Guten tag')

@bot.command(hidden = True)
async def guten(ctx):
    await ctx.send('tag')

@bot.command(hidden = True)
async def spin(ctx):
    await ctx.send('https://www.youtube.com/watch?v=PGNiXGX2nLU')

@bot.command(name = 'rickrolling', hidden = True)
async def XcQ(ctx):
    await ctx.send('<https://www.youtube.com/watch?v=dQw4w9WgXcQ>')
    await ctx.send('<:kappa_jtcf:546748910765604875>')

@bot.command()
async def modstat(ctx):
    await ctx.send(content = '>>Random Factorio Things<<', delete_after = 1)
    await ctx.send(content = '>>Plutonium Energy<<', delete_after = 1)
    await ctx.send(content = '>>RealisticReactors Ingo<<', delete_after = 1)
    await ctx.send(content = '>>Placeable-off-grid<<', delete_after = 1)
    await ctx.message.delete()

@bot.command(hidden = True)
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def clearchat(ctx, arg: int):
    if ctx.author.permissions_in(ctx.channel).administrator or ctx.author.permissions_in(ctx.channel).manage_messages:
        async for message in ctx.channel.history(limit = arg + 1):
            await message.delete()

bot.run('token') # nah
