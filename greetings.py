from discord.ext import commands
import random
from main import bot_config

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.id in message.raw_mentions:
            await message.channel.send(random.choice(['Yeah?', 'What?', 'Yeah, I\'m here.', 'Did I missed something?', 'Yep', 'Nah', 'Uhm...']))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_config = bot_config.GuildConfig(member.guild, bot_config)
        if guild_config.raw_config['welcome_enabled']:
            await guild_config.welcome_channel.send('Welcome, {0.mention}'.format(member))
        if guild_config.raw_config['default_roles']:
            await member.add_roles(*guild_config.default_roles, reason='New member join.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_config = bot_config.GuildConfig(member.guild, bot_config)
        if guild_config.raw_config['welcome_enabled']:
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
