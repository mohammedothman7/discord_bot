# Events cog

import discord
from discord.ext import commands
from discord.utils import get
from database import  db
from pymongo import MongoClient
import pymongo
import datetime

default_role = "Member"
collection = db["users"]
deleted_messages = db["deleted_messages"]

class BasicEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("Ready"))
        print("Bot is online")



    @commands.Cog.listener()
    async def on_message_delete(self, message):
        print("The message " + str(message.id) + " has been deleted")
        post = {"_id": message.id, "author": message.author.name, "author id": message.author.id, "message": message.content, "created at": message.created_at, "deleted at": datetime.datetime.utcnow()}
        deleted_messages.insert_one(post)


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        print("The message " + str(before.id) + " sent by " + str(
        before.author.name) + " has been edited by " + after.author.name)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member} has joined the server!")
        await member.send(f"{member.mention} Welcome to discord server. Please read and follow all the rules")
        role = get(member.guild.roles, name="Member")
        await member.add_roles(role, reason=None, atomic=True)
        print(f"Gave {member.name} the {role} role")
        post = {"_id": member.id, "name": member.name, "Joined": datetime.datetime.today()}
        collection.insert_one(post)


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            collection.remove({"_id": member.id})
            print(f"{member.name} has been deleted from the database")
        except Exception:
            print(f"Could not remove {member.name} from database")




def setup(bot):
    bot.add_cog(BasicEvents(bot))