from discord.ext import commands
#import discord
from user_config import UserConfig

class UserConfiguration(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group()
    async def userconfig(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @userconfig.command()
    async def notifications(self, ctx: commands.Context, new_notifications_setting: str):
        if UserConfig.check(ctx.author):
            user_config = UserConfig(ctx.author)
            user_config.notifications = new_notifications_setting
            await ctx.send('{}, New notifications setting is \'{}\''.format(ctx.author.mention, new_notifications_setting))
        else:
            await ctx.send('{}, you are currently not in bot\'s database. To add yourself, use `$userconfig setup` command.')

    @userconfig.command()
    async def notification_categories(self, ctx: commands.Context, *new_notification_categories: str):
        if UserConfig.check(ctx.author):
            user_config = UserConfig(ctx.author)
            user_config.notification_categories = new_notification_categories
            await ctx.send('{}, New notification categories: {}'.format(ctx.author.mention, ', '.join(new_notification_categories)))
        else:
            await ctx.send('{}, you are currently not in bot\'s database. To add yourself, use `$userconfig setup` command.')

    @userconfig.command()
    async def setup(self, ctx: commands.Context):
        UserConfig.create_user_config(ctx.author)
        await ctx.send('Congratulations, {}, you are now in the bot\'s database!'.format(ctx.author.mention))
