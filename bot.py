# A discord bot created by Moe#6306

from discord.ext import commands

TOKEN = open("BOT_TOKEN", "r").readline()

bot = commands.Bot(command_prefix='-')



extensions = {'basic_commands', 'basic_events', 'music_commands', 'mod_commands'}
players = {}




@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    try:
        bot.load_extension(extension)
        await ctx.send(f"Loaded {extension}")
        print(f"Loaded {extension}")
    except Exception:
        print("ERROR: Could not load extension")
        await ctx.send("ERROR: Could not load extension")


@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    try:
        bot.unload_extension(extension)
        await ctx.send(f"Unloaded {extension}")
        print(f"Unloaded {extension}")
    except Exception:
        print("ERROR: Could not unload extension")
        await ctx.send("ERROR: Could not unload extension")


@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    try:
        bot.unload_extension(extension)
        bot.load_extension(extension)
        await ctx.send(f"Reloaded {extension}")
        print(f"Reloaded {extension}")
    except Exception:
        print("ERROR: Could not reload extension")
        await ctx.send("ERROR: Could not reload extension")


if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as error:
            print(f"{extension} could not be loaded. {error}")


bot.run(TOKEN)
