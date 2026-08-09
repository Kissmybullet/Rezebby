import os
import requests
import yt_dlp
from pyrogram import filters
from pyrogram.types import Message
from LazyDeveloperr import pbot


@pbot.on_message(filters.command(["vsong", "video"]))
async def ytvideo(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/video <video name or link>`")

    user_id = message.from_user.id if message.from_user else 0
    user_name = message.from_user.first_name if message.from_user else "User"
    chutiya = f"[{user_name}](tg://user?id={user_id})"

    query = message.text.split(None, 1)[1]
    pablo = await message.reply_text("» **Searching video, please wait...**")

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": "%(id)s.%(ext)s",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
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

    video_file = None
    thumb_name = None
    try:
        search_target = query if query.startswith("http://") or query.startswith("https://") else f"ytsearch1:{query}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_target, download=True)
            if "entries" in info:
                info = info["entries"][0]

            video_file = ydl.prepare_filename(info)
            title = info.get("title", "Video")
            duration = info.get("duration", 0)
            thumbnail_url = info.get("thumbnail", "")
            channel = info.get("uploader", "YouTube")
            url = info.get("webpage_url", search_target)

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

        caption = f"❄ **Title:** [{title[:40]}]({url})\n💫 **Channel:** {channel}\n🥀 **Requested By:** {chutiya}"

        safe_thumb = thumb_name if (thumb_name and os.path.exists(thumb_name)) else None
        await client.send_video(
            message.chat.id,
            video=video_file,
            caption=caption,
            duration=int(duration),
            thumb=safe_thumb,
            supports_streaming=True,
        )
        await pablo.delete()
    except Exception as e:
        await pablo.edit(f"**Failed to download video:** {e}")
    finally:
        if video_file and os.path.exists(video_file):
            try:
                os.remove(video_file)
            except Exception:
                pass
        if thumb_name and os.path.exists(thumb_name):
            try:
                os.remove(thumb_name)
            except Exception:
                pass
