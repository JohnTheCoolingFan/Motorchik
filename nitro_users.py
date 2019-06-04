TOKEN = ''

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

    await bot.process_commands(message)

@bot.command()
async def nitrousers(ctx):
    result = []
    for member in ctx.guild.members:
        member_profile = await member.profile()
        if member_profile.premium:
            result.append({'name': member.name, 'id': member.id})

    resultfile = open('niro_members.json', 'w')
    resultfile.write(json.dumps(result, sort_keys = True, indent = 4))
    resultfile.close()

bot.run(TOKEN)
