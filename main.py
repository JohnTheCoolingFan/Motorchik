#! /usr/bin/python3

# TODO: make expandable InfoChannels system

import discord
from discord.ext import commands
from guild_config import GuildConfig
import os

bot = commands.Bot(command_prefix=commands.when_mentioned_or('$$'), intents=discord.Intents.all())


@bot.listen()
async def on_guild_join(guild: discord.Guild):
    GuildConfig.create_guild_config(guild)


@bot.listen()
async def on_guild_remove(guild: discord.Guild):
    os.remove('guilds/guild_{}.json'.format(guild.id))


@bot.listen()
async def on_guild_update(guild_before: discord.Guild, guild_after: discord.Guild):
    # Update guild name
    if guild_after.name != guild_before.name:
        guild_config = GuildConfig(guild_after)
        guild_config.raw['name'] = guild_after.name
        guild_config.write()


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    await GuildConfig.check(bot)

bot.load_extension('bot_config')
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

with open('token.txt', 'r') as token_file:
    #bot.run(token_file.read().rstrip())
    bot.run(bot.get_cog('BotConfig').token)
