import discord
from discord.ext import commands
from guild_config import GuildConfig


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    # TODO: add on_member_ban listener
    # TODO: move these listeners to InfoChannels

    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=['clear', 'cl'], description='Clear chat', brief='Clear chat', help='Deletes specified count of messages in this channel. Can be used only by members with messages managing permission.')
    async def clearchat(self, ctx: commands.Context, messages_count: int):
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=messages_count)
        await ctx.send('Deleted {} message(s)'.format(len(deleted)), delete_after=3)

    @commands.has_permissions(ban_members=True)
    @commands.command(case_sensitive=False, description='Ban member', help='Ban specified member. Set delete_message_days to 0 to not delete any messages.')
    async def ban(self, ctx: commands.Context, member: discord.Member, reason: str = 'Not provided', delete_message_days: int = 0):
        guild_config = GuildConfig(ctx.guild)
        await member.ban(reason=reason, delete_message_days=delete_message_days)
        await ctx.send('Banned member '+str(member))
        if guild_config.log_channel:
            await guild_config.log_channel.send('Banned {0}\nReason: {1}'.format(str(member), reason))


def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))
