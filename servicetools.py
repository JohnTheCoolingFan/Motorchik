from discord.ext import commands
#import discord

class ServiceTools(commands.Cog, name='Service Tools', command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def say(self, ctx, channel_id: int, message):
        await ctx.message.delete()
        await self.bot.get_channel(channel_id).send(message)

def setup(bot):
    bot.add_cog(ServiceTools(bot))
