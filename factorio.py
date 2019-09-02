# TODO: search mod portal for mod instead of taking only exact mod's name (not title)

from discord.ext import commands
import discord
import requests as req
from dateutil import parser
from colorthief import ColorThief
from io import BytesIO
MOD_LIST = ['Placeable-off-grid', 'No Artillery Map Reveal', 'Random Factorio Things', 'Plutonium Energy', 'RealisticReactors Ingo']
MOD_LIST_NEW = ['PlaceableOffGrid', 'NoArtilleryMapReveal', 'RandomFactorioThings', 'PlutoniumEnergy', 'RealisticReactors']

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
            json_req = request.json()
            latest_release = sorted(json_req['releases'], key=lambda release: release['version'], reverse=True)[0]
            thumb_color = discord.Color.from_rgb(*ColorThief(BytesIO(req.get('https://mods-data.factorio.com'+json_req['thumbnail']).content)).get_color()) if json_req['thumbnail'] != '/assets/.thumb.png' else discord.Color.from_rgb(47, 137, 197)
            embed = discord.Embed(title=json_req['title'], description=json_req['summary'], url='https://mods.factorio.com/mod/'+mod_name, timestamp=parser.isoparse(latest_release['released_at']), color=thumb_color)
            embed.set_footer(text='Latest update released at:')
            if json_req['thumbnail'] != '/assets/.thumb.png':
                embed.set_thumbnail(url='https://mods-data.factorio.com'+json_req['thumbnail'])
            embed.add_field(name='Game Version', value=latest_release['info_json']['factorio_version'])
            embed.add_field(name='Download', value='[From Official Mod Portal](https://mods.factorio.com'+latest_release['download_url']+')\n[From Factorio Launcher storage](https://factorio-launcher-mods.storage.googleapis.com/'+mod_name+'/'+latest_release['version']+'.zip)')
            embed.add_field(name='Latest Version', value=latest_release['version'])
            embed.add_field(name='Downloaded', value=str(json_req['downloads_count'])+' times')
            embed.add_field(name='Author', value='['+json_req['owner']+'](https://mods.factorio.com/user/'+json_req['owner']+')')
            await ctx.send(embed=embed)
        else:
            await ctx.send('MOD NOT FOUND')

    @commands.command()
    async def modlist(self, ctx):
        for mod_name in MOD_LIST_NEW:
            await ctx.invoke(self.new_mods_statistics, mod_name)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(FactorioCog(bot))
