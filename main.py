#! /usr/bin/python3

# TODO: Auto-Moderation system
# TODO: Configurable per-server messages
# TODO: warns and punishments system, with timed punishments
# TODO: make expandable InfoChannels system
# TODO: Slash commands.

import discord
from discord.ext import commands
import motorchik_setup

# Argument parsing
argparser = motorchik_setup.get_argparser()
arguments = argparser.parse_args()
if arguments.s or arguments.setup:
    motorchik_setup.interactive_setup()

# Bot initialization
bot = commands.Bot(command_prefix=commands.when_mentioned_or('$$'), intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

# Fundamental bot extensions
bot.load_extension('bot_config')
bot.load_extension('guild_config.mongo_client')
bot.load_extension('service_tools')
bot.load_extension('info_channels') # To be implemented, probably as a part of new guild config
bot.load_extension('greetings')

# Commands for moderators ans server owners
bot.load_extension('server_configuration')
bot.load_extension('moderation')

# Other commands
bot.load_extension('simple_modules.factorio')
bot.load_extension('simple_modules.fun_commands')
bot.load_extension('simple_modules.miscellaneous')
bot.load_extension('simple_modules.test_commands')

bot.run(bot.get_cog('BotConfig').token)
