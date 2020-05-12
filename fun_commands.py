from discord.ext import commands
from user_config import UserConfig


class FunCommands(commands.Cog, name='Fun'):
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx: commands.Context):
        if UserConfig.check(ctx.author):
            userconfig = UserConfig(ctx.author)
            userconfig.add_xp(1)

    @commands.command(help='You spin me right round, baby, right round')
    async def spin(self, ctx):
        await ctx.send('https://www.youtube.com/watch?v=PGNiXGX2nLU')

    @commands.command(aliases=['XcQ'], help='A very interesting video you should consider watching')
    async def rickroll(self, ctx):
        await ctx.send('<https://www.youtube.com/watch?v=dQw4w9WgXcQ>')
        await ctx.send('<:kappa_jtcf:546748910765604875>')

    @commands.command()
    async def ping(self, ctx):
        pong = await ctx.send('pong!')
        time_diff = pong.created_at - ctx.message.created_at
        await pong.edit(content='pong!\nTime delta is {0} ms'.format(time_diff.microseconds/1000))

    @commands.command(hidden=True, aliases=['UDOD_COMMUNIST', 'UDOD', 'udod', 'УДОД_КОММУНИСТ', 'Удод_Коммунист', 'УДОД', 'Удод', 'удод'])
    async def udod_communist(self, ctx):
        await ctx.send('https://www.youtube.com/watch?v=YHR5_IvC8Gw')


def setup(bot):
    bot.add_cog(FunCommands(bot))
