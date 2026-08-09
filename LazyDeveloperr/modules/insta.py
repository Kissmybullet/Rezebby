# SOURCE https://github.com/Team-ProjectCodeX
# CREATED BY https://t.me/O_okarma
# PROVIDED BY https://t.me/ProjectCodeX


import requests
from pyrogram import filters
from pyrogram.types import Message

from LazyDeveloperr import pbot as app

DOWNLOADING_STICKER_ID = (
    "CAACAgIAAxkBAAEDv_xlJWmh2-fKRwvLywJaFeGy9wmBKgACVQADr8ZRGmTn_PAl6RC_MAQ"
)


@app.on_message(
    filters.command(["ig", "instagram", "insta", "instadl"])
)
async def instadl_command_handler(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /instadl [Instagram URL]")

    link = message.command[1]
    downloading_sticker = None
    try:
        try:
            downloading_sticker = await message.reply_sticker(DOWNLOADING_STICKER_ID)
        except Exception:
            pass

        content_url = None
        try:
            res = requests.get(f"https://apis.xditya.me/instagram?url={requests.utils.quote(link)}", timeout=10).json()
            if isinstance(res, dict) and "url" in res:
                content_url = res["url"]
            elif isinstance(res, dict) and "download_url" in res:
                content_url = res["download_url"]
        except Exception:
            pass

        if not content_url:
            try:
                res = requests.get(f"https://api.v2.ddinstagram.com/reel?url={requests.utils.quote(link)}", timeout=8).json()
                if isinstance(res, dict) and "video_url" in res:
                    content_url = res["video_url"]
            except Exception:
                pass

        if not content_url:
            try:
                res = requests.get("https://karma-api2.vercel.app/instadl", params={"url": link}, timeout=5).json()
                if isinstance(res, dict) and "content_url" in res:
                    content_url = res["content_url"]
            except Exception:
                pass

        if content_url:
            try:
                await message.reply_video(content_url)
            except Exception:
                await message.reply_photo(content_url)
        else:
            await message.reply("Unable to fetch Instagram media. Please verify the URL or try again later.")

    except Exception as e:
        await message.reply(f"An error occurred while processing: {e}")

    finally:
        if downloading_sticker:
            try:
                await downloading_sticker.delete()
            except Exception:
                pass
