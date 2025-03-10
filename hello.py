import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import pandas as pd
from colorthief import ColorThief
from PIL import Image
import requests
from io import BytesIO
from colorthief import ColorThief
import asyncio
import random


intents = discord.Intents.default()
intents.dm_messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)


if os.path.exists('logs.json'):
    with open('logs.json', 'r') as f:
        logs = json.load(f)
else:
    logs = {}
if os.path.exists('goals.json'):
    with open('goals.json', 'r') as f:
        goals = json.load(f)
else:
    goals = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def log(ctx, *, message: str):
    user_id = str(ctx.author.id)
    if user_id not in logs:
        logs[user_id] = []
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_entry = {"date": current_date, "message": message}
    logs[user_id].append(log_entry)
    with open('logs.json', 'w') as f:
        json.dump(logs, f, indent=4)
    await ctx.send(f'Logged your message:\n\n{current_date}: {message}')

@bot.command()
async def progress(ctx):
    user_id = str(ctx.author.id)
    
    goals_message = "Your current goals:\n"
    if user_id in goals and goals[user_id]:
        for i, goal in enumerate(goals[user_id], 1):
            goals_message += f"{i}. {goal}\n"
    else:
        goals_message += "No goals set.\n"
    
    logs_message = "\nYour logged messages:\n"
    if user_id in logs and logs[user_id]:
        logs_message += "\n".join(f"{i+1}. {entry['date']}: {entry['message']}" for i, entry in enumerate(logs[user_id]))
    else:
        logs_message += "No logged messages."
    
    await ctx.send(f'{goals_message}{logs_message}')

@bot.command()
async def goal(ctx, *, goal: str):
    user_id = str(ctx.author.id)
    if user_id not in goals:
        goals[user_id] = []
    goals[user_id].append(goal)
    with open('goals.json', 'w') as f:
        json.dump(goals, f, indent=4)
    await ctx.send(f'Added new goal: {goal}')

@bot.command()
async def delete(ctx, type_: str, index: int):
    user_id = str(ctx.author.id)
    type_ = type_.lower()
    
    if type_ not in ['log', 'goal']:
        await ctx.send('Please specify either "log" or "goal" as the type to delete.')
        return
    
    if type_ == 'log':
        if user_id in logs and logs[user_id]:
            if 0 < index <= len(logs[user_id]):
                del logs[user_id][index - 1]  # Adjust index to be zero-based
                with open('logs.json', 'w') as f:
                    json.dump(logs, f, indent=4)
                await ctx.send(f'Deleted log entry at index {index}.')
            else:
                await ctx.send('Invalid log index.')
        else:
            await ctx.send('No logs found for this user.')
            
    elif type_ == 'goal':
        if user_id in goals and goals[user_id]:
            if 0 < index <= len(goals[user_id]):
                del goals[user_id][index - 1]  # Adjust index to be zero-based
                with open('goals.json', 'w') as f:
                    json.dump(goals, f, indent=4)
                await ctx.send(f'Deleted goal at index {index}.')
            else:
                await ctx.send('Invalid goal index.')
        else:
            await ctx.send('No goals found for this user.')


@bot.command()
async def deleteall(ctx):
    user_id = str(ctx.author.id)
    deleted_something = False
    
    if user_id in logs:
        del logs[user_id]
        with open('logs.json', 'w') as f:
            json.dump(logs, f, indent=4)
        deleted_something = True
        await ctx.send('All your logs have been deleted.')
    
    if user_id in goals:
        del goals[user_id]
        with open('goals.json', 'w') as f:
            json.dump(goals, f, indent=4)
        deleted_something = True
        await ctx.send('Your goals have been deleted.')
    
    if not deleted_something:
        await ctx.send('You have no logs or goals to delete.')



@bot.command()
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    
    user_id = str(member.id)
    user_logs = logs.get(user_id, [])
    recent_logs = user_logs[-5:]
    formatted_logs = "\n".join(f"{entry['date']}: {entry['message']}" for entry in recent_logs)
    
    user_goals = goals.get(user_id, [])
    if isinstance(user_goals, list):
        recent_goals = user_goals[-3:]  # Get last 3 goals
        formatted_goals = "\n".join(f"{i+1}. {goal}" for i, goal in enumerate(recent_goals))
    else:
        formatted_goals = "No goals set"

    avatar_url = member.avatar.url
    response = requests.get(avatar_url)
    Image.open(BytesIO(response.content))

    color_thief = ColorThief(BytesIO(response.content))
    dominant_color = color_thief.get_color(quality=1)

    discord_color = discord.Color.from_rgb(*dominant_color)

    embed = discord.Embed(title=f"{member.name}'s Profile", color=discord_color)
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="Recent Logs", value=formatted_logs or "No logs available", inline=False)
    embed.add_field(name="Goals", value=formatted_goals, inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    help_message = """
```

here are the available commands:

1. !log <message>: log a message with the current date.
   - example: `!log Completed 10 pushups`

2. !progress: view your logged messages and goals.
   - example: `!progress`

3. !goal <goal>: add a new goal.
   - example: `!goal run a marathon`

4. !delete <type> <index>: delete a log or goal by specifying the type and index.
   - example: `!delete log 1` or `!delete goal 2`

5. !deleteall: delete all your logs and goals.
   - Example: `!deleteall`

6. !profile [@user]: view your profile or another user's profile, including recent logs and goals.
   - Example: `!profile` or `!profile @username`

7. !help: display this helper menu.
   - Example: `!help`
```
"""

    await ctx.send(help_message)


    
bot.run('tokenjak')
