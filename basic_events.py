# Events cog

import discord
from discord.ext import commands
from discord.utils import get
from database import db
from pymongo import MongoClient
import pymongo
from datetime import datetime
from bot_settings import default_role


collection = db["users"]
deleted_messages = db["deleted_messages"]
logs = db["logs"]
banned_users_db = db['banned_users']


class BasicEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("Ready"))
        print("Bot is online")

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if len(message) > 0:
            print("The message " + str(message.id) + " has been deleted")
            post = {"_id": message.id, "author": message.author.name, "author id": message.author.id,
                    "message": message.content, "created at": message.created_at, "deleted at": datetime.utcnow()}
            deleted_messages.insert_one(post)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        print("The message " + str(before.id) + " sent by " + str(
            before.author.name) + " has been edited by " + after.author.name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member} has joined the server!")
        await member.send(f"{member.mention} Welcome to discord server. Please read and follow all the rules")
        role = get(member.guild.roles, name=default_role)
        await member.add_roles(role, reason=None, atomic=True)
        print(f"Gave {member.name} the {role} role")

        if collection.find_one({"_id": member.id}) is None:
            post = {"_id": member.id, "name": member.name, "Joined": datetime.utcnow(), "Bans": 0, "Warnings": 0,
                    "Mutes": 0}
            collection.insert_one(post)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):

        post = {"User ID": user.id,"TYPE:": 'UNBANNED', "name": user.name, "unbanned at": datetime.utcnow()}
        logs.insert_one(post)
        print(f"{user.name} was unbanned and logged to db!")
        banned_users_db.remove({'_id': user.id})

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        try:
            collection.update({"_id": user.id}, {'$inc': {"Bans": 1}})
            print(f"Incremented {user.name} Bans")
        except Exception as error:
            print(f"Failed to increment user bans to users db: {error}")


def setup(bot):
    bot.add_cog(BasicEvents(bot))
