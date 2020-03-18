import discord
from discord.ext import commands, tasks
from database import db
from datetime import datetime

banned_users_db = db["banned_users"]
logs_db = db['logs']
muted_users_db = db['muted_users']


class BotTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto.start()

    @tasks.loop(minutes=10)
    async def auto(self):
        print(f"Running task")
        now = datetime.utcnow()
        guild = self.bot.get_guild(677957812965343262)

        for user in banned_users_db.find():  # Iterating through the banned users db
            ban_time = user['BANNED TIL']
            user_name = user['NAME']
            user_id = user['_id']
            if now >= ban_time:  # Checking if the USERS banned time is up
                await guild.unban(discord.Object(id=user_id))
                print(f"Auto Unbanned: {user_name}")

        for user in muted_users_db.find():  # Iterating through the muted users db
            muted_time = user['MUTED TIL']
            muted_user_name = user['NAME']
            muted_user_id = user['_id']
            member = guild.get_member(muted_user_id)

            if now >= muted_time:  # Checking if the USERS banned time is up
                await member.remove_roles(discord.utils.get(guild.roles, name="Muted"))
                print(f"Auto Unmuted: {muted_user_name}")
                muted_users_db.remove({'_id': muted_user_id})
                post = {"USER ID": user.id, "TYPE:": 'MUTED', "NAME": user.name + '#' + user.discriminator,
                        "UNMUTED AT": datetime.utcnow()}
                logs_db.insert_one(post)

    @auto.before_loop
    async def before_auto_unban(self):
        print('Waiting for bot to be ready to start loop')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(BotTasks(bot))
