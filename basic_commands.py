# Basic commands cog

import discord
from discord.ext import commands


class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')

    @commands.command(aliases=["st","stat"])
    @commands.has_permissions(manage_guild=True)
    async def status(self, act: str, ):
        await self.bot.change_presence(activity=discord.Game(f"{act}"))

    @commands.command(aliases=["default", "def"])
    async def default_role(self, ctx, role: str):
        try:
            self.bot.default_role = role
            await ctx.send(f"Changed the default role on member join to {role}")
        except Exception:
            await ctx.send("Failed to change default role")

    @commands.command(aliases=["h", "?", "commands", "command"])
    async def help(self, ctx):
        author = ctx.message.author

        embed = discord.Embed(color= discord.Color.blue(), title='MoBot - Commands and description', description='A bot created by Moe#6306')


        embed.add_field(name='-ping', value='Returns Pong!', inline=False)
        embed.add_field(name='-join', value='Bot joins the voice channel', inline=False)
        embed.add_field(name='-leave', value='Bot leaves the voice channel', inline=False)
        embed.add_field(name='-play', value='Pass a YT url', inline=False)
        embed.add_field(name='-pause', value='Pauses music', inline=False)
        embed.add_field(name='-resume', value='Resumes music', inline=False)
        embed.add_field(name='-stop', value='Stops music and bot leaves voice channel', inline=False)
        embed.add_field(name='-queue', value='Adds a song to the playlist', inline=False)
        embed.add_field(name='-volume', value='Change the volume between 1 and 10', inline=False)
        embed.add_field(name='-skip', value='Skips the current song', inline=False)


        await ctx.send(author,embed=embed)



def setup(bot):
    bot.add_cog(BasicCommands(bot))
