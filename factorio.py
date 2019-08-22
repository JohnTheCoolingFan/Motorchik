from discord.ext import commands
import requests as req
MOD_LIST = ['Placeable-off-grid', 'No Artillery Map Reveal', 'Random Factorio Things', 'Plutonium Energy', 'RealisticReactors Ingo']

class FactorioCog(commands.Cog, name='Factorio'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['modstat'], description='Info about mods', brief='Info about mods', help='Prints a bunch of commands for uBot to display info about mods')
    async def mods_statistics(self, ctx, *mod_names):
        if mod_names:
            for modname in mod_names:
                await ctx.send('>>'+modname+'<<', delete_after=1)
        else:
            for modname in MOD_LIST:
                await ctx.send(content='>>{0}<<'.format(modname), delete_after=1)
            await ctx.message.delete()

    @commands.command(aliases=['nmodstat'])
    async def new_mods_statistics(self, ctx, mod_name):
        request = req.get('https://mods.factorio.com/api/mods/'+mod_name)
        if request.status_code != 404:
            latest_release = sorted(request.json()['releases'], key=lambda release: release['version'], reverse=True)[0]
            await ctx.send('https://mods.factorio.com'+latest_release['download_url']+'\nOR\n'+'https://factorio-launcher-mods.storage.googleapis.com/'+mod_name+'/'+latest_release['version']+'.zip')
        else:
            await ctx.send('MOD NOT FOUND')

def setup(bot):
    bot.add_cog(FactorioCog(bot))
