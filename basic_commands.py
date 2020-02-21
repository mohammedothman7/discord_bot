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



def setup(bot):
    bot.add_cog(BasicCommands(bot))
