from discord.ext import commands
import discord

class ServiceTools(commands.Cog, name='Service Tools', command_attrs=dict(hidden=True)):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel is discord.DMChannel:
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
        if user.dm_channel is None:
            await user.create_dm()
            dm_channel = user.dm_channel
        await dm_channel.send(message)

def setup(bot: commands.Bot):
    bot.add_cog(ServiceTools(bot))
