# Mod commands cog

import discord
from discord.ext import commands

class ModCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.kick(reason=reason)
            await ctx.send(f"Kicked: {member.mention}")
            print(f"Kicked: {member.mention}")
        except Exception as error:
            await ctx.send(f"Could not find user: {member}")
            print(f"Could not kick user: {member}: {error}")


    @commands.command(aliases=["ban"])
    @commands.has_permissions(ban_members=True)
    async def permban(self, ctx, member: discord.Member, *, reason=None, delete_message_days=1):
        await self.member.ban(reason=reason, delete_message_days=delete_message_days)
        print(f"{member} has been banned from the server. {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (self.user.name, self.user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"{user} has been unbanned")
                return

        await ctx.send("Could not find banned user with given name")
        return False

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)
        print(f"Removed {amount} messages from {ctx.channel.name}")

def setup(bot):
    bot.add_cog(ModCommands(bot))

