from discord.ext import commands
import discord
from botconfig import BotConfig

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_config = BotConfig(bot, 'config.json')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_config = self.bot_config.GuildConfig(member.guild, self.bot_config)
        if guild_config.welcome_channel:
            await guild_config.welcome_channel.send('Welcome, {0.mention}'.format(member))
        if guild_config.default_roles:
            await member.add_roles(*guild_config.default_roles, reason='New member join.')

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_config = self.bot_config.GuildConfig(member.guild, self.bot_config)
        if guild_config.welcome_channel:
            await guild_config.welcome_channel.send('Goodbye, {0} (ID:{1})'.format(str(member), member.id))

    @commands.command(description='\"Hello\" in English', brief='\"Hello\" in English', help='Returns \"Hello\" in English')
    async def hello(self, ctx):
        await ctx.send('Hello!')

    @commands.command(aliases=['gutentag'], description='\"Hello\" in German', brief='\"Hello\" in German', help='Returns \"Hello\" in German')
    async def hello_german(self, ctx):
        await ctx.send('Guten tag')

    @commands.command(aliases=['privet'], description='\"Hello\" in Russian', brief='\"Hello\" in Russian', help='Returns \"Hello\" in Russian')
    async def hello_russian(self, ctx):
        await ctx.send('Приветствую!')

    @commands.command(hidden=True, help='tag')
    async def guten(self, ctx):
        await ctx.send('tag')

def setup(bot):
    bot.add_cog(Greetings(bot))
