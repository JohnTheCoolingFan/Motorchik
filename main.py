#! /usr/bin/python3.7

# TODO: make experience system
# TODO: make role-level system and levelup/leveldown commands

from discord.ext import commands
from botconfig import BotConfig

bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'))

bot_config = BotConfig(bot, 'config.json')


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    await bot_config.check()

bot.load_extension('greetings')
bot.load_extension('testcommands')
bot.load_extension('funcommands')
bot.load_extension('factorio')
bot.load_extension('moderation')
bot.load_extension('reports')
bot.load_extension('configuration')
bot.load_extension('miscellaneous')
bot.load_extension('servicetools')

with open('token.txt', 'r') as token_file:
    bot.run(token_file.read().rstrip())
