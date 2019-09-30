from discord.ext import commands
import discord

class ServiceTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def say(self, ctx, channel:discord.TextChannel, message):
        await ctx.message.delete()
        await channel.send(message)

def setup(bot):
    bot.add_cog(ServiceTools(bot))
