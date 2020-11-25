from discord.ext import commands, tasks
import discord
from guild_config import GuildConfig
from user_config import UserConfig
from typing import List
from datetime import datetime, timedelta


class QueueItem:
    def __init__(self, user: discord.Member, roles: List[discord.Role]):
        self.user = user
        self.roles = roles

class Greetings(commands.Cog):
    queue: List[QueueItem]

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue = []

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_config = GuildConfig(member.guild)
        if guild_config.welcome_channel:
            await guild_config.welcome_channel.send('Welcome, {0.mention}'.format(member))
        if guild_config.default_roles:
            if not member.guild.verification_level.none:
                self.queue.append(QueueItem(member, guild_config.default_roles))
            else:
                await member.add_roles(*guild_config.default_roles, reason='New member join.')

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_config = GuildConfig(member.guild)
        if guild_config.welcome_channel:
            await guild_config.welcome_channel.send('Goodbye, {0} (ID:{1})'.format(str(member), member.id))

    @tasks.loop(seconds=10)
    async def queue_checker(self):
        queue_copy = self.queue.copy()
        queue_to_remove = []
        for queue_item in queue_copy:
            if self.check_queued(queue_item.item):
                await queue_item.user.add_roles(*queue_item.roles, reason='New member join')
                queue_to_remove.append(queue_item)
        for queue_item in queue_to_remove:
            queue_copy.remove(queue_item)
        self.queue = queue_copy.copy()
        del queue_copy
        del queue_to_remove

    async def check_queued(self, user: discord.Member):
        return (datetime.now() - user.joined_at() > timedelta(minutes=10)) and (datetime.now() - user.created_at() > timedelta(minutes=5))

    async def cog_before_invoke(self, ctx: commands.Context):
        if UserConfig.check(ctx.author):
            userconfig = UserConfig(ctx.author)
            userconfig.add_xp(1)

    @commands.command(description='\"Hello\" in English', brief='\"Hello\" in English', help='Returns \"Hello\" in English')
    async def hello(self, ctx: commands.Context):
        await ctx.send('Hello!')

    @commands.command(aliases=['gutentag'], description='\"Hello\" in German', brief='\"Hello\" in German', help='Returns \"Hello\" in German')
    async def hello_german(self, ctx: commands.Context):
        await ctx.send('Guten tag')

    @commands.command(aliases=['privet'], description='\"Hello\" in Russian', brief='\"Hello\" in Russian', help='Returns \"Hello\" in Russian')
    async def hello_russian(self, ctx: commands.Context):
        await ctx.send('Приветствую!')

    @commands.command(hidden=True, help='tag')
    async def guten(self, ctx: commands.Context):
        await ctx.send('tag')

    @commands.command(hidden=True, aliases=['живой?'])
    async def is_alive_rus(self, ctx: commands.Context):
        await ctx.send('Да')

    @commands.command(hidden=True, aliases=['youok?'])
    async def is_alive_eng(self, ctx: commands.Context):
        await ctx.send('yes')


def setup(bot):
    bot.add_cog(Greetings(bot))
