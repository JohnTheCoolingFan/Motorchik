#! /usr/bin/python3

# TODO: make expandable InfoChannels system

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or('$$'), intents=discord.Intents.all())


@bot.listen()
async def on_guild_join(guild: discord.Guild):
    await bot.get_cog('GuildConfigCog').add_guild(guild)


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

bot.load_extension('bot_config')
bot.load_extension('mongo_client')
bot.load_extension('service_tools')
bot.load_extension('info_channels') # To be implemented, probably as a part of new guild config
bot.load_extension('server_configuration')
bot.load_extension('moderation')
bot.load_extension('greetings')
bot.load_extension('factorio')
bot.load_extension('fun_commands')
bot.load_extension('miscellaneous')
bot.load_extension('test_commands')
#bot.load_extension('user_configuration') # Not deleted completely, but disabled to be improved later

bot.run(bot.get_cog('BotConfig').token)
