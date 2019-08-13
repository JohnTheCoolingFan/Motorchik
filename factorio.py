from discord.ext import commands
MOD_LIST = ['Placeable-off-grid', 'No Artillery Map Reveal', 'Random Factorio Things', 'Plutonium Energy', 'RealisticReactors Ingo']

class FactorioCog(commands.Cog, name='Factorio'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['modstat'], description='Info about mods', brief='Info about mods', help='Prints a bunch of commands for uBot to display info about mods')
    async def mods_statistics(self, ctx):
        for modname in MOD_LIST:
            await ctx.send(content='>>{0}<<'.format(modname), delete_after=1)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(FactorioCog(bot))
