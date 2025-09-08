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

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()

client = discord.Client(intents=intents)


# Establishing dates to determine the season
Year = datetime.now(timezone.utc).year
Winter_Start = datetime(Year, 12, 21, tzinfo=timezone.utc)
Spring_Start = datetime(Year, 3, 20, tzinfo=timezone.utc)
Summer_Start = datetime(Year, 6, 21, tzinfo=timezone.utc)
Fall_Start = datetime(Year, 9, 22, tzinfo=timezone.utc)


# Establishing mean and bound temperatures to randomly select the temps
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

scale = 12

# Percipitation list and weights per season
Percip_List = np.array(['Sunny :sunny:', 'Partially Cloudy :white_sun_cloud:', 
                       'Cloudy :cloud:', 'Sun shower :white_sun_rain_cloud:', 
                       'Drizzle :umbrella:', 'Downpour :cloud_rain:', 
                       'Thunderstorm :thunder_cloud_rain:', 'Flurry :snowflake:', 
                       'Blizzard :cloud_snow:', 'Sleet :cloud_rain: :cloud_snow:', 
                       'Hail :ice_cube:', 'Smog :fog:', 'Windy :leaves:', 'Gale :dash:', 'Hurricane :cloud_tornado:'])

Winter_Weights = np.array([0.10, 0.15, 0.15, 0, 0.05, 0.02, 0 ,0.15, 0.10, 0.08, 0.04, 0.05, 0.08, 0.03, 0])
Spring_Weights = np.array([0.22, 0.13, 0.13, 0.05, 0.10, 0.07, 0.05, 0.02, 0, 0.03, 0.05, 0.05, 0.05, 0.05, 0])
Summer_Weights = np.array([0.37, 0.10, 0.08, 0.07, 0.05, 0.05, 0.10, 0, 0, 0, 0.02, 0.07, 0.05, 0.03, 0.01])
Fall_Weights = np.array([0.20, 0.10, 0.10, 0.07, 0.05, 0.05, 0.13, 0.02, 0, 0.03, 0.02, 0.10, 0.09, 0.03, 0.01])


# Embed Variables
title = "<:gear1:1383966866958975057> <:flower1:1383966946009284608> Ironhaven Daily Weather <:flower1:1383966946009284608> <:gear1:1383966866958975057>"

summer = ":sunny: Summer :sunny:"
summer_color = 0xf1c40f # Gold

fall = ":fallen_leaf: Fall :fallen_leaf:"
fall_color = 0xe74c3c # Red

winter = ":snowflake: Winter :snowflake:"
winter_color = 0x3498db # Blue

spring = ":tulip: Spring :tulip:"
spring_color = 0xe91e63 # Magenta


# Special Weather Probability
special = False
Special_Weather = [True, False]
Special_Weights = [0.5, 0.5]


# Special Weather Variables
Special_Nobles = [["<a:explode:1328412911445606472> The Queen Explodes You!!!! <a:explode:1328412911445606472>", "KABOOM! Don\'t even roll."],
                  ["Free Candy Day!","Roll 1000 times!!!"]]
Special_Scholars = [["<:gear3:1383966921644314704> Inventor's Festival <:gear3:1383966921644314704>", 
                     "The university is running a festival to show off its brightest inventors! Today you get a bonus roll for `/tableroll university`!"],
                    ["Evil Science Day!","Perform unethical experiments only!!"]]
Special_Seaglass = [["FLOOD!", "Grab some fish from the street today! `/tableroll streetfish'"],
                    ["Gang Day :D","Everyone pay money to your local gang!"]]
Special_Rosehill = [["Farm Fair Day!", "Extra tableroll to pet a pig today!"],
                    ["Beautiful Flowers Outside","There are beautiful flowers outside. Tableroll pick flowers."]]

generic = [["Generic Event", "You're in the wrong channel."]]


def get_season():
    # Function to check the season
    # It takes takes date and compares it to the start/end dates of the seasons
    # in the nothern hemisphere
    # Outputs: season (String denoting the title to use for each season), 
    # weights (percipitation weights for each season), loc (median temp), low (lower bound temp), 
    # high (upper bound temp), color (embed color to denote each season)

    today = datetime.now(timezone.utc)
    #today = datetime(Year,1,5, tzinfo=timezone.utc) # Specified date used for testing

    if today < Spring_Start or today >= Winter_Start:
        # Winter
        season = winter
        weights = Winter_Weights
        loc = Winter_Median
        low = Winter_Low
        high = Winter_High
        color = winter_color
    elif today >= Spring_Start and today < Summer_Start:
        # Spring
        season = spring
        weights = Spring_Weights
        loc = Spring_Median
        low = Spring_Low
        high = Spring_High
        color = spring_color
    elif today >= Summer_Start and today < Fall_Start:
        # Summer
        season = summer
        weights = Summer_Weights
        loc = Summer_Median
        low = Summer_Low
        high = Summer_High
        color = summer_color
    else:
        # Fall
        season = fall
        weights = Fall_Weights
        loc = Fall_Median
        low = Fall_Low
        high = Fall_High
        color = fall_color

    return season, weights, loc, low, high, color

def get_temp(loc, low, high, weights):
    # Function to randomly generate the temp depending on season and the percip/wind
    # It generates a random number from a truncated normal distribution
    # The percip/wind is randomly chosen from a weighted list with different weights per season
    # Inputs: loc (median of the distrib.), low (lower bound), high (upper bound), weights (percip weights)
    # Outputs: temp_F (temp in F), temp_C (temp converted to C), percip (percipitation/wind flavor)

    a, b = (low - loc) / scale, (high - loc) / scale
    temp = stats.truncnorm.rvs(a=a, b=b, loc=loc, scale=scale, size=1)
    temp_F = int(temp[0])
    temp_C = round((temp_F - 32) * 5/9)

    percip = np.random.choice(Percip_List, size=None, replace=True, p=weights)

    return temp_F, temp_C, percip


def embed_msg(title, color, season, temp_F, temp_C, percip):
    # Unused function to create an embedded message

    embedVar = discord.Embed(title=title, color=color)
    embedVar.add_field(name=season, value = "", inline=False)
    embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
    embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)

    return embedVar


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
async def on_message(message):
    if message.author == client.user:
        return

    # Test embed output
    if message.content.startswith('!test'):
        embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
        embedVar.add_field(name="Field1", value="Test1", inline=False)
        embedVar.add_field(name="Field2", value="Test2", inline=False)
        embedVar.add_field(name="", value="", inline=False)
        embedVar.add_field(name="Field Special Weather", value="Special Test!", inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)

    # Generate random weather by season (No chance of special weather)
    if message.content.startswith('!SummerWeather'):
        season = summer
        color = summer_color
        temp_F, temp_C, percip = get_temp(Summer_Median, Summer_Low, Summer_High, Summer_Weights)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=season, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!FallWeather'):
        season = fall
        color = fall_color
        temp_F, temp_C, percip = get_temp(Fall_Median, Fall_Low, Fall_High, Fall_Weights)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=season, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!WinterWeather'):
        season = winter
        color = winter_color
        temp_F, temp_C, percip = get_temp(Winter_Median, Winter_Low, Winter_High, Winter_Weights)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=season, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!SpringWeather'):
        season = spring
        color = spring_color
        temp_F, temp_C, percip = get_temp(Spring_Median, Spring_Low, Spring_High, Spring_Weights)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=season, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)

    # Generate random weather. Season is determined automatically by today's date
    # No chance of special weather
    if message.content.startswith('!Weather'):
        
        season, weights, loc, low, high, color = get_season()

        temp_F, temp_C, percip = get_temp(loc, low, high, weights)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=season, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)


    # Generate weather and special weather by district
    # Season is determined automatically by today's date
    if message.content.startswith('!SpecialWeatherNobles'):

        season, weights, loc, low, high, color = get_season()
       
        temp_F, temp_C, percip = get_temp(loc, low, high, weights)

        event, flavor = random.choice(Special_Nobles)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=summer, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)
        embedVar.add_field(name="", value="", inline=False)
        embedVar.add_field(name=event, value=flavor, inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!SpecialWeatherScholars'):
        
        season, weights, loc, low, high, color = get_season()
        
        temp_F, temp_C, percip = get_temp(loc, low, high, weights)

        event, flavor = random.choice(Special_Scholars)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=summer, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)
        embedVar.add_field(name="", value="", inline=False)
        embedVar.add_field(name=event, value=flavor, inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!SpecialWeatherSeaglass'):
        
        season, weights, loc, low, high, color = get_season()
        
        temp_F, temp_C, percip = get_temp(loc, low, high, weights)


        event, flavor = random.choice(Special_Seaglass)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=summer, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)
        embedVar.add_field(name="", value="", inline=False)
        embedVar.add_field(name=event, value=flavor, inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!SpecialWeatherRosehill'):
        
        season, weights, loc, low, high, color = get_season()
        
        temp_F, temp_C, percip = get_temp(loc, low, high, weights)

        event, flavor = random.choice(Special_Rosehill)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=summer, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)
        embedVar.add_field(name="", value="", inline=False)
        embedVar.add_field(name=event, value=flavor, inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)


    # Roll random special weather. Season is automatically determined by today's date.
    # The special weather table is automatically determined by the channel this is sent in
    # If not sent in one of the 4 district rolling channels, a "generic event" message is sent instead
    if message.content.startswith('!SpecialWeather'):
        
        season, weights, loc, low, high, color = get_season()
       
        temp_F, temp_C, percip = get_temp(loc, low, high, weights)


        sent_channel = message.channel.id
        if sent_channel == 1367974440419332268:
            special_table = Special_Nobles
        elif sent_channel == 1367974479539605534:
            special_table = Special_Scholars
        elif sent_channel == 1367974510279524442:
            special_table = Special_Seaglass
        elif sent_channel == 1367974598104191026:
            special_table = Special_Rosehill
        else:
            special_table = generic

        event, flavor = random.choice(special_table)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=summer, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)
        embedVar.add_field(name="", value="", inline=False)
        embedVar.add_field(name=event, value=flavor, inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)

    # Roll random special weather. Season is automatically determined by today's date.
    # The special weather table is automatically determined by the channel this is sent in
    # If not sent in one of the 4 district rolling channels, a "generic event" message is sent instead
    if message.content.startswith('!SpecialWeather'):
        
        season, weights, loc, low, high, color = get_season()
       
        temp_F, temp_C, percip = get_temp(loc, low, high, weights)


        sent_channel = message.channel.id
        if sent_channel == 1367974440419332268:
            special_table = Special_Nobles
        elif sent_channel == 1367974479539605534:
            special_table = Special_Scholars
        elif sent_channel == 1367974510279524442:
            special_table = Special_Seaglass
        elif sent_channel == 1367974598104191026:
            special_table = Special_Rosehill
        else:
            special_table = generic

        event, flavor = random.choice(special_table)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=summer, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)
        embedVar.add_field(name="", value="", inline=False)
        embedVar.add_field(name=event, value=flavor, inline=False)
        await message.delete()
        await message.channel.send(embed=embedVar)


    # Roll random special weather. Season is automatically determined by today's date.
    # The special weather table is automatically determined by the channel this is sent in
    # If not sent in one of the 4 district rolling channels, a "generic event" message is sent instead
    if message.content.startswith('!RandomWeather'):
        
        season, weights, loc, low, high, color = get_season()
       
        temp_F, temp_C, percip = get_temp(loc, low, high, weights)

        special = np.random.choice(Special_Weather, size=None, replace=True, p=Special_Weights)

        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=summer, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)

        sent_channel = message.channel.id
        if special:
            if sent_channel == 1367974440419332268:
                special_table = Special_Nobles
            elif sent_channel == 1367974479539605534:
                special_table = Special_Scholars
            elif sent_channel == 1367974510279524442:
                special_table = Special_Seaglass
            elif sent_channel == 1367974598104191026:
                special_table = Special_Rosehill
            else:
                special_table = generic

            event, flavor = random.choice(special_table)

            embedVar.add_field(name="", value="", inline=False)
            embedVar.add_field(name=event, value=flavor, inline=False)

        await message.delete()
        await message.channel.send(embed=embedVar)


    # Randomly generates both weather and special weather. Season is automatically determined by today's date.
    # The is a chance of special weather. The special weather table is automatically determined by the channel this is sent in
    # This will generate and send weather to ALL 4 district rolling channels automatically!!
    if message.content.startswith('!AllRandomWeather'):

        await message.delete()
        season, weights, loc, low, high, color = get_season()
       
        temp_F, temp_C, percip = get_temp(loc, low, high, weights)

        # Get channels, check for special weather, and send
        #channel = client.get_guild(1316562992535572560).get_channel(1363490745394139418)
        for channel_id in channel_ids:

            embedVar = discord.Embed(title=title, color=color)
            embedVar.add_field(name=summer, value = "", inline=False)
            embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
            embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)

            # Roll to see if there is special weather in that district today
            special = np.random.choice(Special_Weather, size=None, replace=True, p=Special_Weights)

            if channel_id == 1367974440419332268:
                special_table = Special_Nobles
            elif channel_id == 1367974479539605534:
                special_table = Special_Scholars
            elif channel_id == 1367974510279524442:
                special_table = Special_Seaglass
            elif channel_id == 1367974598104191026:
                special_table = Special_Rosehill
            else:
                special_table = generic

            event, flavor = random.choice(special_table)

            embedVar.add_field(name="", value="", inline=False)
            embedVar.add_field(name=event, value=flavor, inline=False)

            channel = client.get_guild(server_id).get_channel(channel_id)
            await channel.send(embed=embedVar)
    
    # Randomly generates both weather and special weather. Season is automatically determined by today's date.
    # The is a chance of special weather. The special weather table is automatically determined by the channel this is sent in
    # This will generate and send weather to ALL 4 district rolling channels automatically!!
    if message.content.startswith('!AllSpecialWeather'):

        await message.delete()
        season, weights, loc, low, high, color = get_season()
       
        temp_F, temp_C, percip = get_temp(loc, low, high, weights)

        # Get channels, check for special weather, and send
        #channel = client.get_guild(1316562992535572560).get_channel(1363490745394139418)
        for channel_id in channel_ids:

            embedVar = discord.Embed(title=title, color=color)
            embedVar.add_field(name=summer, value = "", inline=False)
            embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
            embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)

            # Roll to see if there is special weather in that district today
            special = True

            if special:
                if channel_id == 1367974440419332268:
                    special_table = Special_Nobles
                elif channel_id == 1367974479539605534:
                    special_table = Special_Scholars
                elif channel_id == 1367974510279524442:
                    special_table = Special_Seaglass
                elif channel_id == 1367974598104191026:
                    special_table = Special_Rosehill
                else:
                    special_table = generic

                event, flavor = random.choice(special_table)

                embedVar.add_field(name="", value="", inline=False)
                embedVar.add_field(name=event, value=flavor, inline=False)

            channel = client.get_guild(server_id).get_channel(channel_id)
            print(channel)
            await channel.send(embed=embedVar)

 






# Timing the schedule of the bot
WHEN = time(19, 0, 0)  # Test Time
# WHEN = time(18, 42, 0) # 12 AM EST
#channel_id = 1363490745394139418 # Put your channel id here, Sister Server bot-testing
#channel_ids = [1363490745394139418, 1316562993806577687] # Sister Server bot-testing and general
channel_ids = [1367974440419332268, 1367974479539605534, 1367974510279524442, 1367974598104191026] # Ironhave four district rolling channels
server_id = 1367974312367099914 # Ironhaven
# server_id = 1316562992535572560 #Sister Server

async def called_once_a_day():  # Fired every day
    await client.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel


    # Check the season
    season, weights, loc, low, high, color = get_season()

    # Select Temp and Percipitation
    temp_F, temp_C, percip = get_temp(Summer_Median, Summer_Low, Summer_High, Summer_Weights)


    # Get channels, check for special weather, and send
    #channel = client.get_guild(1316562992535572560).get_channel(1363490745394139418)
    for channel_id in channel_ids:


        # Create Embed
        embedVar = discord.Embed(title=title, color=color)
        embedVar.add_field(name=season, value = "", inline=False)
        embedVar.add_field(name="Temperature:", value= str(temp_F) + "\xb0F/" + str(temp_C) + "\xb0C", inline=False)
        embedVar.add_field(name="Wind/Percipitation:", value=percip, inline=False)

        # Roll to see if there is special weather in that district today
        special = np.random.choice(Special_Weather, size=None, replace=True, p=Special_Weights)

        if special:
            if channel_id == 1367974440419332268:
                special_table = Special_Nobles
            elif channel_id == 1367974479539605534:
                special_table = Special_Scholars
            elif channel_id == 1367974510279524442:
                special_table = Special_Seaglass
            elif channel_id == 1367974598104191026:
                special_table = Special_Rosehill
            else:
                special_table = generic

            event, flavor = random.choice(special_table)

            embedVar.add_field(name="", value="", inline=False)
            embedVar.add_field(name=event, value=flavor, inline=False)

        
        channel = client.get_guild(server_id).get_channel(channel_id)
        await channel.send(embed=embedVar)

async def background_task():
    now = datetime.now(timezone.utc)
    #print(now.time())
    print(now)
    if now.time() > WHEN:  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0), tzinfo=timezone.utc)
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        print(seconds)
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
    while True:
        now = datetime.now(timezone.utc) # current time
        target_time = datetime.combine(now.date(), WHEN, tzinfo=timezone.utc)  # 6:00 PM today (In UTC)
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
        await called_once_a_day()  # Call the helper function that sends the message
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0), tzinfo=timezone.utc)
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        print(seconds)
        await asyncio.sleep(seconds) # Sleep until tomorrow and then the loop will start a new iteration


async def main():
    asyncio.create_task(background_task())
    await client.start(TOKEN)


asyncio.run(main())