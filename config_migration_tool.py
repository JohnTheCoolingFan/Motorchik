#! /usr/bin/python3

import mariadb
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
            json.dump(config_data, config_file)
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

def migrate_config(bott: commands.Bot):
    for guild in bott.guilds:
        print('Processing guild {}'.format(guild.id))
        if exists('guilds/guild_{}.json'.format(guild.id)):
            with open('guild/guild_{}.json'.format(guild.id)) as guild_config_file:
                guild_config = json.load(guild_config_file)

            # Default roles
            if 'default_roles' in guild_config.keys() and guild_config['default_roles']:
                print('  Default roles')
                values = ''
                template = '(\{role_id\}, {guild_id}),'.format(guild_id=guild.id) # pylint: disable=W1303,W1401
                for role in guild_config['default_roles']:
                    values = values + template.format(role_id=role)
                values = values[0:-1]
                cur.execute('INSERT INTO default_roles(role_id, guild_id) VALUES {values}'.format(values=values))

            # Info channels
            if 'info_channels' in guild_config.keys() and guild_config['info_channels']:
                print('  Info Channels')
                # Log
                if 'log' in guild_config['info_channels'].keys() and guild_config['info_channels']['log']:
                    print('    Log')
                    channel_id = guild_config['info_channels']['log']['channels_id']
                    is_enabled = guild_config['info_channels']['log']['enabled']
                    # Instead of using "enabled" flag, we store log channel info only when it's needed.
                    if is_enabled:
                        cur.execute('INSERT INTO log_channels(guild_id, channel_id) VALUES ({guild_id}, {channel_id})'.format(guild_id=guild.id, channel_id=channel_id))
                # Welcome
                if 'welcome' in guild_config['info_channels'].keys() and guild_config['info_channels']['welcome']:
                    print('    Welcome')
                    channel_id = guild_config['info_channels']['welcome']['channels_id']
                    is_enabled = guild_config['info_channels']['welcome']['enabled']
                    # Instead of using "enabled" flag, we store welcome channel info only when it's needed.
                    if is_enabled:
                        cur.execute('INSERT INTO welcome_channels(guild_id, channel_id) VALUES ({guild_id}, {channel_id})'.format(guild_id=guild.id, channel_id=channel_id))
            # Here goes the thing I always feared of and that takes majority of json config, but still useless and broken
            # Commands (Command Filters)
            if 'commands' in guild_config.keys() and guild_config['commands']:
                print('  Command Filters')
                filtered_commands = {command_name: command_filter for command_name, command_filter in guild_config['commands'].items() if command_filter['blacklist'] or command_filter['whitelist'] or not command_filter['enabled']}
                values_cfs = ''
                values_restr = []
                print('    Command filter list type and ')
                for command_name, command_filter in filtered_commands.items():
                    is_enabled = command_filter['enabled']
                    if not is_enabled:
                        values_cfs = values_cfs + '({command_name}, {guild_id}, FALSE, FALSE),'.format(command_name=command_name, guild_id=guild.id)
                        print('      {} is not enabled.'.format(command_name))
                        continue
                    # False is blacklist, False is whitelist
                    list_type = bool(command_filter['whitelist'])
                    if list_type:
                        print('      {} has whitelist'.format(command_name))
                        restrict_list = command_filter['whitelist']
                    else:
                        restrict_list = command_filter['blacklist']
                        print('      {} has blacklist'.format(command_name))
                    values_restr.append((command_name, restrict_list))
                    values_cfs = values_cfs + '({command_name}, {guild_id}, TRUE, {list_type}),'.format(command_name=command_name, guild_id=guild.id, list_type='TRUE' if list_type else 'FALSE')
                values_cfs = values_cfs[0:-1]
                cur.execute('INSERT INTO command_filters(name, guild_id, is_enabled, list_type) VALUES {values}'.format(values=values_cfs))
                restr_lookup = dict()
                for command_name, restr_list in values_restr:
                    if command_name not in restr_lookup.keys():
                        cur.execute('SELECT cf_id FROM command_filters WHERE name=\'{}\' AND guild_id={}'.format(command_name, guild.id))
                        restr_lookup[command_name] = cur[0]
                    cf_id = restr_lookup[command_name]
                    cur.execute('INSERT INTO restrict_list(cf_id, channel_id) VALUES ?', tuple((cf_id, channel_id) for channel_id in restr_list))
        else:
            print('Config file for guild {} was not found'.format(guild.id))

bot = commands.Bot(command_prefix='$$')

@bot.event
async def on_ready():
    migrate_config(bot)
