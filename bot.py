# A discord bot created by Moe#6306
import os
import shutil
import time
import discord
import random
from queue import Queue
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import youtube_dl

TOKEN = open("BOT_TOKEN", "r").readline()

bot = commands.Bot(command_prefix='-')

extensions = {'basic_commands', 'basic_events'}
players = {}
is_bot_connected_to_voice = False

default_role = "Member"


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




@bot.command(aliases=["8ball"])
async def _8ball(ctx, *, question):
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."]

    await ctx.send(f'{question}: \n{random.choice(responses)}')


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)


@bot.command(aliases=["ban"])
@commands.has_permissions(ban_members=True)
async def permban(ctx, member: discord.Member, *, reason=None, delete_message_days=1):
    await member.ban(reason=reason, delete_message_days=delete_message_days)
    print(f"{member} has been banned from the server. {reason}")


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"{user} has been unbanned")
            return

    await ctx.send("Could not find banned user with given name")
    return False


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)
    print(f"Removed {amount} messages from {ctx.channel.name}")


@bot.command(aliases=["h", "?", "commands", "command"])
async def _help(ctx):
    await ctx.send(f"To use a command type  -   before the command\nList of commands:\n-ping\n-8ball\n-clear")


@bot.command(aliases=["j", "joi"])
async def join(ctx):
    global voice

    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")
        is_bot_connected_to_voice = True
        print(is_bot_connected_to_voice)
        await ctx.send(f"Joined {channel}")


@bot.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left the {channel} channel")
        await ctx.send(f"Left {channel}")
        is_bot_connected_to_voice= False
    else:
        print(f"Not in a voice channel")
        await ctx.send("Not in a voice channel")


@bot.command()
async def play(ctx, url: str):
    print(f"Bot connected? {is_bot_connected_to_voice}")
    if not is_bot_connected_to_voice:
        await join(ctx)


    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")

    song_there = os.path.isfile("song.mp3")

    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("Music playing, use -queue to add it to the playlist.")
        return

    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue Folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")

    await ctx.send("Getting everything ready now")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    song_name = name.rsplit("-", 2)
    await ctx.send(f"Playing: {song_name[0]}")
    print("playing\n")

queues = {}


@bot.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music not playing failed pause")
        await ctx.send("Music not playing failed pause")


@bot.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Resumed music")
    else:
        print("Music is not paused")
        await ctx.send("Music is not paused")


@bot.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Music stopped")
    else:
        print("No music playing failed to stop")
        await ctx.send("No music playing failed to stop")


queues = {}

@bot.command(pass_context=True, aliases=['q', 'que'])
async def queue(ctx, url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])
    await ctx.send(f"Added song. {q_num} in queue.")

    print("Song added to queue\n")


@bot.command(aliases=["vol", "v", "vl"])
async def volume(ctx, vol: int = 5):
    global volume

    if vol < 1:
        await ctx.send("The volume you chose is too low, please pick a number between 1 and 10")
    elif vol > 10:
        await ctx.send("The volume you chose is too high, please pick a number between 1 and 10")
    else:
        volume = vol / 25
        voice.source.volume = volume
        print(f"Volume changed to {vol}")
        await ctx.send(f"Changed the volume to {vol}")


@bot.command(aliases=["next", "ski", "sk", "ne"])
async def skip(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Playing Next Song")
        voice.stop()
        await ctx.send("Next Song")
    else:
        print("No music playing")
        await ctx.send("No music playing failed")


bot.run(TOKEN)
