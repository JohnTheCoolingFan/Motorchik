#! /usr/bin/python3

# TODO: make expandable InfoChannels system
# TODO: Slash commands.

import discord
from discord.ext import commands
import argparse
import motorchik_setup

argparser = argparse.ArgumentParser(description='Motorchik, discord bot with extensive per-guild configuration directly in discord chat.')

argparser.add_argument('-s', '--setup', action='store_true')
arguments = argparser.parse_args()

if arguments.s or arguments.setup:
    motorchik_setup.interactive_setup()

bot = commands.Bot(command_prefix=commands.when_mentioned_or('$$'), intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

# Fundamental bot extensions
bot.load_extension('bot_config')
bot.load_extension('mongo_client')
bot.load_extension('service_tools')
bot.load_extension('info_channels') # To be implemented, probably as a part of new guild config
# Commands for moderators ans server owners
bot.load_extension('server_configuration')
bot.load_extension('moderation')
# Other commands
bot.load_extension('greetings')
bot.load_extension('factorio')
bot.load_extension('fun_commands')
bot.load_extension('miscellaneous')
bot.load_extension('test_commands')
#bot.load_extension('user_configuration') # Not deleted completely, but disabled to be improved later

bot.run(bot.get_cog('BotConfig').token)
