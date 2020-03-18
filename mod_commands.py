# Mod commands cog

import discord
from discord.ext import commands
from database import db
from datetime import datetime, timedelta
from bot_settings import mutes_til_ban, warnings_til_mute

logs = db["logs"]
banned_users_db = db['banned_users']
collection = db['users']
muted_users = db['muted_users']


async def mute(ctx, user, time, reason):
    role = discord.utils.get(ctx.guild.roles, name="Muted")  # retrieves muted role returns none if there isn't
    muted = discord.utils.get(ctx.guild.text_channels,
                              name="Muted")  # retrieves channel named muted returns none if there isn't

    punishment = await punishment_time(ctx, time)
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
    post = {"_id": user.id, "NAME": user.name + '#' + user.discriminator,
            "MUTED AT": datetime.utcnow(), "MUTED TIL": datetime.utcnow() + punishment}
    muted_users.insert_one(post)
    post = {"USER ID": user.id, "TYPE:": 'MUTED', "NAME": user.name + '#' + user.discriminator,
            "MUTED AT": datetime.utcnow(), "MUTED TIL": datetime.utcnow() + punishment}
    logs.insert_one(post)
    await increment_user_mutes(ctx, user)  # Updates the users muted count to db

    if not muted:  # checks if there is a channel named muted
        overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_message_history=False),
                      ctx.guild.me: discord.PermissionOverwrite(send_messages=True),
                      muted: discord.PermissionOverwrite(read_message_history=True)}  # permissions for the channel
        try:  # creates the channel and sends a message
            channel = await ctx.create_text_channel('Muted', overwrites=overwrites)
            await channel.send(
                "You have been muted!")

        except discord.Forbidden:
            return await ctx.send("I have no permissions to make #Muted")
        except Exception:
            print("Failed to make Muted channel")


async def increment_user_mutes(ctx, user):
    try:
        collection.update({"_id": user.id}, {'$inc': {"Mutes": 1}})
        print(f"Incremented {user.name} Mutes")
        await check_user_mutes(ctx, user)
    except Exception as error:
        print(f"Failed to update user mutes to db: {error}")


async def check_user_mutes(ctx, user):
    mutes = collection.find_one({"_id": user.id})['Mutes']
    print(f"Mutes {mutes}")

    if mutes == 0:
        return
    elif mutes % mutes_til_ban == 0:
        await user.ban(reason='Reach max mute for ban', delete_message_days=0)
        await ctx.send(f"Banned {user.name} for reaching max mutes!")


async def punishment_time(ctx, time):
    week = 0
    day = 0
    hour = 0
    minute = 0
    second = 0

    punishment = list(time)
    punishment_queue = []

    for p in punishment:
        if '0' <= p <= '9':
            punishment_queue.append(str(p))
        elif p == 'w':
            week = punishment_queue
            week = int("".join(week))
            print(f"Week punishment is {week}")
            punishment_queue.clear()
        elif p == 'd':
            day = punishment_queue
            day = int("".join(day))
            print(f"Day punishment is {day}")
            punishment_queue.clear()
        elif p == 'h':
            hour = punishment_queue
            hour = int("".join(hour))
            print(f"Hour punishment is {hour}")
            punishment_queue.clear()
        elif p == 'm':
            minute = punishment_queue
            minute = int("".join(minute))
            print(f"Minutes punishment is {minute}")
            punishment_queue.clear()
        elif p == 's':
            second = punishment_queue
            second = int("".join(second))
            print(f"Seconds punishment is {second}")
            punishment_queue.clear()
        else:
            await ctx.send(f"Please enter a valid punishment time.")

    return timedelta(weeks=week, days=day, hours=hour, minutes=minute, seconds=second)


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
                raise commands.BadArgument("The user was not muted.")

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
    async def permban(self, ctx, member: discord.Member, time: str, *, reason=None, delete_message_days=0):
        punishment = await punishment_time(ctx, time)
        print(f"{member} Member object, Mod commands. Line 154.")

        await member.ban(reason=reason, delete_message_days=delete_message_days)
        post = {"_id": member.id, "TYPE:": 'BANNED', "NAME": member.name + '#' + member.discriminator,
                "BANNED AT": datetime.utcnow(), "BANNED TIL": datetime.utcnow() + punishment}
        banned_users_db.insert_one(post)
        post = {"USER ID": member.id, "TYPE:": 'BANNED', "NAME": member.name + '#' + member.discriminator,
                "BANNED AT": datetime.utcnow(), "BANNED TIL": datetime.utcnow() + punishment}
        logs.insert_one(post)
        print(f"Added {member.name} to ban logs")
        print(f"Banned Til Time {punishment + datetime.utcnow()},Punishment time {punishment}")
        print(f"{member} has been banned from the server. Reason = {reason}")

        await ctx.send(f"{member} has been banned from the server.")

        # 1d7h30m

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        print("In mod commands UNBAN ")
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
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

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def mute(self, ctx, user: Sinner, punishment=None, reason=None):
        await mute(ctx, user, punishment, reason or "treason")  # uses the mute function
        post = {"USER ID": user.id, "TYPE:": 'MUTED', "NAME": user.name + '#' + user.discriminator,
                "UNMUTED AT": datetime.utcnow()}
        logs.insert_one(post)

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def unmute(self, ctx, user: Redeemed):
        await user.remove_roles(discord.utils.get(ctx.guild.roles, name="Muted"))  # removes muted role
        await ctx.send(f"{user.mention} has been unmuted")

    @commands.has_permissions(mute_members=True)
    @commands.command()
    async def block(self, ctx, user: Sinner = None):
        if not user:  # checks if there is user
            return await ctx.send("You must specify a user")

        await ctx.set_permissions(user, send_messages=False)  # sets permissions for current channel
        await increment_user_mutes(ctx, user)

    @commands.has_permissions(mute_members=True)
    @commands.command()
    async def unblock(self, ctx, user: Sinner = None):
        if not user:  # checks if there is user
            return await ctx.send("You must specify a user")

        await ctx.set_permissions(user, send_messages=True)  # gives back send messages permissions

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def warn(self, ctx, member: discord.Member):
        collection.update_one({"_id": member.id}, {'$inc': {"Warnings": 1}})
        warnings = collection.find_one({"_id": member.id})['Warnings']
        if warnings == 0:
            return
        elif warnings % warnings_til_mute == 0:
            await mute(ctx, member, reason=None)
            await ctx.send(f"Muted {member.name} for reaching max warnings!")
        else:
            await ctx.send(f"{member.mention} You have been warned!"
                           f" {warnings % warnings_til_mute}/{warnings_til_mute} til mute!")

        print(f"incremented {member.name} warnings!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_users_db(self, ctx):

        for guild in self.bot.guilds:
            for member in guild.members:
                print(f"{member.id}")
                if collection.find_one({"_id": member.id}):
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
        embed.add_field(name='-mute', value='{Player name} ', inline=False)
        embed.add_field(name='-unmute', value='{Player name} ', inline=False)
        embed.add_field(name='-block', value='{Player name} #Blocks them from that specific channel', inline=False)
        embed.add_field(name='-unblock', value='{Player name} #Unblocks them from that specific channel', inline=False)

        await ctx.send(author, embed=embed)


def setup(bot):
    bot.add_cog(ModCommands(bot))
