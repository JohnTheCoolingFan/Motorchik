"""
Commands intended to be used only by bot owner
"""

import discord
from discord.ext import commands


class ServiceTools(commands.Cog, name='Service Tools'):
    def __init__(self, bot: commands.Bot):
        print('Loading Service Tools module...', end='')
        self.bot = bot
        print(' Done')

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            app_info = await self.bot.application_info()
            await app_info.owner.dm_channel.send('I have received a DM message from {}:'.format(str(message.author)))
            await app_info.owner.dm_channel.send(message.content)

    @commands.command()
    async def say(self, ctx: commands.Context, channel_id: int, message: str):
        await ctx.message.delete()
        await self.bot.get_channel(channel_id).send(message)

    @commands.command()
    async def say_dm(self, ctx: commands.Context, user_id: int, message: str):
        await ctx.message.delete()
        user = self.bot.get_user(user_id)
        dm_channel = user.dm_channel
        if dm_channel is None:
            await user.create_dm()
            dm_channel = user.dm_channel
        await dm_channel.send(message)


def setup(bot: commands.Bot):
    bot.add_cog(ServiceTools(bot))
