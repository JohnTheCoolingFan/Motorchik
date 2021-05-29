from datetime import datetime, timedelta
from typing import List

import discord
from discord.ext import commands, tasks


class QueueItem:
    def __init__(self, user: discord.Member, roles: List[discord.Role]):
        self.user = user
        self.roles = roles

class Greetings(commands.Cog):
    queue: List[QueueItem]

    def __init__(self, bot: commands.Bot):
        print('Loading Greetings module...', end='')
        self.bot = bot
        self.guild_config_cog = bot.get_cog('GuildConfigCog')
        self.queue = []
        # Disabling pylint error because it analyses code improperly, which results in error being reported.
        self.queue_checker.start() # pylint: disable=no-member
        print(' Done')

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_config = await self.guild_config_cog.get_guild(member.guild)
        welcome_channel = await guild_config.get_welcome_channel()
        default_roles = await guild_config.get_default_roles()
        if welcome_channel:
            await welcome_channel.send('Welcome, {0.mention}'.format(member))
        if default_roles:
            if member.guild.verification_level != discord.VerificationLevel.none:
                print("Putting user {} on queue".format(member.id))
                self.queue.append(QueueItem(member, default_roles))
            else:
                await member.add_roles(*default_roles, reason='New member join.')

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_config = await self.guild_config_cog.get_guild(member.guild)
        welcome_channel = await guild_config.get_welcome_channel()
        if welcome_channel:
            await welcome_channel.send('Goodbye, {0} (ID:{1})'.format(str(member), member.id))

    @tasks.loop(seconds=10)
    async def queue_checker(self):
        if len(self.queue) > 0:
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
            mediumlevel = datetime.now() - user.created_at > timedelta(minutes=5)
        if guild_vl >= discord.VerificationLevel.high:
            highlevel = datetime.now() - user.joined_at > timedelta(minutes=10)
        return mediumlevel and highlevel

    @commands.command(description='\"Hello\" in English', brief='\"Hello\" in English', help='Returns \"Hello\" in English')
    async def hello(self, ctx: commands.Context):
        await ctx.send('Hello!')

    @commands.command(aliases=['privet'], description='\"Hello\" in Russian', brief='\"Hello\" in Russian', help='Returns \"Hello\" in Russian')
    async def hello_russian(self, ctx: commands.Context):
        await ctx.send('Приветствую!')

    @commands.command(aliases=['gutentag'], description='\"Hello\" in German', brief='\"Hello\" in German', help='Returns \"Hello\" in German')
    async def hello_german(self, ctx: commands.Context):
        await ctx.send('Guten tag')

    @commands.command(hidden=True, help='tag')
    async def guten(self, ctx: commands.Context):
        await ctx.send('tag')

    @commands.command(hidden=True, aliases=['youok?'])
    async def is_alive_eng(self, ctx: commands.Context):
        await ctx.send('yes')

    @commands.command(hidden=True, aliases=['живой?'])
    async def is_alive_rus(self, ctx: commands.Context):
        await ctx.send('Да')


def setup(bot):
    bot.add_cog(Greetings(bot))
