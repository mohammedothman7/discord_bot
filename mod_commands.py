# Mod commands cog

import discord
from discord.ext import commands
from database import db
from datetime import datetime, timedelta

banned_users_db = db["banned_users"]
collection = db['users']

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
        await member.ban(reason=reason, delete_message_days=delete_message_days)
        print(f"{member} has been banned from the server. Reason = {reason}")
        await  ctx.send(f"{member} has been banned from the server.")
        post = {"_id": member.id, "name": member.name, "banned til": datetime.utcnow(), "reason": reason}
        banned_users_db.insert_one(post)


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                print(f"User ID {user.id}")
                banned_users_db.remove({"_id": user.id})
                await ctx.send(f"{user} has been unbanned")
                print(f"{user} has been unbanned")
                return


        await ctx.send("Could not find banned user with given name")
        return False

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)
        print(f"Removed {amount} messages from {ctx.channel.name}")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_users_db(self, ctx):

        for guild in self.bot.guilds:
            for member in guild.members:
                print(f"{member.id}")
                if collection.find_one({ "_id": member.id}):
                    print("Already in db")
                else:
                    post = {"_id": member.id, "name": member.name, "Joined": datetime.utcnow()}
                    collection.insert_one(post)
                    print(f"Added {member.name} to the db")


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def mod_help(self, ctx):
        author = ctx.message.author

        embed = discord.Embed(color=discord.Color.blue(), title='MoBot - Commands and description',
                              description='A bot created by Moe#6306')


        embed.add_field(name='-kick', value='{Player name} ', inline=False)
        embed.add_field(name='-ban', value='{Player name} ', inline=False)
        embed.add_field(name='-unban', value='{Player name} ', inline=False)
        embed.add_field(name='-clear', value='{Amount of lines to clear} ', inline=False)

        await ctx.send(author,embed=embed)









def setup(bot):
    bot.add_cog(ModCommands(bot))

