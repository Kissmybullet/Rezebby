import os
from datetime import datetime

from PIL import Image
from telegraph import Telegraph, exceptions, upload_file

from LazyDeveloperr import telethn as tbot
from LazyDeveloperr.events import register
TMP_DOWNLOAD_DIRECTORY = "./"
telegraph = Telegraph(domain="graph.org")
r = telegraph.create_account(short_name="Controller")
auth_url = r["auth_url"]


@register(pattern=r"^/tg(m|t)(?:@\w+)?(?:\s+(.+))?")
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    optional_title = event.pattern_match.group(2)
    if event.reply_to_msg_id:
        start = datetime.now()
        r_message = await event.get_reply_message()
        if input_str == "m":
            if not r_message or not r_message.media:
                return await event.reply("Reply to a media file (image/video/sticker) to upload to Telegraph.")
            h = await event.reply("Downloading media...")
            downloaded_file_name = await tbot.download_media(
                r_message, TMP_DOWNLOAD_DIRECTORY
            )
            if not downloaded_file_name:
                return await h.edit("Failed to download media.")
            if downloaded_file_name.endswith(".webp"):
                resize_image(downloaded_file_name)
            try:
                url = None
                import requests
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }

                # 1. Catbox
                try:
                    with open(downloaded_file_name, "rb") as f:
                        res = requests.post(
                            "https://catbox.moe/user/api.php",
                            data={"reqtype": "fileupload"},
                            files={"fileToUpload": f},
                            headers=headers,
                            timeout=10,
                        )
                        if res.status_code == 200 and res.text.startswith("http"):
                            url = res.text.strip()
                except Exception:
                    pass

                # 2. Litterbox
                if not url:
                    try:
                        with open(downloaded_file_name, "rb") as f:
                            res = requests.post(
                                "https://litterbox.catbox.moe/resources/internals/api.php",
                                data={"reqtype": "fileupload", "time": "24h"},
                                files={"fileToUpload": f},
                                headers=headers,
                                timeout=10,
                            )
                            if res.status_code == 200 and res.text.startswith("http"):
                                url = res.text.strip()
                    except Exception:
                        pass

                # 3. Envsh
                if not url:
                    try:
                        with open(downloaded_file_name, "rb") as f:
                            res = requests.post("https://envs.sh", files={"file": f}, headers=headers, timeout=10)
                            if res.status_code == 200 and res.text.startswith("http"):
                                url = res.text.strip()
                    except Exception:
                        pass

                # 4. Telegraph / Graph.org
                if not url:
                    try:
                        media_urls = upload_file(downloaded_file_name)
                        url = f"https://graph.org{media_urls[0]}" if media_urls[0].startswith("/") else media_urls[0]
                    except Exception:
                        pass

                if url:
                    await h.edit(f"Uploaded successfully:\n[Click Here]({url})", link_preview=True)
                else:
                    await h.edit("Upload failed across all file hosts.")
            except Exception as exc:
                await h.edit("Upload failed: " + str(exc))
            finally:
                if os.path.exists(downloaded_file_name):
                    try:
                        os.remove(downloaded_file_name)
                    except Exception:
                        pass
        elif input_str == "t":
            if not r_message:
                return await event.reply("Reply to a text message to paste to Telegraph.")
            user_object = await tbot.get_entity(r_message.sender_id)
            title_of_page = user_object.first_name if user_object else "Telegraph"
            if optional_title:
                title_of_page = optional_title
            page_content = r_message.message or ""
            if not page_content:
                return await event.reply("The replied message has no text to paste.")
            page_content = page_content.replace("\n", "<br>")
            try:
                response = telegraph.create_page(title_of_page, html_content=page_content)
                url = f"https://graph.org/{response['path']}"
                await event.reply(f"Pasted to [Telegraph]({url})", link_preview=True)
            except Exception as exc:
                await event.reply(f"Error creating page: {exc}")
    else:
        await event.reply("Reply to a message to get a permanent telegra.ph link.")


def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")


__help__ = """
ɪ ᴄᴀɴ ᴜᴘʟᴏᴀᴅ ғɪʟᴇs ᴛᴏ ᴛᴇʟᴇɢʀᴀᴘʜ
 ❍ /tgm :ɢᴇᴛ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴏғ ʀᴇᴘʟɪᴇᴅ ᴍᴇᴅɪᴀ
 ❍ /tgt :ɢᴇᴛ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴏғ ʀᴇᴘʟɪᴇᴅ ᴛᴇxᴛ
 ❍ /tgt [ᴄᴜsᴛᴏᴍ ɴᴀᴍᴇ]: ɢᴇᴛ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴏғ ʀᴇᴘʟɪᴇᴅ ᴛᴇxᴛ ᴡɪᴛʜ ᴄᴜsᴛᴏᴍ ɴᴀᴍᴇ.
"""

__mod_name__ = "T-Gʀᴀᴘʜ"
