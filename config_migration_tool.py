#! /usr/bin/python3

import mariadb
import discord
from discord.ext import commands
from os.path import exists
import json
import sys


config_file_name = 'config_test.json'

with open(config_file_name) as config_file:
    config_data = json.load(config_file)

if config_data['storage_method'] != 'mysql':
    response = input('Config storage method is set to {}. Set it to "mysql"? [Y/n] '.format(config_data['storage_method']))
    if response.lower() in ['', 'y', 'ye', 'yes']:
        config_data['storage_method'] = 'mysql'
        with open(config_file_name, 'w') as  config_file:
            json.dump(config_data, config_file, indent=4)
    else:
        print('Migration denied')
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

def migrate_config(guild: discord.Guild):
    print('Processing guild {}'.format(guild.id))
    if exists('guilds/guild_{}.json'.format(guild.id)):
        with open('guilds/guild_{}.json'.format(guild.id)) as guild_config_file:
            guild_config = json.load(guild_config_file)

        # Default roles
        if 'default_roles' in guild_config.keys() and guild_config['default_roles']:
            print('  Default roles')
            values = []
            for role in guild_config['default_roles']:
                values.append((role, guild.id))
            cur.executemany('INSERT INTO default_roles(role_id, guild_id) VALUES (?, ?)', values)

        # Info channels
        if 'info_channels' in guild_config.keys() and guild_config['info_channels']:
            print('  Info Channels')

            # Log
            if 'log' in guild_config['info_channels'].keys() and guild_config['info_channels']['log']:
                print('    Log')
                channel_id = guild_config['info_channels']['log']['channel_id']
                is_enabled = guild_config['info_channels']['log']['enabled']
                # Instead of using "enabled" flag, we store log channel info only when it's needed.
                if is_enabled:
                    cur.execute('INSERT INTO log_channels(guild_id, channel_id) VALUES (?, ?)', (guild.id, channel_id))

            # Welcome
            if 'welcome' in guild_config['info_channels'].keys() and guild_config['info_channels']['welcome']:
                print('    Welcome')
                channel_id = guild_config['info_channels']['welcome']['channel_id']
                is_enabled = guild_config['info_channels']['welcome']['enabled']
                # Instead of using "enabled" flag, we store welcome channel info only when it's needed.
                if is_enabled:
                    cur.execute('INSERT INTO welcome_channels(guild_id, channel_id) VALUES (?, ?)', (guild.id, channel_id))

        # Here goes the thing I always feared of and that takes majority of json config, but still useless and broken
        # Commands (Command Filters)
        if 'commands' in guild_config.keys() and guild_config['commands']:
            print('  Command Filters')
            values_cfs = []
            values_restr = []
            for command_name, command_filter in guild_config['commands'].items():
                print('DEB '+command_name)
                print(command_filter)
                if not ((command_filter['blacklist'] or command_filter['whitelist']) or not command_filter['enabled']):
                    continue
                print('      '+command_name)
                is_enabled = command_filter['enabled']
                if not is_enabled:
                    values_cfs.append((command_name, guild.id, False, False))
                    print('        {} is disabled.'.format(command_name))
                    continue
                # False is blacklist, False is whitelist
                list_type = bool(command_filter['whitelist'])
                if list_type:
                    print('        {} has whitelist'.format(command_name))
                    restrict_list = command_filter['whitelist']
                else:
                    restrict_list = command_filter['blacklist']
                    print('        {} has blacklist'.format(command_name))
                values_restr.append((command_name, restrict_list))
                values_cfs.append((command_name, guild.id, True, list_type))
            if values_cfs:
                cur.executemany('INSERT INTO command_filters(name, guild_id, is_enabled, list_type) VALUES (?, ?, ?, ?)', values_cfs)
                restr_lookup = dict()
                for command_name, restr_list in values_restr:
                    if command_name not in restr_lookup.keys():
                        cur.execute('SELECT cf_id FROM command_filters WHERE name=? AND guild_id=?', (command_name, guild.id))
                        restr_lookup[command_name] = cur.fetchone()[0]
                    cf_id = restr_lookup[command_name]
                    cur.executemany('INSERT INTO restrict_list(cf_id, channel_id) VALUES (?, ?)', [tuple([cf_id, channel_id]) for channel_id in restr_list])
    else:
        print('Config file for guild {} was not found'.format(guild.id))

bot = commands.Bot(command_prefix='$$')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        migrate_config(guild)
    try:
        conn.commit()
        conn.close()
        print('Finished')
    except Exception as e:
        print('Failed to commit: {}'.format(e))
    await bot.close()

bot.run(config_data['token'])
