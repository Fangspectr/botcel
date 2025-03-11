import discord
from discord.ext import commands
import json
import os
from datetime import datetime
from colorthief import ColorThief
from PIL import Image
import requests
from io import BytesIO
import random
import asyncio
from PIL import Image, ImageDraw, ImageFont
import io
import imageio
import numpy as np



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

class MainCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def log(self, ctx, *, message: str):
        user_id = str(ctx.author.id)
        if user_id not in logs:
            logs[user_id] = []
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_entry = {"date": current_date, "message": message}
        logs[user_id].append(log_entry)
        with open('logs.json', 'w') as f:
            json.dump(logs, f, indent=4)
        await ctx.send(f'Logged your message:\n\n{current_date}: {message}')

    @commands.command()
    async def progress(self, ctx):
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

    @commands.command()
    async def goal(self, ctx, *, goal: str):
        user_id = str(ctx.author.id)
        if user_id not in goals:
            goals[user_id] = []
        goals[user_id].append(goal)
        with open('goals.json', 'w') as f:
            json.dump(goals, f, indent=4)
        await ctx.send(f'Added new goal: {goal}')

    @commands.command()
    async def delete(self, ctx, type_: str, index: int):
        user_id = str(ctx.author.id)
        type_ = type_.lower()

        if type_ not in ['log', 'goal']:
            await ctx.send('Please specify either "log" or "goal" as the type to delete.')
            return

        if type_ == 'log':
            if user_id in logs and logs[user_id]:
                if 0 < index <= len(logs[user_id]):
                    del logs[user_id][index - 1] 
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
                    del goals[user_id][index - 1]
                    with open('goals.json', 'w') as f:
                        json.dump(goals, f, indent=4)
                    await ctx.send(f'Deleted goal at index {index}.')
                else:
                    await ctx.send('Invalid goal index.')
            else:
                await ctx.send('No goals found for this user.')


    @commands.command()
    async def deleteall(self, ctx):
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

    @commands.command()
    async def help(self, ctx): # Corrected help command
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
                - example: `!deleteall`

            6. !profile [@user]: view your profile or another user's profile, including recent logs and goals.
                - example: `!profile` or `!profile @username`

            7. !help: display this helper menu.
                - example: `!help`
                ```
        """
        await ctx.send(help_message)


    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
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

    @commands.command()
    async def ol(self, ctx, times: int = 1):
        if times > 20:
            await ctx.send("nah bruh u can only request up to 20 oilans at a time.")
            return

        image_url = "https://media.discordapp.net/attachments/1327892921571213352/1348737334237073430/caption.png?ex=67d08d06&is=67cf3b86&hm=761b717b530d1fb052d7350155515320faeac687184d36fe46cffd6d7fbe198f&=&format=webp&quality=lossless&width=150&height=257"

        try:
            for _ in range(times):
                response = requests.get(image_url)
                if response.status_code == 200:
                    image = BytesIO(response.content)
                    file = discord.File(image, filename="image.png")
                    await ctx.send(file=file)
                else:
                    await ctx.send("Failed to fetch the image from the URL.")
                    break

                await asyncio.sleep(1)
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    async def darshify(self, ctx, *, message: str):
        try:
            words = message.split()
            special_words = ['boves', 'jyrong', 'rus', 'lan']
            suffixes = ['jak', 'cel', 'braham', 'vit']

            for i in range(random.randint(1, 3)):
                words.insert(random.randint(0, len(words)), random.choice(special_words))

            for i in range(len(words)):
                if random.choice([True, False]):
                    words[i] = ''.join(random.choice([char.upper(), char]) for char in words[i])
                if random.choice([True, False]):
                    words[i] = words[i] + random.choice(suffixes)

            darshified = ' '.join(words)

            if len(darshified) > 2000:
                third = len(darshified) // 3
                first_part = darshified[:third]
                second_part = darshified[third: third * 2]
                third_part = darshified[third * 2:]

                await ctx.send(first_part)
                await ctx.send(second_part)
                await ctx.send(third_part)
            else:
                await ctx.send(darshified)

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    async def knum(self, ctx, number_input: str):
        try:
            def kaprekar_routine(num_str):
                sequence = [int(num_str)]
                num = int(num_str)
                for _ in range(100):
                    str_num = str(num).zfill(4)
                    digits_asc = "".join(sorted(str_num))
                    digits_desc = "".join(sorted(str_num, reverse=True))
                    num_asc = int(digits_asc)
                    num_desc = int(digits_desc)
                    num = num_desc - num_asc
                    sequence.append(num)
                    if num == 6174 or num == 0:
                        break
                return sequence

            if not number_input.isdigit() or len(number_input) > 5:
                await ctx.send("Please enter a valid number with at most 5 digits.")
                return

            number = number_input.zfill(4) 
            if len(set(number)) < 2:
                await ctx.send("Please enter a number with at least two different digits.")
                return

            sequence = kaprekar_routine(number)
            sequence_str = " -> ".join(map(str, sequence))
            await ctx.send(f"Kaprekar's Routine for {number_input}:\n{sequence_str}")

        except ValueError:
            await ctx.send("Invalid input. Please enter a number.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")


    @commands.command()
    async def caption(self, ctx, *, text: str):
        try:
            if not ctx.message.attachments:
                await ctx.send("Please attach an image or GIF to add a caption.")
                return

            attachment = ctx.message.attachments[0]
            if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                await ctx.send("Please attach a valid image or GIF file (PNG, JPG, JPEG, GIF, BMP).")
                return

            image_bytes = await attachment.read()
            image_stream = io.BytesIO(image_bytes)

            if attachment.filename.lower().endswith('.gif'):
                try:
                    gif_image = Image.open(image_stream)
                    frames = []
                    for i in range(gif_image.n_frames):
                        gif_image.seek(i)
                        frame = gif_image.copy().convert("RGB")
                        modified_frame = self.add_caption_to_image(frame, text)
                        frames.append(np.array(modified_frame)) 

                    output_buffer = io.BytesIO()
                    imageio.mimsave(output_buffer, frames, format='gif', fps=15)
                    output_buffer.seek(0)
                    await ctx.send(file=discord.File(fp=output_buffer, filename="captioned_gif.gif"))

                except Exception as gif_e:
                    print(f"GIF processing error: {gif_e}") 
                    await ctx.send(f"Error processing GIF: {gif_e}")
                    return

            else:
                image = Image.open(image_stream)
                modified_image = self.add_caption_to_image(image, text)

                output_buffer = io.BytesIO()
                modified_image.save(output_buffer, format="PNG")
                output_buffer.seek(0)

                await ctx.send(file=discord.File(fp=output_buffer, filename="captioned_image.png"))

        except Exception as e:
            print(f"General caption error: {e}") 
            await ctx.send(f"An error occurred: {e}")

    def add_caption_to_image(self, image, text):
        caption_height = 60
        font_size = 40

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        new_image = Image.new("RGB", (image.width, image.height + caption_height), "white")
        draw = ImageDraw.Draw(new_image)

        bbox = draw.textbbox((0, 0), text, font=font) 
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1] 
        text_position = ((new_image.width - text_width) // 2, 10)

        draw.text(text_position, text, fill="black", font=font)
        new_image.paste(image, (0, caption_height))

        return new_image

async def setup(bot):
    await bot.add_cog(MainCommandsCog(bot))
