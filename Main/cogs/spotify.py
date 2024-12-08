"""
Spotify Search Cog for Discord Bot
"""

import discord
from discord.ext import commands
from discord import app_commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os


class SpotifyCog(commands.Cog, name="spotify"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("SpotifyCog is initialized")
        self.spotify = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            )
        )

    @app_commands.command(
        name="search_artist", description="Search for an artist on Spotify."
    )
    @app_commands.describe(artist_name="The name of the artist to search for")
    async def search_artist(
        self, interaction: discord.Interaction, artist_name: str
    ) -> None:
        """
        Search for an artist on Spotify and return their details.

        :param interaction: The command interaction.
        :param artist_name: The name of the artist to search for.
        """
        await interaction.response.defer()  # Show processing indicator
        try:
            results = self.spotify.search(q=f"artist:{artist_name}", type="artist", limit=1)
            if results["artists"]["items"]:
                artist = results["artists"]["items"][0]
                embed = discord.Embed(
                    title=artist["name"],
                    description=f"**Followers:** {artist['followers']['total']}\n"
                                f"**Popularity:** {artist['popularity']}\n"
                                f"[Spotify Profile]({artist['external_urls']['spotify']})",
                    color=0x1DB954,
                )
                if artist.get("images"):
                    embed.set_thumbnail(url=artist["images"][0]["url"])
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(
                    content=f"No artist found for `{artist_name}`."
                )
        except Exception as e:
            await interaction.followup.send(
                content=f"An error occurred while searching for `{artist_name}`: {e}"
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SpotifyCog(bot))
    print("SpotifyCog has been added to the bot")
