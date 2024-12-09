import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=os.getenv("PREFIX", "/"),
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        try:
            await self.load_extension("cogs.spotify")  # Load spotify.py under cogs
            synced_commands = await self.tree.sync()
            print(f"Successfully synced {len(synced_commands)} commands globally:")
            for cmd in synced_commands:
                print(f" - {cmd.name}: {cmd.description}")
        except Exception as e:
            print(f"Error during command sync: {e}")


bot = DiscordBot()

@bot.event
async def on_ready():
    print(f"Bot is online and logged in as {bot.user}")

bot.run(os.getenv("TOKEN"))
