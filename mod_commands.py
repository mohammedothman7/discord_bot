# Mod commands cog

import discord
from discord.ext import commands
from database import db
from datetime import datetime, timedelta

banned_users_db = db["banned_users"]
collection = db['users']


async def mute(ctx, user, reason):
    role = discord.utils.get(ctx.guild.roles, name="Muted")  # retrieves muted role returns none if there isn't
    muted = discord.utils.get(ctx.guild.text_channels,
                             name="Muted")  # retrieves channel named muted returns none if there isn't
    if not role:  # checks if there is muted role
        try:  # creates muted role
            muted = await ctx.guild.create_role(name="Muted", reason="To use for muting")
            for channel in ctx.guild.channels:  # removes permission to view and send in the channels
                await channel.set_permissions(muted, send_messages=False,
                                              read_message_history=False,
                                              read_messages=False)
        except discord.Forbidden:
            return await ctx.send("I have no permissions to make a muted role")
        await user.add_roles(muted)  # adds newly created muted role
        await ctx.send(f"{user.mention} has been sent to muted for {reason}")
    else:
        await user.add_roles(role)  # adds already existing muted role
        await ctx.send(f"{user.mention} has been sent to muted for {reason}")

    try:
        collection.update({"_id": user.id}, {'$inc': {"Mutes": 1}})
        print(f"Incremented {user.name} Mutes")
    except Exception:
        print("Failed to update user mutes to db")

    if not muted:  # checks if there is a channel named muted
        overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_message_history=False),
                      ctx.guild.me: discord.PermissionOverwrite(send_messages=True),
                      muted: discord.PermissionOverwrite(read_message_history=True)}  # permissions for the channel
        try:  # creates the channel and sends a message
            channel = await ctx.create_text_channel('Muted', overwrites=overwrites)
            await channel.send(
                "You have been muted!")
            # Updates the users muted count to db

        except discord.Forbidden:
            return await ctx.send("I have no permissions to make #Muted")
        except Exception:
            print("Failed to make Muted channel")



class ModCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class Sinner(commands.Converter):
        async def convert(self, ctx, argument):
            argument = await commands.MemberConverter().convert(ctx, argument)  # gets a member object
            permission = argument.guild_permissions.manage_messages  # can change into any permission
            if not permission:  # checks if user has the permission
                return argument  # returns user object
            else:
                raise commands.BadArgument(
                    "You cannot punish other staff members")  # tells user that target is a staff member

    # Checks if you have a muted role
    class Redeemed(commands.Converter):
        async def convert(self, ctx, argument):
            argument = await commands.MemberConverter().convert(ctx, argument)  # gets member object
            muted = discord.utils.get(ctx.guild.roles, name="Muted")  # gets role object
            if muted in argument.roles:  # checks if user has muted role
                return argument  # returns member object if there is muted role
            else:
                raise commands.BadArgument("The user was not muted.")  # self-explainatory




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
    async def mute(self, ctx, user: Sinner, reason=None):
        await mute(ctx, user, reason or "treason")  # uses the mute function

    @commands.command()
    async def unmute(self, ctx, user: Redeemed):
        await user.remove_roles(discord.utils.get(ctx.guild.roles, name="Muted")) # removes muted role
        await ctx.send(f"{user.mention} has been unmuted")

    @commands.command()
    async def block(self, ctx, user: Sinner = None):
        if not user:  # checks if there is user
            return await ctx.send("You must specify a user")

        await ctx.set_permissions(user, send_messages=False)  # sets permissions for current channel

    @commands.command()
    async def unblock(self, ctx, user: Sinner = None):
        if not user:  # checks if there is user
            return await ctx.send("You must specify a user")

        await ctx.set_permissions(user, send_messages=True)  # gives back send messages permissions


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_users_db(self, ctx):

        for guild in self.bot.guilds:
            for member in guild.members:
                print(f"{member.id}")
                if collection.find_one({ "_id": member.id}):
                    print("Already in db")
                else:
                    post = {"_id": member.id, "name": member.name, "Joined": datetime.datetime.today(), "Bans": 0,
                            "Warnings": 0, "Mutes": 0}
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

