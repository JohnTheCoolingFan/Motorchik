from discord.ext import commands
import discord
import requests as req
from bs4 import BeautifulSoup
from dateutil import parser
from colorthief import ColorThief
from io import BytesIO
from user_config import UserConfig
from typing import Iterable

MOD_LIST_MOTORCHIK = ['PlaceableOffGrid', 'NoArtilleryMapReveal', 'RandomFactorioThings', 'PlutoniumEnergy', 'RealisticReactors']


# TODO: make customizable mod-list, which will update automatically over time by editing messages


class FactorioCog(commands.Cog, name='Factorio'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=['modstat', 'ms'])
    async def mods_statistics(self, ctx: commands.Context, *mods_names):
        if UserConfig.check(ctx.author):
            userconfig = UserConfig(ctx.author)
            userconfig.add_xp(5 * len(mods_names))

        mods_data = await self.get_mods_info(mods_names)
        if mods_data:
            for mod_data in mods_data:
                await self.send_mod_embed(ctx, mod_data)
        else:
            embed = discord.Embed(title='Mod not found', description='Failed to find mods',
                                  color=discord.Color.from_rgb(255, 10, 10))
            await ctx.send(embed=embed)
    
    @staticmethod
    async def send_mod_embed(ctx: commands.Context, mod_data: dict):
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
        await ctx.send(embed=embed)

    async def get_mods_info(self, mod_names: Iterable) -> list:
        result = []
        for mod_name in mod_names:
            request = req.get('https://mods.factorio.com/api/mods/' + mod_name)
            if request.status_code == 200:
                json_req = request.json()
                latest_release = sorted(json_req['releases'], key=lambda release: release['version'], reverse=True)[0]
                if json_req['thumbnail'] != '/assets/.thumb.png':
                    thumb_color = discord.Color.from_rgb(*ColorThief(
                        BytesIO(req.get('https://mods-data.factorio.com' + json_req['thumbnail']).content)).get_color())
                    thumbnail_url = 'https://mods-data.factorio.com' + json_req['thumbnail']
                else:
                    thumb_color = discord.Color.from_rgb(47, 137, 197)
                    thumbnail_url = ''
                result.append(dict(title=json_req['title'], description=json_req['summary'],
                                   url='https://mods.factorio.com/mod/' + mod_name,
                                   timestamp=parser.isoparse(latest_release['released_at']), color=thumb_color,
                                   thumbnail_url=thumbnail_url,
                                   game_version=latest_release['info_json']['factorio_version'],
                                   download_official='https://mods.factorio.com' + latest_release['download_url'],
                                   download_launcher='https://factorio-launcher-mods.storage.googleapis.com/{}/{}.zip'.format(
                                       mod_name, latest_release['version']), latest_version=latest_release['version'],
                                   downloads_count=json_req['downloads_count'], author=json_req['owner']))
            else:
                new_mod_name = await self.find_mod(mod_name)
                if new_mod_name:
                    result.append(*await self.get_mods_info([new_mod_name]))
        return result

    @staticmethod
    async def find_mod(mod_name: str) -> str:
        request = req.get('https://mods.factorio.com/query/' + mod_name.replace(' ', '%20'))
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

    @commands.command(aliases=['ml'])
    async def modlist(self, ctx: commands.Context):
        await ctx.invoke(self.mods_statistics, *MOD_LIST_MOTORCHIK)
        await ctx.message.delete()


def setup(bot: commands.Bot):
    bot.add_cog(FactorioCog(bot))
