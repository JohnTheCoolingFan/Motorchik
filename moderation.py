import discord
from discord.ext import commands
from typing import Optional


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        print('Loading Moderation module...', end='')
        self.bot = bot
        self.guild_config_cog = bot.get_cog('GuildConfigCog')
        print(' Done')

    # TODO: message filters
    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=['clear', 'cl'],
                      description='Clear chat',
                      brief='Clear chat',
                      help='Deletes specified count of messages in this channel. Can be used only by members with messages managing permission.')
    async def clearchat(self, ctx: commands.Context, messages_count: int):
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=messages_count)
        await ctx.send('Deleted {} message(s)'.format(len(deleted)), delete_after=3)

    @commands.has_permissions(ban_members=True)
    @commands.command(description='Ban member', help='Ban specified member. Set delete_message_days to 0 to not delete any messages.')
    async def ban(self, ctx: commands.Context, member: discord.Member, reason: Optional[str], delete_message_days: int = 0):
        guild_config = await self.guild_config_cog.get_guild(ctx.guild)
        await member.ban(reason=reason, delete_message_days=delete_message_days)
        await ctx.send('Banned member '+str(member))
        if reason is None:
            reason = 'Reason not provided'
        else:
            reason = 'Reason: ' + reason
        log_channel = await guild_config.get_log_channel()
        if log_channel:
            await log_channel.send('Banned {0}\nBy: {1}\n{2}'.format(str(member), ctx.author.mention, reason))

    @commands.has_permissions(ban_members=True)
    @commands.command(aliases=['uban'], description='Unban user', help='Unban specified member.')
    async def unban(self, ctx: commands.Context, member: discord.Member, reason: str = 'Not provided'):
        guild_config = await self.guild_config_cog.get_guild(ctx.guild)
        await member.unban(reason=reason)
        await ctx.send('Unbanned member '+str(member))
        log_channel = await guild_config.get_log_channel()
        if log_channel:
            await log_channel.send('Unbanned {0}\nBy: {1}\nReason: {2}'.format(str(member), ctx.author.mention, reason))

    @commands.has_permissions(kick_members=True)
    @commands.command(description='Kick member', help='Kick specified member')
    async def kick(self, ctx: commands.Context, member: discord.Member, reason: str = 'Not provided'):
        guild_config = await self.guild_config_cog.get_guild(ctx.guild)
        await member.kick(reason=reason)
        await ctx.send('Kicked member '+str(member))
        log_channel = await guild_config.get_log_channel()
        if log_channel:
            await log_channel.send('Kicked {0}\nBy: {1}\nReason: {2}'.format(str(member), ctx.author.mention, reason))


def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))
