from discord.ext import commands
import discord
import requests as req
from bs4 import BeautifulSoup
from dateutil import parser
from colorthief import ColorThief
from io import BytesIO
from user_config import UserConfig

MOD_LIST_UBOT = ['Placeable-off-grid', 'No Artillery Map Reveal', 'Random Factorio Things', 'Plutonium Energy', 'RealisticReactors Ingo']
MOD_LIST_MOTORCHIK = ['PlaceableOffGrid', 'NoArtilleryMapReveal', 'RandomFactorioThings', 'PlutoniumEnergy', 'RealisticReactors']

# TODO: make customizable mod-list, which will update automatically over time by editing messages
# TODO: this cog needs some reorganization...


class FactorioCog(commands.Cog, name='Factorio'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=['modstat'], description='Info about mods', brief='Info about mods', help='Prints a bunch of commands for uBot to display info about mods')
    async def mods_statistics(self, ctx: commands.Context, *mod_names: str):
        if UserConfig.check(ctx.author):
            userconfig = UserConfig(ctx.author)
            userconfig.add_xp(5)

        if mod_names:
            for modname in mod_names:
                await ctx.send('>>'+modname+'<<', delete_after=1)
        else:
            for modname in MOD_LIST_UBOT:
                await ctx.send(content='>>{0}<<'.format(modname), delete_after=1)
            await ctx.message.delete()

    @commands.command(aliases=['nmodstat'])
    async def new_mods_statistics(self, ctx: commands.Context, *, mod_name: str):
        if UserConfig.check(ctx.author):
            userconfig = UserConfig(ctx.author)
            userconfig.add_xp(15)

        request = req.get('https://mods.factorio.com/api/mods/'+mod_name)
        if request.status_code == 200:
            json_req = request.json()
            latest_release = sorted(json_req['releases'], key=lambda release: release['version'], reverse=True)[0]
            if json_req['thumbnail'] != '/assets/.thumb.png':
                thumb_color = discord.Color.from_rgb(*ColorThief(
                    BytesIO(req.get('https://mods-data.factorio.com' + json_req['thumbnail']).content)).get_color())
            else:
                thumb_color = discord.Color.from_rgb(47, 137, 197)
            embed = discord.Embed(title=json_req['title'], description=json_req['summary'], url='https://mods.factorio.com/mod/'+mod_name, timestamp=parser.isoparse(latest_release['released_at']), color=thumb_color)
            embed.set_footer(text='Latest update released at:')
            if json_req['thumbnail'] != '/assets/.thumb.png':
                embed.set_thumbnail(url='https://mods-data.factorio.com'+json_req['thumbnail'])
            embed.add_field(name='Game Version', value=latest_release['info_json']['factorio_version'])
            embed.add_field(name='Download', value='[From Official Mod Portal](https://mods.factorio.com{download_url})\n[From Factorio Launcher storage](https://factorio-launcher-mods.storage.googleapis.com/{mod_name}/{version}.zip)'.format(download_url=latest_release['download_url'], mod_name=mod_name, version=latest_release['version']))
            embed.add_field(name='Latest Version', value=latest_release['version'])
            embed.add_field(name='Downloaded', value=str(json_req['downloads_count'])+' times')
            embed.add_field(name='Author', value='[{owner}](https://mods.factorio.com/user/{owner})'.format(owner=json_req['owner']))
            await ctx.send(embed=embed)
        else:
            new_mod_name = self.find_mod(mod_name)
            if new_mod_name:
                await ctx.invoke(self.new_mods_statistics, mod_name=new_mod_name)
            else:
                embed = discord.Embed(title='Mod not found', description='Failed to find mod \'{}\''.format(mod_name), color=discord.Color.from_rgb(255, 10, 10))
                await ctx.send(embed=embed)

    async def get_mods_info(self, mod_names: list) -> list:
        result = []
        for mod_name in mod_names:
            request = req.get('https://mods.factorio.com/api/mods/'+mod_name)
            if request.status_code == 200:
                json_req = request.json()
                latest_release = sorted(json_req['releases'], key=lambda release: release['version'], reverse=True)[0]
                if json_req['thumbnail'] != '/assets/.thumb.png':
                    thumb_color = discord.Color.from_rgb(*ColorThief(BytesIO(req.get('https://mods-data.factorio.com'+json_req['thumbnail']).content)).get_color())
                    thumbnail_url = 'https://mods-data.factorio.com'+json_req['thumbnail']
                else:
                    thumb_color = discord.Color.from_rgb(47, 137, 197)
                    thumbnail_url = ''
                result.append(dict(title=json_req['title'], description=json_req['summary'], url='https://mods.factorio.com/'+mod_name,
                    timestamp=parser.isoparse(latest_release['released_at']), color=thumb_color, thumbnail_url=thumbnail_url, game_version=latest_release['info_json']['factorio_version'],
                    download_official='https://mods.factorio.com'+latest_release['download_url'], download_launcher='https://factorio-launcher-mods.storage.googleapis.com/{}/{}.zip'.format(
                        mod_name, latest_release['version']), latest_version=latest_release['version'], downloads_count=json_req['downloads_count'], author=json_req['owner']))
            else:
                new_mod_name = self.find_mod(mod_name)
                if new_mod_name:
                    result.append(*self.get_mods_info([new_mod_name]))
        return result

    @staticmethod
    def find_mod(mod_name: str) -> str:
        request = req.get('https://mods.factorio.com/query/'+mod_name.replace(' ', '%20'))
        if request.status_code == 200:
            soup = BeautifulSoup(request.text, 'html.parser')
            mod_card = soup.find('div', {'class': 'mod-card'})
            if mod_card:
                retrieved_mod_name = mod_card.a['href'].replace('/mod/', '')
                return retrieved_mod_name
            else:
                return ''
        else:
            return ''

    @commands.command()
    async def modlist(self, ctx: commands.Context):
        for mod_name in MOD_LIST_MOTORCHIK:
            await ctx.invoke(self.new_mods_statistics, mod_name=mod_name)
        await ctx.message.delete()


def setup(bot: commands.Bot):
    bot.add_cog(FactorioCog(bot))
