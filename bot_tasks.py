import discord
from discord.ext import commands, tasks
from database import db
import datetime

banned_users = db["banned_users"]

class BotTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @tasks.loop(seconds=15)
    async def auto_unban(self):
        now = datetime.datetime.utcnow()

        for user in banned_users.find():
            ban_time = banned_users.find_one({"banned til"})
            print(ban_time)

            if ban_time >= now:
                return




def setup(bot):
    bot.add_cog(BotTasks(bot))