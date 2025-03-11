import discord
from discord.ext import commands
import asyncio 

TOKEN = 'puturtoken'

intents = discord.Intents.default()
intents.dm_messages = True
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.load_extension("main_commands") 
    await bot.load_extension("music_commands") 

async def main(): 
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main()) 

