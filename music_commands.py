import discord
from discord.ext import commands
import youtube_dl
import yt_dlp as youtube_dl 
import asyncio

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer): 
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class MusicCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel"""
        if not ctx.author.voice:
            return await ctx.send("You are not connected to a voice channel.")
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command()
    async def ed(self, ctx):
        """Plays Castle on the Hill"""
        if ctx.author.voice is None:
            return await ctx.send("You must be in a voice channel to use this command.")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)
        try:
            async with ctx.typing():
                url = "https://www.youtube.com/watch?v=7Qp5vcuMIlk"  # Direct link
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True) # use self.bot.loop
                ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            await ctx.send(f'Now playing: {player.title}')
        except Exception as e:
            print(f"Error playing song: {e}")
            await ctx.send(f"There was an error playing the song: {e}")

    @commands.command()
    async def leave(self, ctx):
        """Leaves the voice channel"""
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            await ctx.send("Leaving voice channel.")
        else:
            await ctx.send("I am not in a voice channel.")

    @commands.command()
    async def pause(self, ctx):
        """Pauses the music"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused the music.")
        else:
            await ctx.send("No music is currently playing.")

    @commands.command()
    async def resume(self, ctx):
        """Resumes the music"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed the music.")
        else:
            await ctx.send("Music is not paused.")

    @commands.command()
    async def stop(self, ctx):
        """Stops the music"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Stopped the music.")
        else:
            await ctx.send("No music is currently playing.")

# --- Cog setup function ---
async def setup(bot):
    await bot.add_cog(MusicCommandsCog(bot))
