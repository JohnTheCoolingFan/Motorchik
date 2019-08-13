#! /usr/bin/python3.7
# TabNine::sem

# TODO: make role-level system and levelup/leveldown commands
# TODO: make experience system
# TODO: add a report system (report user or report message)
# TODO: add setting to report with emoji
# TODO: split code into a number of files

from discord.ext import commands
#import discord
from botconfig import BotConfig

MOD_LIST = ['Placeable-off-grid', 'No Artillery Map Reveal', 'Random Factorio Things', 'Plutonium Energy', 'RealisticReactors Ingo']
DEFAULT_GUILD_CONFIG = {'name': '', 'welcome_channel_id': 0, 'welcome_enabled': True, 'log_channel_id': 0, 'log_enabled': True, 'reports_channel_id': 0, 'default_roles': [], 'commands': {}}

bot = commands.Bot(command_prefix='$')

bot_config = BotConfig(bot, 'config_new.json')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    await bot_config.check(bot)

bot.load_extension('greetings')
bot.load_extension('testcommands')
bot.load_extension('funcommandss')
bot.load_extension('factorio')
bot.load_extension('moderation')
bot.load_extension('reports')
bot.load_extension('configuration')

tokenfile = open('token.txt', 'r')
TOKEN = tokenfile.read().rstrip()
tokenfile.close()

bot.run(TOKEN)

del TOKEN
