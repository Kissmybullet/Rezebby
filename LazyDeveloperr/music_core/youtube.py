# ====================================================================================
# 💟 Reach Out @LazyDeveloperr 💟
# ------------------------------------------------------------------------------------
# 👑 Lead Engineer : Intkhab Ahmad (@LazyDeveloperr)
# 🐙 GitHub        : https://github.com/LazyDeveloperr
# 📸 Instagram     : https://instagram.com/LazyDeveloperr
# 📢 Telegram      : https://telegram.me/LazyDeveloperr
# ------------------------------------------------------------------------------------
# ✨ Features & Fixes in this Module:
#   🎯 Fixed short song title searches (like "Her", "Run", "Die") playing wrong songs
# ====================================================================================

import asyncio
import os
import random
import re
import urllib.parse

import aiohttp
from py_yt import Playlist, Recommendations, VideosSearch

from LazyDeveloperr import logger
from LazyDeveloperr.music_helpers import Track, utils

# Use environment variables for configuration
API_URL = os.getenv("API_URL", "").rstrip("/")
API_KEY = os.getenv("API_KEY", "")


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.cookie_dir = "LazyDeveloperr/cookies"
        self.warned = False
        self._recent_prefetches = {}  # vidid -> timestamp
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        self.iregex = re.compile(
            r"https?://(?:www\.|m\.|music\.)?(?:youtube\.com|youtu\.be)"
            r"(?!/(watch\?v=[A-Za-z0-9_-]{11}|shorts/[A-Za-z0-9_-]{11}"
            r"|playlist\?list=PL[A-Za-z0-9_-]+|[A-Za-z0-9_-]{11}))\S*"
        )
        self._client = None

    async def get_client(self):
        if self._client is None or self._client.closed:
            self._client = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=600.0, connect=10.0)
            )
        return self._client

    def get_cookies(self):
        self.cookies = []
        possible_paths = [
            "cookies.txt",
            "cookie.txt",
            self.cookie_dir,
            "cookies",
            "LazyDeveloperr/cookies.txt",
            "LazyDeveloperr/cookies/cookies.txt",
            os.path.join(os.getcwd(), "cookies.txt"),
            os.path.join(os.getcwd(), "cookie.txt"),
        ]
        for p in possible_paths:
            if os.path.isfile(p):
                self.cookies.append(p)
            elif os.path.isdir(p) and os.path.exists(p):
                for file in os.listdir(p):
                    if file.endswith(".txt"):
                        self.cookies.append(os.path.join(p, file))

        if self.cookies:
            cookie_path = random.choice(self.cookies)
            logger.info(f"[Cookies] Found cookie file: {cookie_path}")
            return cookie_path
        logger.warning("[Cookies] No cookies.txt found in root or cookie directories!")
        return None

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        async with aiohttp.ClientSession() as session:
            for url in urls:
                name = url.split("/")[-1]
                link = "https://batbin.me/raw/" + name
                async with session.get(link) as resp:
                    resp.raise_for_status()
                    with open(f"{self.cookie_dir}/{name}.txt", "wb") as fw:
                        fw.write(await resp.read())
        logger.info(f"Cookies saved in {self.cookie_dir}.")

    def valid(self, url: str) -> bool:
        from LazyDeveloperr.music_core.spotify import spotify
        return bool(re.match(self.regex, url)) or spotify.valid(url)

    def invalid(self, url: str) -> bool:
        from LazyDeveloperr.music_core.spotify import spotify
        if spotify.valid(url):
            return False
        return bool(re.match(self.iregex, url))

    def _clean_link(self, link: str):
        if not link:
            return ""
        link = str(link)
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]
        return link

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        from LazyDeveloperr.music_core.spotify import spotify

        # Step 1: Spotify Web API (PRIMARY SEARCH ENGINE for metadata)
        try:
            sp_res = None
            if "open.spotify.com" in query or "spotify:" in query:
                if "track" in query:
                    sp_title = await spotify.track(query)
                    if sp_title:
                        sp_res = await spotify.search_track(sp_title)
            else:
                sp_res = await spotify.search_track(query)

            if sp_res:
                sp_artist = sp_res.get("artist") or ""
                sp_song_name = sp_res.get("title") or ""
                logger.info(f"[Spotify] Found: {sp_song_name} by {sp_artist}")
                return Track(
                    id=sp_res.get("id") or ("sp_" + re.sub(r"[^\w]", "", sp_song_name)),
                    channel_name=sp_artist or "Spotify",
                    duration=sp_res.get("duration_str") or "03:30",
                    duration_sec=sp_res.get("duration_sec") or 210,
                    message_id=m_id,
                    title=sp_song_name,
                    thumbnail=sp_res.get("thumbnail") or "",
                    url=sp_res.get("url") or "",
                    view_count="",
                    video=video,
                    artist=sp_artist,
                )
        except Exception as sp_err:
            logger.warning(f"[Spotify] Search failed: {sp_err}. Falling back to JioSaavn.")

        # Step 2: JioSaavn Direct API Search (fallback when Spotify fails/unavailable)
        try:
            client = await self.get_client()
            safe_q = urllib.parse.quote(query)
            jio_api = f"https://www.jiosaavn.com/api.php?__call=search.getResults&q={safe_q}&_format=json&p=1&n=10"
            async with client.get(jio_api, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}) as resp:
                if resp.status == 200:
                    res_data = await resp.json(content_type=None)
                    results = res_data.get("results", [])
                    _bad = re.compile(r"(?i)\b(karaoke|instrumental|cover|tribute|originally performed)\b")
                    valid_item = None
                    for r in results:
                        song_name = r.get("song") or r.get("title") or ""
                        if r.get("encrypted_media_url") and not _bad.search(song_name):
                            valid_item = r
                            break
                    if not valid_item and results:
                        valid_item = results[0]

                    if valid_item:
                        dur = int(valid_item.get("duration", 0) or 0)
                        dur_str = f"{dur // 60}:{dur % 60:02d}"
                        image_url = valid_item.get("image", "")
                        if image_url:
                            image_url = image_url.replace("150x150", "500x500").replace("50x50", "500x500")
                        artists = valid_item.get("primary_artists") or valid_item.get("singers") or "JioSaavn"
                        song_title = valid_item.get("song") or valid_item.get("title") or query
                        logger.info(f"[JioSaavn] Fallback found: {song_title} by {artists}")
                        return Track(
                            id=valid_item.get("id"),
                            channel_name=artists,
                            duration=dur_str,
                            duration_sec=dur,
                            message_id=m_id,
                            title=song_title[:60],
                            thumbnail=image_url,
                            url=valid_item.get("perma_url") or f"https://www.jiosaavn.com/song/{valid_item.get('id')}",
                            view_count="",
                            video=video,
                            artist=artists,
                        )
        except Exception as jio_err:
            logger.warning(f"[JioSaavn] Fallback search failed: {jio_err}")

        logger.error(f"[Search] All engines failed for query: {query!r}")
        return None


    async def playlist(
        self, limit: int, user: str, url: str, video: bool
    ) -> list[Track | None]:
        url = self._clean_link(url)
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist["videos"][:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration") or "00:00"),
                    title=data.get("title")[:40],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url", "").split("?")[0],
                    url=data.get("link", "").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except Exception as e:
            logger.error(f"Playlist error: {e}")
        return tracks

    async def prefetch(self, link: str, video: bool = False):
        return True

    async def get_related(
        self, video_id: str, video: bool = False, max_duration: int = 0
    ) -> Track | None:
        try:
            _results = await Recommendations.getRelated(video_id)
            if not isinstance(_results, dict):
                return None
            results = _results.get("result")
            if results:
                videos = [r for r in results if r.get("type") == "video"]
                if max_duration:
                    videos = [
                        v
                        for v in videos
                        if utils.to_seconds(v.get("duration") or "00:00")
                        <= max_duration
                    ]
                if not videos:
                    return None
                data = random.choice(videos)
                return Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name"),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration") or "00:00"),
                    title=data.get("title")[:40],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url", "").split("?")[0],
                    url=data.get("link"),
                    user="Autoplay",
                    video=video,
                )
        except Exception as e:
            logger.error(f"Error fetching related videos: {e}")
        return None

    async def download(self, video_id: str, video: bool = False, title: str = None, artist: str = None) -> str | None:
        import glob
        raw_query = title or video_id
        # Preserve artist in the search query - only strip noise keywords
        clean_q = re.sub(r"(?i)\b(official|full song|video|hd|4k|lyric|lyrics|video song)\b", "", raw_query)
        clean_q = re.sub(r"[\|\[\(\]\)]", " ", clean_q)
        clean_q = " ".join(clean_q.split())
        search_query = clean_q if clean_q else raw_query

        # Build the precise artist+title query for best match
        # artist is only trusted when it came from Spotify (verified source)
        # When artist comes from JioSaavn fallback it may be unreliable
        has_trusted_artist = bool(artist) and "," not in (artist or "")  # Spotify gives single artist; JioSaavn gives comma-separated
        if has_trusted_artist and artist.lower() not in (title or "").lower():
            artist_title_query = f"{title} {artist}".strip() if title else search_query
            sc_query = f'"{artist}" "{title}"' if title else search_query
        else:
            # Unknown/unreliable artist - use clean title only for best popular match
            artist_title_query = search_query
            sc_query = search_query


        os.makedirs("downloads", exist_ok=True)

        safe_name = re.sub(r"[^\w\-_]", "_", video_id)
        for ext in ("webm", "mp3", "m4a", "mp4", "mkv", "opus", "ogg"):
            cached = os.path.join("downloads", f"{safe_name}.{ext}")
            if os.path.exists(cached) and os.path.getsize(cached) > 65536:
                logger.info(f"Cache hit: {cached}")
                return cached

        loop = asyncio.get_event_loop()

        # Stage 1: JioSaavn Official API DES 320kbps MP3 Extractor (audio only)
        if not video:
            try:
                target_mp3 = os.path.join("downloads", f"{safe_name}.mp3")
                client = await self.get_client()

                enc_url = None

                # Step 1A: JioSaavn search with ARTIST+TITLE combined query (n=10 for better matching)
                safe_q = urllib.parse.quote(artist_title_query)
                jio_api = f"https://www.jiosaavn.com/api.php?__call=search.getResults&q={safe_q}&_format=json&p=1&n=10"
                async with client.get(jio_api, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}) as resp:
                    if resp.status == 200:
                        res_data = await resp.json(content_type=None)
                        results = res_data.get("results", [])

                        # Patterns to ALWAYS reject (karaoke, instrumental, cover, originally performed)
                        _bad = re.compile(r"(?i)\b(karaoke|instrumental|cover|tribute|originally performed)\b")

                        artist_lower = (artist or "").lower() if has_trusted_artist else ""
                        title_lower = (title or "").lower()
                        best = None

                        for r in results:
                            r_song = (r.get("song") or r.get("title") or "").lower()
                            r_artists = (r.get("primary_artists") or r.get("singers") or "").lower()
                            has_enc = bool(r.get("encrypted_media_url"))

                            # Skip karaoke / instrumental / cover versions
                            if _bad.search(r_song):
                                continue

                            clean_words = [w for w in re.findall(r"\w+", title_lower) if len(w) > 1 and w not in ("feat", "featuring", "remix", "version", "official", "audio", "video")]
                            title_match = any(w in r_song for w in clean_words) if clean_words else title_lower in r_song
                            artist_match = artist_lower and artist_lower in r_artists

                            if has_enc and has_trusted_artist and artist_match and title_match:
                                best = r  # Perfect Spotify-verified match
                                break
                            if has_enc and title_match and not best:
                                best = r  # Title match, keep searching for better

                        if not best:
                            # Last resort: first result that isn't karaoke/instrumental
                            for r in results:
                                r_song = (r.get("song") or r.get("title") or "").lower()
                                if r.get("encrypted_media_url") and not _bad.search(r_song):
                                    best = r
                                    break

                        if best:
                            enc_url = best.get("encrypted_media_url")
                            logger.info(f"[Music] JioSaavn matched: {best.get('song')} by {best.get('primary_artists')}")




                if enc_url:
                            raw_mp3_url = ""
                            try:
                                import base64
                                data_bytes = base64.b64decode(enc_url)
                                key_bytes = b"38346591"

                                # Method 1: Crypto.Cipher (pycryptodome)
                                try:
                                    from Crypto.Cipher import DES
                                    cipher = DES.new(key_bytes, DES.MODE_ECB)
                                    dec_b = cipher.decrypt(data_bytes)
                                    pad = dec_b[-1]
                                    raw_mp3_url = dec_b[:-pad].decode("utf-8")
                                except Exception:
                                    pass

                                # Method 2: cryptography
                                if not raw_mp3_url:
                                    try:
                                        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                                        from cryptography.hazmat.backends import default_backend
                                        cipher = Cipher(algorithms.TripleDES(key_bytes * 3), modes.ECB(), backend=default_backend())
                                        decryptor = cipher.decryptor()
                                        dec_b = decryptor.update(data_bytes) + decryptor.finalize()
                                        pad = dec_b[-1]
                                        raw_mp3_url = dec_b[:-pad].decode("utf-8")
                                    except Exception:
                                        pass

                                # Method 3: pyDes
                                if not raw_mp3_url:
                                    try:
                                        import pyDes
                                        cipher = pyDes.des(key_bytes, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
                                        raw_mp3_url = cipher.decrypt(data_bytes).decode("utf-8")
                                    except Exception:
                                        pass

                                if raw_mp3_url:
                                    # Try 320kbps first, then fall back to 160kbps
                                    for quality in ("_320.mp4", "_160.mp4", "_96.mp4"):
                                        attempt_url = re.sub(r"_(96|128|160|320)\.mp4", quality, raw_mp3_url)
                                        try:
                                            async with client.get(attempt_url, headers={"User-Agent": "Mozilla/5.0"}) as audio_resp:
                                                if audio_resp.status == 200:
                                                    # Stream in chunks to avoid incomplete silent file
                                                    with open(target_mp3, "wb") as f:
                                                        async for chunk in audio_resp.content.iter_chunked(65536):
                                                            f.write(chunk)
                                                    if os.path.exists(target_mp3) and os.path.getsize(target_mp3) > 65536:
                                                        logger.info(f"[Music] JioSaavn {quality} MP3 success: {target_mp3}")
                                                        return target_mp3
                                                    else:
                                                        os.remove(target_mp3)
                                        except Exception:
                                            continue
                            except Exception as dec_err:
                                logger.warning(f"JioSaavn decryption error: {dec_err}")
            except Exception as jio_err:
                logger.warning(f"JioSaavn direct download failed: {jio_err}")

        def _download():
            import yt_dlp

            def get_matching_file():
                matches = glob.glob(os.path.join("downloads", f"{safe_name}.*"))
                valid = [f for f in matches if not f.endswith((".jpg", ".png", ".json", ".part", ".ytdl")) and os.path.getsize(f) > 0]
                return valid[0] if valid else None

            # Strategy 2: SoundCloud Search - sc_query built in outer scope with verified artist info
            sc_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join("downloads", f"{safe_name}.%(ext)s"),
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "socket_timeout": 15,
            }
            try:
                logger.info(f"[Music] SoundCloud search: {sc_query}")
                with yt_dlp.YoutubeDL(sc_opts) as sc_ydl:
                    sc_ydl.extract_info(f"scsearch1:{sc_query}", download=True)
            except Exception as sc_err:
                logger.warning(f"[Music] SoundCloud download failed ({sc_err}).")

            return get_matching_file()

        try:
            file_path = await loop.run_in_executor(None, _download)
            if file_path and os.path.exists(file_path):
                return file_path
        except Exception as e:
            logger.error(f"SoundCloud download failed for {video_id}: {e}")

        return None

    async def close(self):
        if self._client and not self._client.closed:
            await self._client.close()
