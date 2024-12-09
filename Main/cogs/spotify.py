import discord
from discord.ext import commands
from discord import app_commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import random
from wheel.metadata import generate_requirements
from spotipy.oauth2 import SpotifyOAuth


class SpotifyCog(commands.Cog, name="spotify"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("SpotifyCog is initialized")
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri="http://localhost:8888",
            scope="playlist-modify-public"
        ))

    @app_commands.command(
        name="search_artist", description="Search for an artist on Spotify."
    )
    @app_commands.describe(artist_name="The name of the artist to search for")
    async def search_artist(
        self, interaction: discord.Interaction, artist_name: str
    ) -> None:
        # artist_name: The name of the artist to search for.
        await interaction.response.defer()
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
        except Exception:
            await interaction.followup.send(
                content=f"An error occurred."
            )

    @app_commands.command(
        name="top_songs", description="Get the top songs of a specific artist."
    )
    @app_commands.describe(artist_name="The name of the artist")
    async def top_songs(self, interaction: discord.Interaction, artist_name: str) -> None:
        await interaction.response.defer()
        try:
            # try to search for artist
            results = self.spotify.search(q=f"artist:{artist_name}", type="artist", limit=1)
            if not results["artists"]["items"]:
                await interaction.followup.send(
                    content=f"No artist found for `{artist_name}`."
                )
                return

            artist = results["artists"]["items"][0]
            artist_id = artist["id"]

            # if artist exists
            top_tracks = self.spotify.artist_top_tracks(artist_id)
            if not top_tracks["tracks"]:
                await interaction.followup.send(
                    content=f"No top songs found for `{artist_name}`."
                )
                return

            # bot response
            embed = discord.Embed(
                title=f"Top Songs by {artist['name']}",
                description="Here are the top tracks:",
                color=0x1DB954,
            )
            for idx, track in enumerate(top_tracks["tracks"][:10], start=1):
                embed.add_field(
                    name=f"{idx}. {track['name']}",
                    value=f"[Listen on Spotify]({track['external_urls']['spotify']})",
                    inline=False,
                )
            if artist.get("images"):
                embed.set_thumbnail(url=artist["images"][0]["url"])
            await interaction.followup.send(embed=embed)
        except Exception:
            await interaction.followup.send(
                content=f"An error occured."
            )

    @app_commands.command(
        name="trending", description="Find top artists by genre."
    )
    @app_commands.describe(genre="Which major genre?")
    async def trending(self, interaction: discord.Interaction, genre: str) -> None:
        await interaction.response.defer()
        try:
            results = self.spotify.search(q=f"genre:{genre}", type="artist", limit=5)

            if not results["artists"]["items"]:
                await interaction.followup.send(
                    content=f"No artists found for `{genre}`. Try major genres like pop, jazz, rock, etc."
                )
                return

            embed = discord.Embed(
                title=f"Trending Artists in {genre}",
                description="Here are some trending artists:",
            )
            for artist in results["artists"]["items"]:
                embed.add_field(
                    name=artist["name"],
                    value=f"[Spotify Link]({artist['external_urls']['spotify']})",
                    inline=False,
                )
            await interaction.followup.send(embed=embed)

        except Exception:
            await interaction.followup.send(
                content="An error occurred while searching."
            )
    @app_commands.command(
        name = "new_releases", description = "Find new releases by country."
    )
    @app_commands.describe(country="Which country?")
    async def new_releases(self, interaction: discord.Interaction, country: str) -> None:
        await interaction.response.defer()
        try:
            results = self.spotify.new_releases(country, limit = 10, offset = 0)
            if not results["albums"]["items"]:
                await interaction.followup.send(
                    content="Invalid country, try again."
                )
                return
            embed = discord.Embed(
                title = f"New Releases in  {country}",
                description="Here are some new releases:",
            )
            for release in results["albums"]["items"]:
                embed.add_field(
                    name = release["name"],
                    value = f"[Spotify Link]({release['external_urls']['spotify']})",
                    inline = False,
                )
            if results["albums"]["items"][0].get("images"):
                embed.set_thumbnail(url=results["albums"]["items"][0]["images"][0]["url"])

            await interaction.followup.send(embed=embed)

        except Exception:
            await interaction.followup.send(
                content="An error occurred."
            )

    @app_commands.command(
        name="create_playlist",
        description="Helps u create a playlist given an artist."
    )
    @app_commands.describe(artist_name="Name of the artist")
    async def create_playlist(self, interaction: discord.Interaction, artist_name: str):
        await interaction.response.defer()
        try:                                            # Search for the artist
            results = self.spotify.search(q=f'artist:{artist_name}', type='artist')
            if not results['artists']['items']:
                await interaction.followup.send("No artist found.")
                return

            artist = results['artists']['items'][0]
            artist_id = artist['id']
            albums = self.spotify.artist_albums(artist_id, album_type='album')
            album_ids = [album['id'] for album in albums['items']]
            all_tracks = []

            for album_id in album_ids:
                tracks = self.spotify.album_tracks(album_id)
                all_tracks.extend(tracks['items'])

            if not all_tracks:
                await interaction.followup.send(f"No tracks found for artist '{artist_name}'.")
                return

            random_tracks = random.sample(all_tracks, min(len(all_tracks), 10))
            track_uris = [track['uri'] for track in random_tracks]
            user_id = self.spotify.current_user()['id']
            playlist = self.spotify.user_playlist_create(user_id, f"Random {artist_name} Tracks") #playlist

            self.spotify.playlist_add_items(playlist['id'], track_uris) #add the tracks

            await interaction.followup.send(
                f"Playlist '{playlist['name']}' created successfully! [Open in Spotify]({playlist['external_urls']['spotify']})")

        except Exception:
            await interaction.followup.send("An error occurred.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SpotifyCog(bot))
    print("SpotifyCog has been added to the bot")
