# bot.py
import os
import random
import numpy as np
import scipy.stats as stats

import discord
from dotenv import load_dotenv

from discord.ext import commands
from datetime import datetime, time, date, timedelta, timezone
import asyncio


BASEDIR = 'C:\\Users\\lovew\\Documents\\WeatherBot'
load_dotenv(os.path.join(BASEDIR, '.env'))

#load_dotenv(override=True)
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
print(GUILD)

intents = discord.Intents.all()

#client = commands.Bot(command_prefix=',', intents=intents)
client = discord.Client(intents=intents)
#bot = commands.Bot(intents=intents, command_prefix='$')


Year = datetime.now(timezone.utc).year
Winter_Start = datetime(Year, 12, 21)
Spring_Start = datetime(Year, 3, 20)
Summer_Start = datetime(Year, 6, 21)
Fall_Start = datetime(Year, 9, 22)

test = datetime(Year,11,10)

if test < Spring_Start or test >= Winter_Start:
    print("It's Winter.")
elif test >= Spring_Start and test < Summer_Start:
    print ("It's Spring.")
elif test >= Summer_Start and test < Fall_Start:
    print("It's Summer.")
else:
    print("It's Fall.")

Winter_Median = 35
Spring_Median = 60
Summer_Median = 75
Fall_Median = 55

Winter_Low = -20
Spring_Low = 45
Summer_Low = 60
Fall_Low = 30

Winter_High = 50
Spring_High = 75
Summer_High = 105
Fall_High = 70

Percip_List = np.array(['Sunny :sunny:', 'Partially Cloudy :white_sun_cloud:', 
                       'Cloudy :cloud:', 'Sun shower :white_sun_rain_cloud:', 
                       'Drizzle :umbrella:', 'Downpour :cloud_rain:', 
                       'Thunderstorm :thunder_cloud_rain:', 'Flurry :snowflake:', 
                       'Blizzard :cloud_snow:', 'Sleet :cloud_rain: :cloud_snow:', 
                       'Hail :ice_cube:', 'Smog :fog:', 'Windy :leaves:', 'Gale :dash:', 'Hurricane :cloud_tornado:'])

Winter_Weights = np.array([0.10, 0.15, 0.15, 0, 0.05, 0.02, 0 ,0.15, 0.10, 0.08, 0.04, 0.05, 0.08, 0.03, 0])
Spring_Weights = np.array([0.20, 0.12, 0.11, 0.05, 0.10, 0.07, 0.05, 0.05, 0, 0.05, 0.05, 0.05, 0.05, 0.05, 0])
Summer_Weights = np.array([0.37, 0.10, 0.08, 0.07, 0.05, 0.05, 0.10, 0, 0, 0, 0.02, 0.07, 0.05, 0.03, 0.01])
Fall_Weights = np.array([0.20, 0.15, 0.10, 0.07, 0.05, 0.05, 0.13, 0, 0, 0, 0.02, 0.10, 0.09, 0.03, 0.01])

#for i in range (0,31):
    #temp = int(np.random.normal(loc=Summer_Median, scale=7.0, size=None))
    #temp = np.random.randint(50, high=105, size=None, dtype=int)
 #   scale = 12
 #   loc = Winter_Median
 #   a, b = (Winter_Low - loc) / scale, (Winter_High - loc) / scale
 #   temp = stats.truncnorm.rvs(a=a, b=b, loc=loc, scale=scale, size=1)
 #   temp = int(temp[0])
 #   percip = np.random.choice(Percip_List, size=None, replace=True, p=Winter_Weights)
 #   print(str(temp) + "/" + percip)

# Make a function to make a weather embed message with color, temp, and percip.
# Make a function to pick random temp
# Make a function to pick random percip
# Make a command to roll Summer/Winter/Spring/Fall weather manually
# Test for 50 days of each season yourself
# Add into the daily bot command




@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def embed_msg(season, color, temp, percip):
    print("Function Called")
    embedVar = discord.Embed(title="<:gear1:1383909855831785602> <:daisy:1383967158295330946> Ironhaven Daily Weather <:daisy:1383967158295330946> <:gear1:1383909855831785602>", color=color)
    embedVar.add_field(name=season, value = "", inline=False)
    embedVar.add_field(name="Temperature", value=str(temp) + "\xb0F/" + str(temp) + "\xb0C", inline=False)
    embedVar.add_field(name="Wind/Percipitation", value=percip, inline=False)
    return embedVar

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    brooklyn_99_quotes = [
        'I\'m explode.',
        'explode explode explode',
        (
            'Cool.'
            'EXPLODE NOW.'
        ),
    ]

    if message.content == '99!':
        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)

    
    if "tsubaki" in message.content:
        response = "get more bald"
        await message.channel.send(response, tts=True)

    if message.content.startswith('!hello'):
        embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
        embedVar.add_field(name="Field1", value="hi <a:eggsplode:1328413158930513954> \n bark bark this better be a *new* paragraph", inline=False)
        embedVar.add_field(name="Field2", value="hi2 <:cursednessie:1327685087457841212> <:dorian:1142539825174565015> \n ## Do you do this too", inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!WeatherTest'):
        embedVar = discord.Embed(title="<:gear1:1383909855831785602> <:daisy:1383967158295330946> Ironhaven Daily Weather Forecast <:daisy:1383967158295330946> <:gear1:1383909855831785602>", color=0x00ff00)
        embedVar.add_field(name=":sunny: Summer :sunny:", value = "", inline=False)
        embedVar.add_field(name="Temperature", value="999 \xb0F/666 \xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation", value="Parially Cloudy :cloud:", inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!Test'):
        print("Test activated")
        embedVar = asyncio.create_task(embed_msg("Fall",0x1abc9c,99,"Rain Bitch"))
        #embedVar = embed_msg("Fall",0x1abc9c,99,"Rain Bitch")
        await message.delete()
        print(embedVar)
        await message.channel.send(embed=embedVar)
        await message.channel.send("help")

WHEN = time(15, 4, 0)  # 6:00 PM
channel_id = 1363490745394139418 # Put your channel id here
server_id = 1316562992535572560

async def called_once_a_day():  # Fired every day
    await client.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel
    print("We are in: ")
    print(GUILD)
    print("GUILD: ")
    x = client.get_guild(1316562992535572560)
    print(x)
    channel = client.get_guild(1316562992535572560).get_channel(1363490745394139418)
    print("CHANNEL: ")
    print(channel)
    await channel.send("MESSAGE NOW!!!!")

async def background_task():
    now = datetime.now(timezone.utc)
    print(now.time())
    print(now)
    if now.time() > WHEN:  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0), tzinfo=timezone.utc)
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        print(seconds)
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
    while True:
        now = datetime.now(timezone.utc) # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
        target_time = datetime.combine(now.date(), WHEN, tzinfo=timezone.utc)  # 6:00 PM today (In UTC)
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
        await called_once_a_day()  # Call the helper function that sends the message
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0), tzinfo=timezone.utc)
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        print(seconds)
        await asyncio.sleep(seconds) # Sleep until tomorrow and then the loop will start a new iteration


async def main():
    print("For the love of god man")
    asyncio.create_task(background_task())
    await client.start(TOKEN)


asyncio.run(main())

#if __name__ == "__main__":
#    client.loop.create_task(background_task())
#    client.run('token')