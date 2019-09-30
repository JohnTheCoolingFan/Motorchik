import discord
from discord.ext import commands
from botconfig import BotConfig

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_config = BotConfig(bot, 'config.json')

    @commands.command(aliases=['clear'], description='Clear chat', brief='Clear chat', help='Deletes specified count of messages in this channel. Can be used only by members with messages managing permission.')
    @commands.has_permissions(manage_messages=True)
    async def clearchat(self, ctx, messages_count: int):
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=messages_count)
        await ctx.send('Deleted {} message(s)'.format(len(deleted)), delete_after=3)

    @commands.has_permissions(ban_members=True)
    @commands.command(case_sensitive=False, description='Ban member')
    async def ban(self, ctx, member: discord.Member, reason):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        await member.ban(reason=reason, delete_message_days=0)
        await ctx.send('Banned member '+str(member))
        if guild_config.log_channel:
            await guild_config.log_channel.send('Banned {0}\nReason: {1}'.format(str(member), reason))

def setup(bot):
    bot.add_cog(Moderation(bot))
