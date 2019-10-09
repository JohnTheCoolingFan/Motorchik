from discord.ext import commands


class Miscellaneous(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def github(self, ctx: commands.Context):
        await ctx.send('https://github.com/JohnTheCoolingFan/Motorchik')

    @commands.command()
    async def gitlab(self, ctx: commands.Context):
        await ctx.send('https://gitlab.com/JohnTheCoolingFan/Motorchik')

    @commands.command()
    async def source(self, ctx: commands.Context):
        await ctx.send('Choose one which you prefer:\nGitHub: https://github.com/JohnTheCoolingFan/Motorchik\nGitLab: https://gitlab.com/JohnTheCoolingFan/Motorchik')


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
