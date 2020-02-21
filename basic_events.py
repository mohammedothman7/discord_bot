# Events cog

import discord
from discord.ext import commands
from discord.utils import get


class BasicEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("Ready"))
        print("Bot is online")


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        print("The message " + str(message.message_id) + " has been deleted")


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        print("The message " + str(before.id) + " sent by " + str(
        before.author.name) + " has been edited by " + after.author.name)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member} has joined the server!")
        await member.send(f"{member.mention} Welcome to discord server. Please read and follow all the rules")
        role = get(member.guild.roles, name=get(self.default_role))
        await member.add_roles(role, reason=None, atomic=True)
        print(f"Gave {member.name} the {role} role")


def setup(bot):
    bot.add_cog(BasicEvents(bot))