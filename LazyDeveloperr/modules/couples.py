import os 
import random
from datetime import datetime, timedelta
from telegraph import upload_file
from PIL import Image, ImageDraw
from pyrogram import *
from pyrogram.types import *
from pyrogram.enums import *

from LazyDeveloperr import pbot as app
from LazyDeveloperr.mongo.couples_db import _get_image, get_couple, save_couple


@app.on_message(filters.command("couples"))
async def ctest(_, message):
    cid = message.chat.id
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘs.")

    today = datetime.now().strftime("%d/%m/%Y")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

    is_selected = await get_couple(cid, today)
    if is_selected and isinstance(is_selected, dict):
        c1_id = is_selected.get("c1_id")
        c2_id = is_selected.get("c2_id")
        saved_img = is_selected.get("img")

        try:
            u1 = await app.get_users(c1_id)
            N1 = u1.mention if u1 else f"[User](tg://user?id={c1_id})"
        except Exception:
            N1 = f"[User](tg://user?id={c1_id})"

        try:
            u2 = await app.get_users(c2_id)
            N2 = u2.mention if u2 else f"[User](tg://user?id={c2_id})"
        except Exception:
            N2 = f"[User](tg://user?id={c2_id})"

        TXT = f"""
**ᴛᴏᴅᴀʏ's sᴇʟᴇᴄᴛᴇᴅ ᴄᴏᴜᴘʟᴇs 💓 :

➖➖➖➖➖➖➖➖➖➖➖➖
{N1} + {N2} = ❣️
➖➖➖➖➖➖➖➖➖➖➖➖

HAA MERI JAAN
ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow} !!**
"""
        if saved_img and os.path.exists(saved_img):
            return await message.reply_photo(saved_img, caption=TXT)
        elif saved_img and saved_img.startswith(("http://", "https://")):
            return await message.reply_photo(saved_img, caption=TXT)
        else:
            return await message.reply_text(TXT)

    # If not selected today, generate new couple of the day
    try:
        msg = await message.reply_text("ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...")
        list_of_users = []

        async for i in app.get_chat_members(message.chat.id, limit=50):
            if i.user and not i.user.is_bot:
                list_of_users.append(i.user.id)

        if len(list_of_users) < 2:
            return await msg.edit("Not enough members in this group to choose a couple!")

        c1_id = random.choice(list_of_users)
        c2_id = random.choice(list_of_users)
        while c1_id == c2_id:
            c1_id = random.choice(list_of_users)

        photo1 = (await app.get_chat(c1_id)).photo
        photo2 = (await app.get_chat(c2_id)).photo

        try:
            u1 = await app.get_users(c1_id)
            N1 = u1.mention if u1 else f"[User](tg://user?id={c1_id})"
        except Exception:
            N1 = f"[User](tg://user?id={c1_id})"

        try:
            u2 = await app.get_users(c2_id)
            N2 = u2.mention if u2 else f"[User](tg://user?id={c2_id})"
        except Exception:
            N2 = f"[User](tg://user?id={c2_id})"

        try:
            p1 = await app.download_media(photo1.big_file_id, file_name="pfp.png")
        except Exception:
            p1 = "LazyDeveloperr/Love/upic.png"
        try:
            p2 = await app.download_media(photo2.big_file_id, file_name="pfp1.png")
        except Exception:
            p2 = "LazyDeveloperr/Love/upic.png"

        img1 = Image.open(f"{p1}")
        img2 = Image.open(f"{p2}")

        img = Image.open("LazyDeveloperr/Love/HMMM.jpg")

        img1 = img1.resize((390, 390))
        img2 = img2.resize((390, 390))

        mask = Image.new('L', img1.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + img1.size, fill=255)

        mask1 = Image.new('L', img2.size, 0)
        draw = ImageDraw.Draw(mask1)
        draw.ellipse((0, 0) + img2.size, fill=255)

        img1.putalpha(mask)
        img2.putalpha(mask1)

        draw = ImageDraw.Draw(img)

        img.paste(img1, (120, 194), img1)
        img.paste(img2, (780, 196), img2)

        out_img = f'test_{cid}.png'
        img.save(out_img)

        TXT = f"""
**ᴛᴏᴅᴀʏ's sᴇʟᴇᴄᴛᴇᴅ ᴄᴏᴜᴘʟᴇs 💓 :

➖➖➖➖➖➖➖➖➖➖➖➖
{N1} + {N2} = ❣️
➖➖➖➖➖➖➖➖➖➖➖➖

HAA MERI JAAN
ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow} !!**
"""

        await message.reply_photo(out_img, caption=TXT)
        await msg.delete()

        img_link = out_img
        try:
            a = upload_file(out_img)
            if a:
                img_link = "https://graph.org/" + a[0]
        except Exception:
            pass

        couple_data = {"c1_id": c1_id, "c2_id": c2_id}
        await save_couple(cid, today, couple_data, img_link)

    except Exception as e:
        print(f"Error in couples handler: {e}")
    finally:
        try:
            if os.path.exists("pfp.png"):
                os.remove("pfp.png")
            if os.path.exists("pfp1.png"):
                os.remove("pfp1.png")
        except Exception:
            pass

    
