"""
Commands about Factorio. Mostly just request data from mods.factorio.com
and make embed from it.
"""

import asyncio

import aiohttp
import discord
from bs4 import BeautifulSoup
from dateutil import parser
from discord.ext import commands
from natsort import natsorted

MOD_LIST_MOTORCHIK = ['artillery-spidertron', 'PlaceableOffGrid', 'NoArtilleryMapReveal', 'RandomFactorioThings', 'PlutoniumEnergy']

MODPORTAL_URL = 'https://mods.factorio.com'
LAUNCHER_URL = 'https://factorio-launcher-mods.storage.googleapis.com/{}/{}.zip'


# TODO: make customizable mod-list, which will update automatically over time by editing messages
#       InfoChannels milestone
# TODO: asynchronous and better thumb main color detection


class FactorioCog(commands.Cog, name='Factorio'):

    def __init__(self, bot: commands.Bot):
        print('Loading Factorio module...', end='')
        self.bot = bot
        self.__session = aiohttp.ClientSession()
        print(' Done')

    @commands.command(aliases=['modstat', 'ms'])
    async def mods_statistics(self, ctx: commands.Context, *mods_names):
        await asyncio.wait([asyncio.create_task(self.process_mod(ctx, mod_name)) for mod_name in mods_names])

    async def process_mod(self, ctx: commands.Context, mod_name: str):
        mod_data = await self.get_mod_info(mod_name)
        if mod_data['success']:
            embed = await self.construct_mod_embed(mod_data)
        else:
            embed = await self.failed_mod_embed(mod_data)
        await ctx.send(embed=embed)

    @staticmethod
    async def construct_mod_embed(mod_data: dict) -> discord.Embed:
        embed = discord.Embed(title=mod_data['title'], description=mod_data['description'], url=mod_data['url'],
                              timestamp=mod_data['timestamp'], color=mod_data['color'])
        embed.set_footer(text='Latest update was released at:')
        if mod_data['thumbnail_url']:
            embed.set_thumbnail(url=mod_data['thumbnail_url'])
        embed.add_field(name='Game version', value=mod_data['game_version'])
        embed.add_field(name='Download',
                        value='[From official mod portal]({})\n[From Factorio Launcher storage]({})'.format(
                            mod_data['download_official'], mod_data['download_launcher']))
        embed.add_field(name='Latest version', value=mod_data['latest_version'])
        embed.add_field(name='Downloaded', value=str(mod_data['downloads_count']) + ' times')
        embed.add_field(name='Author',
                        value='[{author}](https://mods.factorio.com/user/{author})'.format(author=mod_data['author']))
        return embed

    @staticmethod
    async def failed_mod_embed(mod_data: dict) -> discord.Embed:
        embed = discord.Embed(title='Mod not found', description='Failed to find {}'.format(mod_data['mod_name']), color=discord.Color.from_rgb(255, 10, 10))
        return embed

    async def get_mod_info(self, mod_name: str) -> dict:
        api_response = await self.__session.get(MODPORTAL_URL + '/api/mods/' + mod_name)
        if api_response.status == 200:
            json_req = await api_response.json()
            latest_release = natsorted(json_req['releases'], key=lambda release: release['version'], reverse=True)[0]
            if json_req['thumbnail'] != '/assets/.thumb.png':
                #thumb_color = discord.Color.from_rgb(*ColorThief(
                    #BytesIO(req.get('https://mods-data.factorio.com' + json_req['thumbnail']).content)).get_color())
                thumbnail_url = 'https://mods-data.factorio.com' + json_req['thumbnail']
            else:
                #thumb_color = discord.Color.from_rgb(47, 137, 197)
                thumbnail_url = ''
            thumb_color = discord.Color.from_rgb(47, 137, 197)
            return dict(title=json_req['title'],
                        description=json_req['summary'],
                        url=MODPORTAL_URL + '/mod/' + mod_name,
                        timestamp=parser.isoparse(latest_release['released_at']),
                        color=thumb_color,
                        thumbnail_url=thumbnail_url,
                        game_version=latest_release['info_json']['factorio_version'],
                        download_official=MODPORTAL_URL + latest_release['download_url'],
                        download_launcher=LAUNCHER_URL.format(mod_name,latest_release['version']),
                        latest_version=latest_release['version'],
                        downloads_count=json_req['downloads_count'],
                        author=json_req['owner'],
                        success=True,
                        mod_name=mod_name)
        else:
            new_mod_name = await self.find_mod(mod_name)
            if new_mod_name:
                return await self.get_mod_info(new_mod_name)
            else:
                return dict(success=False, mod_name=mod_name)

    async def find_mod(self, mod_name: str) -> str:
        search_response = await self.__session.get(MODPORTAL_URL + '/query/' + mod_name.replace(' ', '%20'))
        if search_response.status == 200:
            soup = BeautifulSoup(await search_response.text(), 'html.parser')
            mod_h2 = soup.find('h2', {'class': 'mb0'})
            if mod_h2:
                retrieved_mod_name = mod_h2.a['href'].replace('/mod/', '')
                return retrieved_mod_name
            else:
                return ''
        else:
            return ''

    @commands.command(aliases=['ml'])
    async def modlist(self, ctx: commands.Context):
        await ctx.message.delete()
        await ctx.invoke(self.mods_statistics, *MOD_LIST_MOTORCHIK)


def setup(bot: commands.Bot):
    bot.add_cog(FactorioCog(bot))
