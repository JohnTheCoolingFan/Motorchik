from discord.ext import commands
import datetime
import discord
import platform


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

    @commands.command()
    async def hostinfo(self, ctx: commands.Context):
        with open('/proc/uptime', 'r') as uptime_file:
            uptime_seconds = float(uptime_file.readline().split()[0])
            uptime_string = str(datetime.timedelta(seconds=uptime_seconds))
        embed = discord.Embed(title='Host info',
                              timestamp=datetime.datetime.now(tz=datetime.timezone(datetime.timedelta())),
                              colour=discord.Colour.from_rgb(47, 137, 197))
        embed.add_field(name='Hostname', value=platform.node() if platform.node() else 'Unknown')
        embed.add_field(name='Platform', value=platform.platform() if platform.platform() else 'Unknown')
        embed.add_field(name='Architecture', value=platform.machine() if platform.machine() else 'Unknown')
        embed.add_field(name='Host uptime', value=uptime_string)
        embed.add_field(name='Python implementation', value=platform.python_implementation() if platform.python_implementation() else 'Unknown')
        embed.add_field(name='Python version', value=platform.python_version() if platform.python_version() else 'Unknown')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
