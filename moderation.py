# TODO: Improve clear command

from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['clear'], description='Clear chat', brief='Clear chat', help='Deletes specified count of messages in this channel. Can be used only by members with messages managing permission.')
    @commands.has_permissions(manage_messages=True)
    async def clearchat(self, ctx, messages_count: int):
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=messages_count)
        await ctx.send('Deleted {} message(s)'.format(len(deleted)), delete_after=3)

def setup(bot):
    bot.add_cog(Moderation(bot))
