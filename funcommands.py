from discord.ext import commands

class FunCommands(commands.Cog, name='Fun'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='You spin me right round, baby, right round')
    async def spin(self, ctx):
        await ctx.send('https://www.youtube.com/watch?v=PGNiXGX2nLU')

    @commands.command(aliases=['XcQ'], help='You\'ve got RICKROLLED, LUL')
    async def rickroll(self, ctx):
        await ctx.send('<https://www.youtube.com/watch?v=dQw4w9WgXcQ>')
        await ctx.send('<:kappa_jtcf:546748910765604875>')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

def setup(bot):
    bot.add_cog(FunCommands(bot))
