from discord.ext import commands
from botconfig import BotConfig

class Reports(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.bot_config = BotConfig(bot, 'config_new.json')

    @commands.command()
    async def report(self, ctx):
        guild_config = self.bot_config.GuildConfig(ctx.guild, self.bot_config)
        await guild_config.reports_channel.send('Well, `report` command is incomplete.\n{0.author.mention} wanted to report something.'.format(ctx))

def setup(bot):
    bot.add_cog(Reports(bot))
