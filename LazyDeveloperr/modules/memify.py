import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

from LazyDeveloperr import telethn as bot
from LazyDeveloperr.events import register

@register(pattern=r"^/mmf(?:@\w+)?(?:\s+(.+))?")
async def handler(event):
    if event.fwd_from:
        return

    if not event.reply_to_msg_id:
        return await event.reply("Reply to an image or sticker with `/mmf text`!")

    reply_message = await event.get_reply_message()

    if not reply_message or not reply_message.media:
        return await event.reply("Reply to an image or sticker with `/mmf text`!")

    file = await bot.download_media(reply_message)
    msg = await event.reply("Memifying this image... ✊🏻")

    text = (event.pattern_match.group(1) or "").strip()

    if not text:
        return await msg.edit("Usage: `/mmf top text ; bottom text`")

    try:
        meme = await drawText(file, text)
        await bot.send_file(event.chat_id, file=meme, force_document=False, reply_to=event.id)
        await msg.delete()
        if os.path.exists(meme):
            os.remove(meme)
    except Exception as e:
        await msg.edit(f"Error memifying image: {e}")


async def drawText(image_path, text):
    img = Image.open(image_path)
    i_width, i_height = img.size

    try:
        m_font = ImageFont.truetype("arial.ttf", int((70 / 640) * i_width))
    except Exception:
        m_font = ImageFont.load_default()

    if ";" in text:
        upper_text, lower_text = text.split(";")

    else:
        upper_text = text

        lower_text = ""

    draw = ImageDraw.Draw(img)

    current_h, pad = 10, 5

    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            uwl, uht, uwr, uhb = m_font.getbbox(u_text)
            u_width, u_height = uwr - uwl, uhb - uht

            draw.text(
                xy=(((i_width - u_width) / 2) - 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(((i_width - u_width) / 2) + 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=((i_width - u_width) / 2, int(((current_h / 640) * i_width)) - 2),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(((i_width - u_width) / 2), int(((current_h / 640) * i_width)) + 2),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=((i_width - u_width) / 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(255, 255, 255),
            )

            current_h += u_height + pad

    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            uwl, uht, uwr, uhb = m_font.getbbox(l_text)
            u_width, u_height = uwr - uwl, uhb - uht

            draw.text(
                xy=(
                    ((i_width - u_width) / 2) - 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(
                    ((i_width - u_width) / 2) + 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) - 2,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) + 2,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(255, 255, 255),
            )

            current_h += u_height + pad

    image_name = "memify.webp"
    webp_file = os.path.join(image_name)
    img.save(webp_file, "webp")
    img.close()
    if os.path.exists(image_path):
        try:
            os.remove(image_path)
        except Exception:
            pass
    return webp_file


__mod_name__ = "Mᴍғ"
__help__ = """ 
⫸ /mmf <ᴛᴇxᴛ> ◉ ᴛᴏ ᴍᴇᴍɪғʏ """
