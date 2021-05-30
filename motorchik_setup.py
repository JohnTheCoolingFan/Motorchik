#! /usr/bin/python3

"""
Script/module to setup new Motorchik instance. Creates config.json.
"""

import argparse
import getpass
import json
import os.path as p

def get_argparser():
    argparser = argparse.ArgumentParser(description='Motorchik, discord bot with extensive per-guild configuration directly in discord chat.')
    argparser.add_argument('-s', '--setup', action='store_true')
    return argparser

def interactive_setup():
    print('Welcome to Motorchik interactive setup. It will ask for some parameters and create a new config file with entered parameters')
    config_data = dict()

    bot_token = getpass.getpass('Please enter bot\'s token (will not be echoed): ')
    config_data['token'] = bot_token

    log_channel_id = input('(Optional) Log channel id. Leave empty for none: ')
    if log_channel_id:
        try:
            config_data['log_channel'] = int(log_channel_id)
        except ValueError:
            config_data['log_channel'] = 0
    else:
        config_data['log_channel'] = 0

    attempt_input = True

    while attempt_input:
        print('''
              Config storage method is how guild and user settings are going to be stored. Enter the name or number.
               1. mongo (default)''')
        config_storage_method = input('Choice: ')

        if config_storage_method in ['1', 'mongo']:
            config_data['mongo'] = setup_mongo()
            attempt_input = False
        elif config_storage_method == '':
            print('Choosing default method: mongo')
            attempt_input = False
            config_data['mongo'] = setup_mongo()
        else:
            print('Invalid input')

    config_file_path = 'config.json'
    if p.exists(config_file_path):
        print('config.json already exists! New config will be written to config.json.new')
        config_file_path = 'config.json.new'

    with open(config_file_path, 'w') as config_file:
        json.dump(config_data, config_file)

    print('Finished setup. Motorchik is ready to start.')

def setup_mongo():
    print('You have chosen to store guild settings in MongoDB.')
    mongo_host = input('MongoDB host address: ')
    mongo_port = input('MongoDB server port (optional if specified in the host address): ')

    if mongo_port:
        try:
            mongo_port = int(mongo_port)
        except ValueError:
            mongo_port = ''

    print('For remote access, MongoDB requires to have a user and a password. If you plan to host MongoDB on the same machine as Motorchik, leave the next two empty.')
    mongo_username = input('MongoDB username: ')
    mongo_password = getpass.getpass('MongoDB user password (will not be echoed): ')

    print('Finished setting up MongoDB credentials')
    return {'host': mongo_host, 'port': mongo_port, 'username': mongo_username, 'password': mongo_password}

if __name__ == '__main__':
    interactive_setup()
