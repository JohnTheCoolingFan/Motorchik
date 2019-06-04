import discord
#from discord.ext import comnmands

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$gutentag'):
        await message.channel.send('Guten tag')
        return

    if message.content.startswith('$guten'):
        await message.channel.send('tag')

    if message.content.startswith('<@551085000775172096>'):
        await message.channel.send('What?')

    if message.content.startswith('$cavej'):
        await message.channel.send('<@196160375593369600>')

    if message.content.startswith('$spin'):
        await message.channel.send('https://www.youtube.com/watch?v=PGNiXGX2nLU')

    if message.content.startswith('$XcQ'):
        await message.channel.send('<https://www.youtube.com/watch?v=dQw4w9WgXcQ>')
        await message.channel.send('<:kappa_jtcf:546748910765604875>')

    if message.content.startswith('$modstat'):
        await message.channel.send('>>Random Factorio Things<<')
        await message.channel.send('>>Plutonium Energy<<')
        await message.channel.send('>>RealisticReactors Ingo<<')
        await message.channel.send('>>Placeable-off-grid<<')


client.run('token') # Nein
