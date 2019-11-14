#from discord.ext import commands
import discord
import json
import os.path
from typing import List

class UserConfig:
    user: discord.User
    raw: dict

    def __init__(self, user: discord.User):
        self.user = user
        with open('user/user_{}.json'.format(user.id)) as user_config:
            self.raw = json.load(user_config)

    @property
    def notifications(self) -> str:
        return self.raw['notifications']

    @notifications.setter
    def notifications(self, new_notifications_setting: str):
        if new_notifications_setting in ['private', 'public', 'public-no-ping', 'disabled']:
            self.raw['notifications'] = new_notifications_setting
            self.write()
        else:
            print('Invalid notifications setting was passed: \'{setting}\', User: {user}'.format(setting=new_notifications_setting, user=str(self.user)))

    @property
    def notification_categories(self) -> List[str]:
        return self.raw['notification_categories']

    @notification_categories.setter
    def notification_categories(self, new_notification_categories: List[str]):
        if set(new_notification_categories).issubset(['all', 'guild-levels', 'bot-levels']):
            self.raw['notification_categories'] = new_notification_categories
            self.write()
        else:
            print('Invalid list of new notification setting was passed for user {user}'.format(user=str(self.user)))

    @property
    def xp(self) -> int:
        return self.raw['xp']

    def add_xp(self, xp_amount: int):
        self.raw['xp'] += xp_amount
        self.write()

    @classmethod
    def check(cls, user: discord.User):
        return os.path.exists('users/user_{}.json'.format(user.id))

    @classmethod
    def create_user_config(cls, user: discord.User):
        with open('users/user_{}.json'.format(user.id), 'w') as new_user_config_file:
            new_user_config = dict(name=user.name, discriminator=user.discriminator, notifications='private', notification_categories=['all'], xp=10)
            json.dump(new_user_config, new_user_config_file)

    def write(self):
        with open('users/user_{}'.format(self.user.id), 'w') as user_config:
            json.dump(self.raw, user_config, indent=4, sort_keys=True)
