#! /usr/bin/python3

import mariadb
from discord.ext import commands
from os.path import exists
import json
import sys

# 1. Read config, get bot token.
# 2. Look for config storing method. If "mysql" - Good to go.
# 3. If there's no info on how to connect to mysql, Ask the user.
# 4. Use the creds to connect to mysql.
# 5. Seek for database. If not specified, ask the name. If doesn't exist, create.
# 6. If db doesn't have required tables, create. Also recommended to check the format.
# 7. Ask the user or look for argument whether or not to migrate the config.
# 8. Migrate the json config if needed.
# 9. Write the bot config file info, if got any new.

with open('config_test.json') as config_file:
    config_data = json.load(config_file)

mysql_data = config_data['mysql']

try:
    conn = mariadb.connect(
        user=mysql_data['user'],
        password=mysql_data['password'],
        host=mysql_data['host'],
        database=mysql_data['database']
    )
except mariadb.Error as e:
    print(f"Error connecting: {e}")
    sys.exit(1)

cur = conn.cursor()

def migrate_config(bott: commands.Bot):
    for guild in bott.guilds:
        if exists('guilds/guild_{}.json'.format(guild.id)):
            with open('guild/guild_{}.json'.format(guild.id)) as guild_config_file:
                guild_config = json.load(guild_config_file)
            if guild_config['default_roles']:
                values = ''
                template = '(\{role_id\}, {guild_id}),'.format(guild_id=guild.id)
                for role in guild_config['default_roles']:
                    values = values + template.format(role_id=role)
                values = values[0:-1]
                cur.execute('INSERT INTO default_roles(role_id, guild_id) VALUES {values}'.format(values=values))
        else:
            print('Config file for guild {} was not found'.format(guild.id))

bot = commands.Bot(command_prefix='$$')

@bot.event
async def on_ready():
    migrate_config(bot)
