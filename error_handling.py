# TODO: Delete this or make this useful

from discord.ext import commands


class ErrorHandling(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, error: commands.CommandError):
        print(error)


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandling(bot))
