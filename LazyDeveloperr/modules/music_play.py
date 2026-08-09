# ====================================================================================
# 💟 Reach Out @LazyDeveloperr 💟
# ------------------------------------------------------------------------------------
# 👑 Lead Engineer : Intkhab Ahmad (@LazyDeveloperr)
# 🐙 GitHub        : https://github.com/LazyDeveloperr
# 📸 Instagram     : https://instagram.com/LazyDeveloperr
# 📢 Telegram      : https://telegram.me/LazyDeveloperr
# ------------------------------------------------------------------------------------
# ✨ Features & Fixes in this Module:
#   ⏭️ Play next song button and /skip now work for full Spotify playlists
#   📤 Automatic audio and video file backup to database log channel
# ====================================================================================

import os
from pathlib import Path

from pyrogram import filters, types

from LazyDeveloperr import Kartik, app, config, db, lang, logger, queue, tg, yt
from LazyDeveloperr.music_helpers import buttons, utils
from LazyDeveloperr.music_helpers._play import checkUB


def playlist_to_queue(chat_id: int, tracks: list) -> str:
    text = "<blockquote expandable>"
    for track in tracks:
        pos = queue.add(chat_id, track)
        text += f"<b>{pos}.</b> {track.title}\n"
    text = text[:1948] + "</blockquote>"
    return text


@app.on_message(
    filters.command(["play", "playforce", "vplay", "vplayforce", "spotify"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
@checkUB
async def play_hndlr(
    _,
    m: types.Message,
    force: bool = False,
    m3u8: bool = False,
    video: bool = False,
    url: str = None,
) -> None:
    sent = await m.reply_text(m.lang["play_searching"])
    file = None
    mention = m.from_user.mention
    media = tg.get_media(m.reply_to_message) if m.reply_to_message else None
    tracks = []

    if media:
        setattr(sent, "lang", m.lang)
        file = await tg.download(m.reply_to_message, sent)

    elif m3u8:
        file = await tg.process_m3u8(url, sent.id, video)

    elif url:
        from LazyDeveloperr.music_core.spotify import spotify
        from LazyDeveloperr.music_helpers import Track
        import re
        if spotify.valid(url):
            if "playlist" in url or "album" in url:
                await sent.edit_text("Fetching Spotify playlist...")
                sp_tracks = await spotify.playlist(url)
                if sp_tracks:
                    file = await yt.search(sp_tracks[0], sent.id, video=video)
                    if len(sp_tracks) > 1:
                        tracks = []
                        for song_query in sp_tracks[1:]:
                            song_id = "sp_" + re.sub(r"[^\w]", "", song_query)[:30]
                            t_obj = Track(
                                id=song_id,
                                channel_name="Spotify",
                                duration="03:30",
                                duration_sec=210,
                                message_id=sent.id,
                                title=song_query,
                                user=mention,
                                video=video,
                                url=url
                            )
                            tracks.append(t_obj)
            else:
                sp_query = await spotify.track(url)
                if sp_query:
                    file = await yt.search(sp_query, sent.id, video=video)

        if not file:
            if "playlist" in url:
                await sent.edit_text(m.lang["playlist_fetch"])
                tracks = await yt.playlist(config.PLAYLIST_LIMIT, mention, url, video)

                if not tracks:
                    return await sent.edit_text(m.lang["playlist_error"])

                file = tracks[0]
                tracks.remove(file)
                file.message_id = sent.id
            else:
                file = await yt.search(url, sent.id, video=video)

        if not file:
            return await sent.edit_text(
                m.lang["play_not_found"].format(config.SUPPORT_CHAT)
            )

    elif len(m.command) >= 2:
        query = " ".join(m.command[1:])
        file = await yt.search(query, sent.id, video=video)
        if not file:
            return await sent.edit_text(
                m.lang["play_not_found"].format(config.SUPPORT_CHAT)
            )

    if not file:
        return await sent.edit_text(m.lang["play_usage"])

    if file.duration_sec > config.DURATION_LIMIT:
        return await sent.edit_text(
            m.lang["play_duration_limit"].format(config.DURATION_LIMIT // 60)
        )

    if await db.is_logger():
        await utils.play_log(m, sent.link, file.title, file.duration)

    file.user = mention
    if force:
        current = queue.get_current(m.chat.id)
        if current and current.message_id:
            try:
                await app.delete_messages(m.chat.id, current.message_id)
            except Exception:
                pass
        queue.force_add(m.chat.id, file)
    else:
        if not await db.get_call(m.chat.id):
            queue.clear(m.chat.id)

        position = queue.add(m.chat.id, file)

        if position != 0 and await db.get_call(m.chat.id):
            await sent.edit_text(
                m.lang["play_queued"].format(
                    position,
                    file.url,
                    file.title,
                    file.duration,
                    m.from_user.mention,
                ),
                reply_markup=buttons.play_queued(
                    m.chat.id, file.id, m.lang["play_now"]
                ),
            )
            if tracks:
                added = playlist_to_queue(m.chat.id, tracks)
                await app.send_message(
                    chat_id=m.chat.id,
                    text=m.lang["playlist_queued"].format(len(tracks)) + added,
                )
            return

    if not file.file_path:
        fname_pattern = [
            f"downloads/{file.id}.webm",
            f"downloads/{file.id}.mp4",
            f"downloads/{file.id}.m4a",
        ]
        cached = next((f for f in fname_pattern if Path(f).exists()), None)
        if cached:
            file.file_path = cached
        else:
            await sent.edit_text(m.lang["play_downloading"])
            file.file_path = await yt.download(file.id, video=video, title=file.title)

    if not file.file_path:
        return await sent.edit_text(
            f"❌ **Download failed!**\n\nUnable to download the audio. "
            f"Please add `cookies.txt` to the bot root directory and try again."
        )

    await Kartik.play_media(chat_id=m.chat.id, message=sent, media=file)

    # Send the actual audio/video file to the Database / Logger Channel
    if app.logger and app.logger != 0:
        try:
            log_caption = f"🎵 **Title:** {file.title}\n👤 **Played By:** {mention}\n💬 **Chat:** {m.chat.title} (`{m.chat.id}`)"
            if file.file_path and os.path.exists(file.file_path):
                if video:
                    await app.send_video(chat_id=app.logger, video=file.file_path, caption=log_caption)
                else:
                    await app.send_audio(chat_id=app.logger, audio=file.file_path, caption=log_caption, title=file.title)
        except Exception as log_err:
            logger.warning(f"[Log Channel] Error forwarding file to DB channel: {log_err}")

    if not tracks:
        return
    added = playlist_to_queue(m.chat.id, tracks)
    await app.send_message(
        chat_id=m.chat.id,
        text=m.lang["playlist_queued"].format(len(tracks)) + added,
    )
