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

config_file_name = 'config_test.json'

with open(config_file_name) as config_file:
    config_data = json.load(config_file)

if config_data['storage_method'] != 'mysql':
    response = input('Config storage method is set to {}. Set it to "mysql"? [Y/n] '.format(config_data['storage_method']))
    if response.lower() in ['', 'y', 'ye', 'yes']:
        config_data['storage_method'] = 'mysql'
        with open(config_file_name, 'w') as  config_file:
            json.dump(config_data, config_file)
    else:
        print('No migration is needed.')
        sys.exit(1)

if 'mysql' in config_data.keys():
    mysql_data = config_data['mysql']
else:
    response = input('There\'s no database info in bot config. Do you want to add it? [Y/n] ')
    if response.lower() in ['', 'y', 'ye', 'yes']:
        host = input('MySQL server host: ')
        user = input('MySQL user: ')
        password = input('MySQL user password (will be echoed. Leave empty to add manually): ')
        database = input('MySQL database name: ')
        config_data['mysql'] = dict(host=host, user=user, password=password, database=database)
        with open(config_file_name, 'w') as config_file:
            json.dump(config_data, config_file)
        if not password:
            print('Password is empty. Please add it manually in the config file')
            sys.exit(1)
    else:
        print('Database info is required for migrating and bot\'s functioning with database. Please fill it in manually.')
        sys.exit(1)

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
