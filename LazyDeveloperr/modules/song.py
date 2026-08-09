import os
import requests
import yt_dlp
from pyrogram import filters
from LazyDeveloperr import SUPPORT_CHAT, pbot, BOT_NAME


@pbot.on_message(filters.command(["song", "music"]))
async def song(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/song <song name or link>`")

    user_id = message.from_user.id if message.from_user else 0
    user_name = message.from_user.first_name if message.from_user else "User"
    chutiya = f"[{user_name}](tg://user?id={user_id})"

    query = message.text.split(None, 1)[1]
    m = await message.reply_text("» **Searching song, please wait...**")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "%(id)s.%(ext)s",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    cookie_file = None
    if os.path.exists("cookies.txt"):
        cookie_file = "cookies.txt"
    elif os.path.exists("LazyDeveloperr/cookies"):
        for f in os.listdir("LazyDeveloperr/cookies"):
            if f.endswith(".txt"):
                cookie_file = os.path.join("LazyDeveloperr/cookies", f)
                break

    if cookie_file:
        ydl_opts["cookiefile"] = cookie_file

    audio_file = None
    thumb_name = None
    try:
        search_target = query if query.startswith("http://") or query.startswith("https://") else f"ytsearch1:{query}"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_target, download=True)
        except Exception:
            fallback_opts = {
                "format": "bestaudio/best",
                "outtmpl": "%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                info = ydl.extract_info(search_target, download=True)
            if "entries" in info:
                info = info["entries"][0]

            title = info.get("title", "Song")
            duration = info.get("duration", 0)
            thumbnail_url = info.get("thumbnail", "")
            views = info.get("view_count", 0)
            url = info.get("webpage_url", search_target)
            video_id = info.get("id", "temp")

            audio_file = f"{video_id}.mp3"
            if not os.path.exists(audio_file):
                audio_file = ydl.prepare_filename(info)

        thumb_name = f"thumb_{info.get('id', 'temp')}.jpg"
        if thumbnail_url:
            try:
                res = requests.get(thumbnail_url, timeout=5)
                with open(thumb_name, "wb") as f:
                    f.write(res.content)
            except Exception:
                thumb_name = None
        else:
            thumb_name = None

        caption = f"**Title:** [{title[:40]}]({url})\n**Duration:** `{duration}s`\n**Views:** `{views}`\n**Requested By:** {chutiya}"

        safe_thumb = thumb_name if (thumb_name and os.path.exists(thumb_name)) else None
        await message.reply_audio(
            audio_file,
            caption=caption,
            performer=BOT_NAME,
            thumb=safe_thumb,
            title=title,
            duration=int(duration),
        )
        await m.delete()
    except Exception as e:
        await m.edit(f"**Download Error:** {e}")
    finally:
        if audio_file and os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except Exception:
                pass
        if thumb_name and os.path.exists(thumb_name):
            try:
                os.remove(thumb_name)
            except Exception:
                pass
