# TODO: make reports

from discord.ext import commands
from guild_config import GuildConfig


class Reports(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def report(self, ctx):
        guild_config = GuildConfig(ctx.guild)
        await guild_config.reports_channel.send('Well, `report` command is incomplete.\n{0.author.mention} wanted to report something.'.format(ctx))


def setup(bot):
    bot.add_cog(Reports(bot))
