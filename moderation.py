from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['clear'], description='Clear chat', brief='Clear chat', help='Deletes specified count of messages in this channel. Can be used only by members with messages managing permission.')
    @commands.has_permissions(manage_messages=True)
    async def clearchat(self, ctx, message_count: int):
        await ctx.message.delete()
        async for message in ctx.channel.history(limit=message_count):
            await message.delete()

def setup(bot):
    bot.add_cog(Moderation(bot))
