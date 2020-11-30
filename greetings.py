from discord.ext import commands, tasks
import discord
from guild_config import GuildConfig
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
        self.queue_checker.start()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_config = GuildConfig(member.guild)
        if guild_config.welcome_channel:
            await guild_config.welcome_channel.send('Welcome, {0.mention}'.format(member))
        if guild_config.default_roles:
            if member.guild.verification_level != discord.VerificationLevel.none:
                print("Putting user {} on queue".format(member.id))
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
        print('Checking queue. {} items'.format(len(self.queue)))
        queue_to_remove = []
        for queue_item in self.queue:
            if self.check_queued(queue_item.user):
                print('User {} is now valid for automatic role giving'.format(queue_item.user.id))
                await queue_item.user.add_roles(*queue_item.roles, reason='New member join')
                queue_to_remove.append(queue_item)
        for queue_item in queue_to_remove:
            print('Removing user {} from queue'.format(queue_item.user.id))
            self.queue.remove(queue_item)

    @staticmethod
    def check_queued(user: discord.Member):
        guild_vl = user.guild.verification_level
        mediumlevel = True
        highlevel = True
        if guild_vl >= discord.VerificationLevel.medium:
            mediumlevel = datetime.now() - user.created_at() > timedelta(minutes=5)
        if guild_vl >= discord.VerificationLevel.high:
            highlevel = datetime.now() - user.joined_at() > timedelta(minutes=10)
        return mediumlevel and highlevel

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
