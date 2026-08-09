# ====================================================================================
# 💟 Reach Out @LazyDeveloperr 💟
# ------------------------------------------------------------------------------------
# 👑 Lead Engineer : Intkhab Ahmad (@LazyDeveloperr)
# 🐙 GitHub        : https://github.com/LazyDeveloperr
# 📸 Instagram     : https://instagram.com/LazyDeveloperr
# 📢 Telegram      : https://telegram.me/LazyDeveloperr
# ------------------------------------------------------------------------------------
# ✨ Features & Fixes in this Module:
#   🎧 Spotify song, album, and playlist link support
#   🚀 Works smoothly without needing any Spotify API keys
# ====================================================================================

import base64
import re
import aiohttp
from LazyDeveloperr import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, logger


class SpotifyAPI:
    def __init__(self):
        self.client_id = (SPOTIFY_CLIENT_ID or "").strip().strip('"').strip("'")
        self.client_secret = (SPOTIFY_CLIENT_SECRET or "").strip().strip('"').strip("'")
        self.token = None

    async def get_token(self):
        if not self.client_id or not self.client_secret:
            logger.warning("[Spotify] SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET is not set! Spotify search disabled. Set these env vars to enable accurate song matching.")
            return None
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://accounts.spotify.com/api/token",
                    data={"grant_type": "client_credentials"},
                    headers={
                        "Authorization": f"Basic {auth_header}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    timeout=aiohttp.ClientTimeout(total=10.0),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.token = data.get("access_token")
                        return self.token
                    else:
                        resp_body = await resp.text()
                        logger.warning(f"[Spotify] Token request failed: HTTP {resp.status} - {resp_body}")
        except Exception as e:
            logger.error(f"[Spotify] Error fetching token: {e}")
        return None

    def valid(self, url: str) -> bool:
        return "open.spotify.com" in url or "spotify:" in url

    async def oembed_track(self, url: str) -> str | None:
        """Public oEmbed fallback for single tracks (Requires NO API credentials)."""
        try:
            oembed_url = f"https://open.spotify.com/oembed?url={url}"
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    oembed_url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=aiohttp.ClientTimeout(total=8.0)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        title = data.get("title", "")
                        artist = data.get("author_name", "")
                        if title:
                            res = f"{title} {artist}".strip()
                            logger.info(f"[Spotify oEmbed] Resolved track: {res}")
                            return res
        except Exception as e:
            logger.warning(f"[Spotify oEmbed] Error: {e}")
        return None

    async def track(self, url: str):
        token = await self.get_token()
        if token:
            match = re.search(r"track[/:]([a-zA-Z0-9]+)", url)
            if match:
                track_id = match.group(1)
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"https://api.spotify.com/v1/tracks/{track_id}",
                            headers={"Authorization": f"Bearer {token}"},
                            timeout=aiohttp.ClientTimeout(total=8.0),
                        ) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                artist = data["artists"][0]["name"] if data.get("artists") else ""
                                name = data.get("name", "")
                                return f"{name} {artist}".strip()
                except Exception as e:
                    logger.error(f"Error fetching Spotify track via API: {e}")

        # Public oEmbed Fallback when API token fails / missing
        return await self.oembed_track(url)

    async def playlist(self, url: str):
        token = await self.get_token()
        if token:
            match = re.search(r"(?:playlist|album)[/:]([a-zA-Z0-9]+)", url)
            if match:
                playlist_id = match.group(1)
                is_album = "album" in url
                endpoint = f"https://api.spotify.com/v1/albums/{playlist_id}/tracks" if is_album else f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            endpoint,
                            headers={"Authorization": f"Bearer {token}"},
                            timeout=aiohttp.ClientTimeout(total=10.0),
                        ) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                results = []
                                items = data.get("items", []) if is_album else [i.get("track") for i in data.get("items", []) if i.get("track")]
                                for track in items:
                                    if track:
                                        artist = track["artists"][0]["name"] if track.get("artists") else ""
                                        name = track.get("name", "")
                                        results.append(f"{name} {artist}".strip())
                                if results:
                                    return results
                except Exception as e:
                    logger.error(f"Error fetching Spotify playlist/album via API: {e}")

        # Public Scraper Fallback for Playlists / Albums
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                    timeout=aiohttp.ClientTimeout(total=10.0)
                ) as resp:
                    if resp.status == 200:
                        page_text = await resp.text()
                        track_ids = re.findall(r"https://open\.spotify\.com/track/([a-zA-Z0-9]+)", page_text)
                        unique_ids = list(dict.fromkeys(track_ids))
                        logger.info(f"[Spotify Scraper] Found {len(unique_ids)} track IDs in playlist/album")
                        results = []
                        for tid in unique_ids[:20]:  # Fetch first 20 tracks
                            t_info = await self.oembed_track(f"https://open.spotify.com/track/{tid}")
                            if t_info:
                                results.append(t_info)
                        return results
        except Exception as e:
            logger.error(f"Error scraping Spotify playlist/album page: {e}")

        return []

    async def album(self, url: str):
        return await self.playlist(url)

    async def search_track(self, query: str):
        token = await self.get_token()
        if not token:
            return None
        import urllib.parse
        q = urllib.parse.quote(query)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.spotify.com/v1/search?q={q}&type=track&limit=1",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        tracks = data.get("tracks", {}).get("items", [])
                        if tracks:
                            t = tracks[0]
                            artist = t["artists"][0]["name"] if t.get("artists") else ""
                            name = t.get("name", "")
                            duration_ms = t.get("duration_ms", 0)
                            images = t.get("album", {}).get("images", [])
                            thumb = images[0]["url"] if images else ""
                            url = t.get("external_urls", {}).get("spotify", "")
                            return {
                                "title": name,
                                "artist": artist,
                                "query": f"{name} {artist}".strip(),
                                "duration_ms": duration_ms,
                                "duration_sec": int(duration_ms / 1000),
                                "duration_str": f"{int((duration_ms / 1000) // 60)}:{int((duration_ms / 1000) % 60):02d}",
                                "thumbnail": thumb,
                                "url": url,
                                "id": t.get("id", ""),
                            }
        except Exception as e:
            logger.error(f"Error searching Spotify track: {e}")
        return None


spotify = SpotifyAPI()
