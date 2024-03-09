import discord
import os
import pyaudio
from discord.ext import commands,tasks,voice_recv
from dotenv import load_dotenv

load_dotenv()

class MyAudioSource(discord.PCMAudio):
    def __init__(self, stream):
        self.stream = stream

    def read(self):
        return self.stream.read(CHUNK)
    def is_opus(self):
        return False
    
class MyAudioSink(voice_recv.AudioSink):
    def __init__(self, stream):
        self.stream = stream

    def write(self, user, data):
        self.stream.write(data.pcm)
        
    def wants_opus(self):
        return False
    
    def cleanup(self):
        return


# PyAudio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
# Chunk = 20ms of data
CHUNK = (RATE // 1000) * 20

# Create a PyAudio instance
audio = pyaudio.PyAudio()

# Open a new stream
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

# Output stream
output_stream = audio.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           output=True,
                           frames_per_buffer=CHUNK)


# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    # Check is already connected to a voice channel
    if ctx.message.guild.voice_client:
        await ctx.send("Already connected to a voice channel")
        return

    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    voice_client = await channel.connect(cls=voice_recv.VoiceRecvClient)

    my_audio_source = MyAudioSource(stream)

    voice_client.play(my_audio_source)

    my_audio_sink = MyAudioSink(output_stream)

    voice_client.listen(my_audio_sink)

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.event
async def on_ready():
    print('Running!')
    for guild in bot.guilds:
        for channel in guild.text_channels :
            if str(channel) == "general" :
                await channel.send('Bot Activated..')
        print('Active in {}\n Member Count : {}'.format(guild.name,guild.member_count))

@bot.command(help = "Prints details of Author")
async def whats_my_name(ctx) :
    await ctx.send('Hello {}'.format(ctx.author.name))

@bot.event
async def on_member_join(member):
     for channel in member.guild.text_channels :
         if str(channel) == "general" :
             on_mobile=False
             if member.is_on_mobile() == True :
                 on_mobile = True
             await channel.send("Welcome to the Server {}!!\n On Mobile : {}".format(member.name,on_mobile))             

@bot.event
async def on_message(message) :
    await bot.process_commands(message) 
    if str(message.content).lower() == "hello":
        await message.channel.send('Hi!')


if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)