from discord.ext import commands
class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def github(self, ctx):
        await ctx.send('https://github.com/JohnTheCoolingFan/Motorchik')

    @commands.command()
    async def gitlab(self, ctx):
        await ctx.send('https://gitlab.com/JohnTheCoolingFan/Motorchik')

def setup(bot):
    bot.add_cog(Miscellaneous(bot))
