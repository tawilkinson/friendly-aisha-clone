import os
import random
import discord
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')
BOT_USER_ID = os.getenv('BOT_USER_ID')
BOT_ROLE_ID = os.getenv('BOT_ROLE_ID')
MOVIE_AGENDA = os.getenv('MOVIE_AGENDA')
TV_GAMES_AGENDA = os.getenv('TV_GAMES_AGENDA')

DEBUG = True

client = commands.Bot(command_prefix='a?')


def scrape_movie_events_from_calender(calender):
    events = []
    adgenda_html = requests.get(calender)
    soup = BeautifulSoup(adgenda_html.text, 'html.parser')
    if not 'Nothing currently scheduled' in soup.text:
        adgenda_events = soup.select("body > div.view-container-border > div > div")
        for event in adgenda_events:
            date = ''
            event_date = event.find("div", class_="date")
            if event_date:
                date = event_date.text
            event_times = event.findAll("td", class_="event-time")
            if event_times:
                times = [event_time.text for event_time in event_times]
            event_summary = event.findAll("div", class_="event-summary")
            if event_summary:
                descriptions = [event.text for event in event_summary]
            oneline_event_list = [date, dict(zip(times, descriptions))]
            events.append(oneline_event_list)
    return events


def scrape_events_from_calender(calender):
    events = []
    adgenda_html = requests.get(calender)
    soup = BeautifulSoup(adgenda_html.text, 'html.parser')
    if not 'Nothing currently scheduled' in soup.text:
        adgenda_events = soup.select("body > div.view-container-border > div > div")
        for event in adgenda_events:
            event_text = event.text
            oneline_event_list = event_text.split('\n')
            events.append(oneline_event_list)
    return events


def embed_movie_schedule(schedule, first=False):
    formatted_schedule = discord.Embed(title='Movie Schedule')
    if not schedule:
        formatted_schedule.add_field(name='Empty schedule', value='Hmm, looks like nothing is scheduled!')
    else:
        if first:
            schedule = [schedule[0]]

        for day in schedule:
            formatted_schedule.add_field(name=day[0],
                                        value='\n'.join([str(time + ': ' + description) for time, description in day[1].items()]),
                                        inline=False)

    formatted_schedule.add_field(name='Calender',
                                value='[See the full calender of events online](https://calendar.google.com/calendar/u/0/embed?src=qjva8eaked6q9vdcgqkspqvseg@group.calendar.google.com)',
                                inline=False)
    return formatted_schedule


def embed_games_schedule(schedule):
    formatted_schedule = discord.Embed(title='TV Games')
    formatted_schedule.add_field(name='Every Wednesday at 8PM!', value='join Acres Greg in the TV games voice channel for socialising and games')
    for day in schedule:
        formatted_schedule.add_field(name=day[0],
                                    value='\n'.join(day[1:]),
                                    inline=False)
    return formatted_schedule


def embed_response(text):
    robot_response = discord.Embed(title='Beep boop!')
    robot_response.add_field(name='a?', value=text)
    return robot_response


def get_random_friendly_advice():
    with open('friendly_robot_advice.txt') as f:
        friendly_robot_advice=[line.strip() for line in f]
    random_friendly_message=random.choice(friendly_robot_advice)
    return random_friendly_message


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == SERVER:
            break
    print(str(client.user) + " has connected to Discord Server " + str(guild.name))


@client.event
async def on_message(message):
    chat_message = message.content.lower()

    if DEBUG:
        print(str(message.author) + '\n' + str(chat_message))

    if message.author == client.user:
        return

    # if wade used AoE2 shortcut for lol, reply
    if message.author.id == 474091918050066432:
        if '11' in chat_message:
            await message.channel.send("herb_laugh.mp4")

    if any(id in chat_message for id in [BOT_USER_ID, BOT_ROLE_ID]):
        await message.channel.send('Beep boop!')

    if 'robot' in chat_message:
        friendly_message = get_random_friendly_advice()
        await message.channel.send(friendly_message)

    if 'regulations' in chat_message:
        await message.channel.send('Praise be the regulations')

    if 'movie schedule' in chat_message:
        schedule = scrape_movie_events_from_calender(MOVIE_AGENDA)
        print_schedule = embed_movie_schedule(schedule)
        await message.channel.send(embed=print_schedule)

    if 'tv games schedule' in chat_message:
        schedule = scrape_events_from_calender(TV_GAMES_AGENDA)
        print_schedule = embed_games_schedule(schedule)
        await message.channel.send(embed=print_schedule)

    await client.process_commands(message)


@client.command(name='movies', help='Read the full movie schedule from the calendar')
async def full_schedule(ctx):
    schedule = scrape_movie_events_from_calender(MOVIE_AGENDA)
    print_schedule = embed_movie_schedule(schedule)
    await ctx.send(embed=print_schedule)


@client.command(name='movie', help='Reads the next scheduled movie schedule from the calendar')
async def next_scheduled(ctx):
    schedule = scrape_movie_events_from_calender(MOVIE_AGENDA)
    print_schedule = embed_movie_schedule(schedule, first=True)
    await ctx.send(embed=print_schedule)


client.run(TOKEN)
