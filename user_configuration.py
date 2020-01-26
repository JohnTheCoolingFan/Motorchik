from discord.ext import commands
import discord
from user_config import UserConfig
from typing import Optional
from guild_config import GuildConfig


class UserConfiguration(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def userconfig(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @userconfig.command(brief='Change where and how to send notifications.', help='Change where and how to send notifications.\n\n\'private\': notifications are sent to user\'s DM.\n\'public\': notifications are sent to the same channel where action which invoked the notification was made (e.g. when level-up for sending a message). Notification will be deleted after 5 seconds.\n\'public-no-ping\': same as \'public\' but wothout mention\n\'disabled\': notifications are disabled.')
    async def notifications(self, ctx: commands.Context, new_notifications_setting: str):
        if UserConfig.check(ctx.author):
            if new_notifications_setting not in ['private', 'public', 'public-no-ping', 'disabled']:
                await ctx.send('{} wrong notifications setting:\'{}\''.format(ctx.author.mention, new_notifications_setting))
            else:
                user_config = UserConfig(ctx.author)
                user_config.notifications = new_notifications_setting
                await ctx.send('{} New notifications setting is \'{}\''.format(ctx.author.mention, new_notifications_setting))
        else:
            await ctx.send('{} you are currently not in bot\'s database. To add yourself, use `$userconfig setup` command.')

    @userconfig.command(brief='Choose which notifications to receive', help='Choose which notifications to receive.\n\n\'all\': receive all notifications\n\'guild-levels\': receive notifications about guild level-ups (and level-downs)\n\'bot-levels\': receive notifications about bot level-ups (and level-downs)')
    async def notification_categories(self, ctx: commands.Context, *new_notification_categories: str):
        if UserConfig.check(ctx.author):
            if set(new_notification_categories).issubset(['all', 'guild-levels', 'bot-levels']):
                user_config = UserConfig(ctx.author)
                user_config.notification_categories = new_notification_categories
                await ctx.send('{} New notification categories: {}'.format(ctx.author.mention, ', '.join(new_notification_categories)))
            else:
                await ctx.send('{} wrong notification categories: {}'.format(ctx.author.mention, ', '.join(new_notification_categories)))
        else:
            await ctx.send('{} you are currently not in bot\'s database. To add yourself, use `$userconfig setup` command.')

    @userconfig.command(brief='Add user to bot\'s database.', help='Add user to bot\'s database.')
    async def setup(self, ctx: commands.Context):
        if UserConfig.check(ctx.author):
            await ctx.send('{} you are already in bot\'s database'.format(ctx.author.mention))
        else:
            UserConfig.create_user_config(ctx.author)
            await ctx.send('Congratulations {} you are now in the bot\'s database!'.format(ctx.author.mention))

    @commands.command(brief='Info about user')
    async def userinfo(self, ctx: commands.Context, member: Optional[discord.Member]):
        if member is None:
            member = ctx.author
        guild_config = GuildConfig(ctx.guild)
        member_xp = guild_config.get_xp(member)
        await ctx.send('{member.mention} xp is {member_xp}'.format(member=member, member_xp=member_xp))


def setup(bot: commands.Bot):
    bot.add_cog(UserConfiguration(bot))
