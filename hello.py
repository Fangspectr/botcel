import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import pandas as pd
from colorthief import ColorThief
import discord
from discord.ext import commands
from PIL import Image
import requests
from io import BytesIO
from colorthief import ColorThief
import asyncio
import random


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

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
    if user_id in logs:
        user_logs = logs[user_id]
        formatted_logs = "\n".join(f"{entry['date']}: {entry['message']}" for entry in user_logs)
        await ctx.send(f'Your logged messages:\n\n{formatted_logs}')
    else:
        await ctx.send('You have no logged messages.')

@bot.command()
async def goal(ctx, *, goal: str):
    user_id = str(ctx.author.id)
    goals[user_id] = goal
    with open('goals.json', 'w') as f:
        json.dump(goals, f, indent=4)
    await ctx.send(f'Your goal has been set to: {goal}')


@bot.command()
async def profile(ctx, member: discord.Member = None):
    # If no member is mentioned, default to the command author
    member = member or ctx.author
    
    user_id = str(member.id)
    user_logs = logs.get(user_id, [])
    recent_logs = user_logs[-5:]  # Get the last 5 logs
    formatted_logs = "\n".join(f"{entry['date']}: {entry['message']}" for entry in recent_logs)
    user_goal = goals.get(user_id, 'No goal set')

    avatar_url = member.avatar.url
    response = requests.get(avatar_url)
    Image.open(BytesIO(response.content))

    color_thief = ColorThief(BytesIO(response.content))
    dominant_color = color_thief.get_color(quality=1)

    discord_color = discord.Color.from_rgb(*dominant_color)

    embed = discord.Embed(title=f"{member.name}'s Profile", color=discord_color)
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="Recent Logs", value=formatted_logs or "No logs available", inline=False)
    embed.add_field(name="Goal", value=user_goal, inline=False)

    await ctx.send(embed=embed)

#needs to be fixed
BOARD_WIDTH = 20
BOARD_HEIGHT = 10
PADDLE_HEIGHT = 3
BALL_SYMBOL = "⚪"
PADDLE_SYMBOL = "▓"
EMPTY_SYMBOL = "⬛"
EMBED_COLOR = 0x00ff00

ball_x = BOARD_WIDTH // 2
ball_y = BOARD_HEIGHT // 2
ball_dx = 1
ball_dy = 1
left_paddle_y = BOARD_HEIGHT // 2 - PADDLE_HEIGHT // 2
right_paddle_y = BOARD_HEIGHT // 2 - PADDLE_HEIGHT // 2
left_score = 0
right_score = 0
game_board = []
game_active = False

def create_board():
    global game_board
    game_board = [[EMPTY_SYMBOL for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def update_board():
    create_board()
    
    for i in range(PADDLE_HEIGHT):
        if 0 <= left_paddle_y + i < BOARD_HEIGHT:
            game_board[left_paddle_y + i][0] = PADDLE_SYMBOL
        if 0 <= right_paddle_y + i < BOARD_HEIGHT:
            game_board[right_paddle_y + i][BOARD_WIDTH-1] = PADDLE_SYMBOL
    
    if 0 <= ball_y < BOARD_HEIGHT and 0 <= ball_x < BOARD_WIDTH:
        game_board[ball_y][ball_x] = BALL_SYMBOL

def format_board():
    board_str = f"Score: {left_score} - {right_score}\n\n"
    for row in game_board:
        board_str += "".join(row) + "\n"
    return board_str

async def move_ball():
    global ball_x, ball_y, ball_dx, ball_dy, left_score, right_score, game_active

    ball_x += ball_dx
    ball_y += ball_dy

    if ball_y <= 0 or ball_y >= BOARD_HEIGHT - 1:
        ball_dy *= -1

    if ball_x == 1 and left_paddle_y <= ball_y < left_paddle_y + PADDLE_HEIGHT:
        ball_dx *= -1
    elif ball_x == BOARD_WIDTH-2 and right_paddle_y <= ball_y < right_paddle_y + PADDLE_HEIGHT:
        ball_dx *= -1

    if ball_x < 0:
        right_score += 1
        ball_x = BOARD_WIDTH // 2
        ball_y = BOARD_HEIGHT // 2
    elif ball_x >= BOARD_WIDTH:
        left_score += 1
        ball_x = BOARD_WIDTH // 2
        ball_y = BOARD_HEIGHT // 2

    if left_score >= 5 or right_score >= 5:
        game_active = False
        return True
    return False

@bot.command()
async def pong(ctx):
    global game_active, left_score, right_score
    
    if game_active:
        await ctx.send("A game is already in progress!")
        return

    try:
        left_score = 0
        right_score = 0
        game_active = True
        
        create_board()
        embed = discord.Embed(description=format_board(), color=EMBED_COLOR)
        game_message = await ctx.send(embed=embed)

        controls = ['⬆️', '⬇️', '🔼', '🔽', '❌']
        for control in controls:
            try:
                await game_message.add_reaction(control)
            except discord.errors.Forbidden:
                await ctx.send("I don't have permission to add reactions!")
                game_active = False
                return

        while game_active:
            try:
                update_board()
                game_over = await move_ball()
                
                if game_over:
                    winner = "Left" if left_score >= 5 else "Right"
                    embed = discord.Embed(title=f"Game Over! {winner} player wins!", 
                                        description=format_board(), 
                                        color=EMBED_COLOR)
                else:
                    embed = discord.Embed(description=format_board(), color=EMBED_COLOR)
                
                await game_message.edit(embed=embed)
                await asyncio.sleep(1)
            except discord.errors.NotFound:
                game_active = False
                await ctx.send("Game message was deleted. Game ended.")
                break
            except Exception as e:
                game_active = False
                await ctx.send(f"An error occurred: {str(e)}")
                break
                
    except Exception as e:
        game_active = False
        await ctx.send(f"An error occurred: {str(e)}")


@bot.event
async def on_reaction_add(reaction, user):
    global left_paddle_y, right_paddle_y, game_active
    
    if user.bot or not game_active:
        return

    if reaction.emoji == '⬆️' and left_paddle_y > 0:
        left_paddle_y -= 1
    elif reaction.emoji == '⬇️' and left_paddle_y < BOARD_HEIGHT - PADDLE_HEIGHT:
        left_paddle_y += 1
    elif reaction.emoji == '🔼' and right_paddle_y > 0:
        right_paddle_y -= 1
    elif reaction.emoji == '🔽' and right_paddle_y < BOARD_HEIGHT - PADDLE_HEIGHT:
        right_paddle_y += 1
    elif reaction.emoji == '❌':
        game_active = False

    await reaction.remove(user)
    
bot.run('tokenjak')
