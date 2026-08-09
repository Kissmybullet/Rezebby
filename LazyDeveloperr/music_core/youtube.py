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

        search_term = query.strip()

        # Step 1: Spotify Web API / Public oEmbed Resolution (If Spotify link or query)
        if spotify.valid(query) or "open.spotify.com" in query or "spotify:" in query:
            try:
                sp_title = await spotify.track(query)
                if sp_title:
                    search_term = sp_title
                    logger.info(f"[Spotify Resolved] Query '{query}' -> '{sp_title}'")
            except Exception as sp_err:
                logger.warning(f"[Spotify Track Resolve] Failed: {sp_err}")

        # Step 2: Primary Engine - YouTube VideosSearch for Exact Song Matching
        try:
            results = await VideosSearch(search_term, limit=5).next()
            if isinstance(results, dict) and results.get("result"):
                vids = results["result"]
                if vids:
                    item = vids[0]
                    vid_id = item.get("id")
                    vid_title = item.get("title", search_term)
                    channel = item.get("channel", {}).get("name", "YouTube")
                    dur = item.get("duration", "03:30")
                    dur_sec = utils.to_seconds(dur)
                    thumb = item.get("thumbnails", [{}])[-1].get("url", "").split("?")[0]
                    vid_url = item.get("link") or f"https://www.youtube.com/watch?v={vid_id}"

                    logger.info(f"[YouTube Search] Matched exact track: '{vid_title}' ({vid_id}) for '{search_term}'")
                    return Track(
                        id=vid_id,
                        channel_name=channel,
                        duration=dur,
                        duration_sec=dur_sec,
                        message_id=m_id,
                        title=vid_title[:60],
                        thumbnail=thumb,
                        url=vid_url,
                        view_count="",
                        video=video,
                        artist=channel,
                    )
        except Exception as yt_err:
            logger.warning(f"[YouTube Search] Failed for '{search_term}': {yt_err}")

        # Step 3: JioSaavn Direct API Search (Fallback if YouTube Search is unavailable)
        try:
            client = await self.get_client()
            safe_q = urllib.parse.quote(search_term)
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
                        song_title = valid_item.get("song") or valid_item.get("title") or search_term
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
    async def download(self, video_id: str, video: bool = False, title: str = None, artist: str = None) -> str | None:
        import glob
        raw_query = title or video_id
        clean_q = re.sub(r"(?i)\b(official|full song|video|hd|4k|lyric|lyrics|video song)\b", "", raw_query)
        clean_q = re.sub(r"[\|\[\(\]\)]", " ", clean_q)
        clean_q = " ".join(clean_q.split())
        search_query = clean_q if clean_q else raw_query

        has_trusted_artist = bool(artist) and "," not in (artist or "")
        if has_trusted_artist and artist.lower() not in (title or "").lower():
            artist_title_query = f"{title} {artist}".strip() if title else search_query
            sc_query = f'"{artist}" "{title}"' if title else search_query
        else:
            artist_title_query = search_query
            sc_query = search_query

        os.makedirs("downloads", exist_ok=True)

        safe_name = re.sub(r"[^\w\-_]", "_", video_id)

        loop = asyncio.get_event_loop()

        def _download():
            import yt_dlp

            def get_matching_file():
                matches = glob.glob(os.path.join("downloads", f"{safe_name}.*"))
                valid = [f for f in matches if not f.endswith((".jpg", ".png", ".json", ".part", ".ytdl")) and os.path.getsize(f) > 0]
                return valid[0] if valid else None

            # Strategy 1: Direct YouTube Download for 11-char Video IDs (Guarantees 100% exact original song track!)
            if len(video_id) == 11 and not video_id.startswith("sp_"):
                yt_url = f"https://www.youtube.com/watch?v={video_id}"
                # Purge any stale file from old JioSaavn bug to force fresh 100% original YouTube download
                for old_ext in ("mp3", "m4a", "mp4", "webm", "opus", "mkv", "ogg"):
                    old_f = os.path.join("downloads", f"{safe_name}.{old_ext}")
                    if os.path.exists(old_f):
                        try:
                            os.remove(old_f)
                            logger.info(f"[Music] Removed stale cached file: {old_f}")
                        except Exception:
                            pass

                ydl_opts = {
                    "format": "bestaudio/best" if not video else "best[ext=mp4]/best",
                    "outtmpl": os.path.join("downloads", f"{safe_name}.%(ext)s"),
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                    "noplaylist": True,
                    "overwrites": True,
                    "socket_timeout": 15,
                }
                try:
                    logger.info(f"[Music] Direct YouTube downloading exact track ID: {video_id}")
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([yt_url])
                    res = get_matching_file()
                    if res:
                        logger.info(f"[Music] Direct YouTube download success: {res}")
                        return res
                except Exception as yt_err:
                    logger.warning(f"[Music] Direct YouTube download failed ({yt_err}). Attempting fallbacks...")

            # Strategy 2: SoundCloud Search Fallback
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
                logger.info(f"[Music] SoundCloud search fallback: {sc_query}")
                with yt_dlp.YoutubeDL(sc_opts) as sc_ydl:
                    sc_ydl.extract_info(f"scsearch1:{sc_query}", download=True)
                res = get_matching_file()
                if res:
                    return res
            except Exception as sc_err:
                logger.warning(f"[Music] SoundCloud download failed ({sc_err}).")

            return get_matching_file()

        # Stage 1: JioSaavn Official API DES 320kbps MP3 Extractor (STRICT title/artist matching only)
        if not video:
            try:
                target_mp3 = os.path.join("downloads", f"{safe_name}.mp3")
                client = await self.get_client()

                enc_url = None
                safe_q = urllib.parse.quote(artist_title_query)
                jio_api = f"https://www.jiosaavn.com/api.php?__call=search.getResults&q={safe_q}&_format=json&p=1&n=10"
                async with client.get(jio_api, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}) as resp:
                    if resp.status == 200:
                        res_data = await resp.json(content_type=None)
                        results = res_data.get("results", [])

                        _bad = re.compile(r"(?i)\b(karaoke|instrumental|cover|tribute|originally performed)\b")
                        artist_lower = (artist or "").lower() if has_trusted_artist else ""
                        title_lower = (title or "").lower()
                        best = None

                        for r in results:
                            r_song = (r.get("song") or r.get("title") or "").lower()
                            r_artists = (r.get("primary_artists") or r.get("singers") or "").lower()
                            has_enc = bool(r.get("encrypted_media_url"))

                            if _bad.search(r_song):
                                continue

                            clean_words = [w for w in re.findall(r"\w+", title_lower) if len(w) > 1 and w not in ("feat", "featuring", "remix", "version", "official", "audio", "video")]
                            title_match = any(w in r_song for w in clean_words) if clean_words else title_lower in r_song
                            artist_match = artist_lower and artist_lower in r_artists

                            if has_enc and has_trusted_artist and artist_match and title_match:
                                best = r
                                break
                            if has_enc and title_match and not best:
                                best = r

                        # ONLY use JioSaavn if strict title match succeeded (NEVER use random unrelated song)
                        if best:
                            enc_url = best.get("encrypted_media_url")
                            logger.info(f"[Music] JioSaavn matched strictly: {best.get('song')} by {best.get('primary_artists')}")

                if enc_url:
                    raw_mp3_url = ""
                    try:
                        import base64
                        data_bytes = base64.b64decode(enc_url)
                        key_bytes = b"38346591"

                        try:
                            from Crypto.Cipher import DES
                            cipher = DES.new(key_bytes, DES.MODE_ECB)
                            dec_b = cipher.decrypt(data_bytes)
                            pad = dec_b[-1]
                            raw_mp3_url = dec_b[:-pad].decode("utf-8")
                        except Exception:
                            pass

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

                        if not raw_mp3_url:
                            try:
                                import pyDes
                                cipher = pyDes.des(key_bytes, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
                                raw_mp3_url = cipher.decrypt(data_bytes).decode("utf-8")
                            except Exception:
                                pass

                        if raw_mp3_url:
                            for quality in ("_320.mp4", "_160.mp4", "_96.mp4"):
                                attempt_url = re.sub(r"_(96|128|160|320)\.mp4", quality, raw_mp3_url)
                                try:
                                    async with client.get(attempt_url, headers={"User-Agent": "Mozilla/5.0"}) as audio_resp:
                                        if audio_resp.status == 200:
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

        # Direct YouTube / SoundCloud Executor Fallback
        try:
            file_path = await loop.run_in_executor(None, _download)
            if file_path and os.path.exists(file_path):
                return file_path
        except Exception as e:
            logger.error(f"Download failed for {video_id}: {e}")

        return None

        return None

    async def close(self):
        if self._client and not self._client.closed:
            await self._client.close()
