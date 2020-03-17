from discord.ext import commands
import discord
from guild_config import GuildConfig
from user_config import UserConfig


class Greetings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_config = GuildConfig(member.guild)
        if guild_config.welcome_channel:
            await guild_config.welcome_channel.send('Welcome, {0.mention}'.format(member))
        if guild_config.default_roles:
            await member.add_roles(*guild_config.default_roles, reason='New member join.')

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_config = GuildConfig(member.guild)
        if guild_config.welcome_channel:
            await guild_config.welcome_channel.send('Goodbye, {0} (ID:{1})'.format(str(member), member.id))

    async def cog_before_invoke(self, ctx: commands.Context):
        if UserConfig.check(ctx.author):
            userconfig = UserConfig(ctx.author)
            userconfig.add_xp(1)

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
