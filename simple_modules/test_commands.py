"""
Commands for testing
"""

from discord.ext import commands


class TestCommands(commands.Cog, name='Test Commands', command_attrs=dict(hidden=True)):
    def __init__(self, bot: commands.Bot):
        print('Loading TestCommands module...', end='')
        self.bot = bot
        print(' Done')

    # TODO: https://discordpy.readthedocs.io/en/latest/api.html?highlight=messageable%20send#discord.abc.Messageable.send
    # allowed_mentions
    @commands.command(help='Returns text typed after $test')
    async def test(self, ctx, *, text: str):
        await ctx.send(text)

    @commands.command(help='Returns passed arguments count and the arguments', aliases=['advtest', 'atest'])
    async def advanced_test(self, ctx, *args):
        await ctx.send('Passed {} arguments: {}'.format(len(args), ', '.join(args)))


def setup(bot):
    bot.add_cog(TestCommands(bot))
