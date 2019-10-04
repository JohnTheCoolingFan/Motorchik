#! /usr/bin/python3.7

# TODO: make experience system
# TODO: make role-level system and levelup/leveldown commands

from discord.ext import commands
#import discord
from botconfig import BotConfig

DEFAULT_GUILD_CONFIG = {'name': '', 'welcome_channel_id': 0, 'welcome_enabled': True, 'log_channel_id': 0, 'log_enabled': True, 'reports_channel_id': 0, 'default_roles': [], 'commands': {}}

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

tokenfile = open('token.txt', 'r')
TOKEN = tokenfile.read().rstrip()
tokenfile.close()

bot.run(TOKEN)

del TOKEN
