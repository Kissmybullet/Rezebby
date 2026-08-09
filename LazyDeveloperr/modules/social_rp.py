# ====================================================================================
# 💟 Reach Out @LazyDeveloperr 💟
# ------------------------------------------------------------------------------------
# 👑 Lead Engineer : Intkhab Ahmad (@LazyDeveloperr)
# 🐙 GitHub        : https://github.com/LazyDeveloperr
# 📸 Instagram     : https://instagram.com/LazyDeveloperr
# 📢 Telegram      : https://telegram.me/LazyDeveloperr
# ------------------------------------------------------------------------------------
# ✨ Features & Fixes in this Module:
#   🌸 Interactive /kiss, /hug, /sex, and /pat commands with accept buttons
#   🖼️ Custom image saving (/set_*_img), viewing (/view_*_img), and deleting (/remove)
#   ⚡ Fixed media sending issues so images send smoothly without link errors
# ====================================================================================

import io
import random
import re
import aiohttp
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from LazyDeveloperr import pbot as app, db, logger

# Default custom image list for acceptance responses (when MongoDB list is empty)
DEFAULT_IMAGES = {
    "kiss": [
        "https://telegra.ph/file/49c43e6fc856534a09853.jpg"
    ],
    "hug": [
        "https://telegra.ph/file/49c43e6fc856534a09853.jpg"
    ],
    "pat": [
        "https://telegra.ph/file/49c43e6fc856534a09853.jpg"
    ],
    "sex": [
        "https://telegra.ph/file/49c43e6fc856534a09853.jpg"
    ]
}


async def send_rp_media(chat_id: int, media_url_or_id: str, caption: str, reply_markup=None, reply_to_message_id=None):
    """Robust media sender handling Telegram file_ids, raw URLs, and HTTP CURL failures."""
    # 1. Try sending directly as animation/photo
    try:
        if "http://" in media_url_or_id or "https://" in media_url_or_id:
            try:
                return await app.send_animation(
                    chat_id=chat_id,
                    animation=media_url_or_id,
                    caption=caption,
                    reply_markup=reply_markup,
                    reply_to_message_id=reply_to_message_id
                )
            except Exception:
                return await app.send_photo(
                    chat_id=chat_id,
                    photo=media_url_or_id,
                    caption=caption,
                    reply_markup=reply_markup,
                    reply_to_message_id=reply_to_message_id
                )
        else:
            # Send file_id directly
            return await app.send_photo(
                chat_id=chat_id,
                photo=media_url_or_id,
                caption=caption,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id
            )
    except Exception as e:
        logger.warning(f"[RP Media] Direct send failed ({e}), attempting stream bytes fallback...")

    # 2. In-memory aiohttp stream bytes fallback (bypasses Telegram WebpageCurlFailed 400 errors)
    if "http://" in media_url_or_id or "https://" in media_url_or_id:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(media_url_or_id, headers={"User-Agent": "Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(total=8.0)) as resp:
                    if resp.status == 200:
                        content_bytes = await resp.read()
                        bio = io.BytesIO(content_bytes)
                        bio.name = "media.gif" if ".gif" in media_url_or_id else "media.jpg"
                        try:
                            return await app.send_animation(
                                chat_id=chat_id,
                                animation=bio,
                                caption=caption,
                                reply_markup=reply_markup,
                                reply_to_message_id=reply_to_message_id
                            )
                        except Exception:
                            bio.seek(0)
                            return await app.send_photo(
                                chat_id=chat_id,
                                photo=bio,
                                caption=caption,
                                reply_markup=reply_markup,
                                reply_to_message_id=reply_to_message_id
                            )
        except Exception as dl_err:
            logger.error(f"[RP Media] Stream download failed: {dl_err}")

    # 3. Text fallback
    return await app.send_message(
        chat_id=chat_id,
        text=caption,
        reply_markup=reply_markup,
        reply_to_message_id=reply_to_message_id
    )


async def get_rp_images(category: str) -> list[str]:
    """Fetch custom images from MongoDB for the category, fallback to defaults."""
    try:
        doc = await db.db.social_rp.find_one({"_id": category})
        if doc and doc.get("urls") and len(doc["urls"]) > 0:
            return doc["urls"]
    except Exception:
        pass
    return DEFAULT_IMAGES.get(category, DEFAULT_IMAGES["kiss"])


async def add_rp_image(category: str, url: str) -> int:
    """Add a new custom image URL/file_id to MongoDB collection list using $addToSet."""
    await db.db.social_rp.update_one(
        {"_id": category},
        {"$addToSet": {"urls": url}},
        upsert=True
    )
    doc = await db.db.social_rp.find_one({"_id": category})
    return len(doc.get("urls", [])) if doc else 1


# Set Custom Image Commands (/set_kiss_img, /set_hug_img, /set_sex_img, /set_pat_img)
@app.on_message(filters.command(["set_kiss_img", "set_hug_img", "set_sex_img", "set_pat_img"]))
async def set_rp_img_handler(_, message: Message):
    cmd = message.command[0].lower()
    category = cmd.replace("set_", "").replace("_img", "")  # kiss, hug, sex, pat

    img_url = None
    if message.reply_to_message:
        reply = message.reply_to_message
        if reply.photo:
            img_url = reply.photo.file_id
        elif reply.animation:
            img_url = reply.animation.file_id
        elif reply.sticker:
            img_url = reply.sticker.file_id
        elif reply.video:
            img_url = reply.video.file_id
        elif reply.text and ("http://" in reply.text or "https://" in reply.text):
            img_url = reply.text.strip()
    elif len(message.command) >= 2:
        img_url = message.command[1].strip()

    if not img_url:
        return await message.reply_text(
            f"❌ **Usage:** Reply to a Photo, GIF, or Video, or send link:\n/{cmd} <image_url> to append new pictures to {category.upper()} list."
        )

    count = await add_rp_image(category, img_url)
    await message.reply_text(
        f"✨ **Successfully added picture/GIF to {category.upper()} list in MongoDB!** ✨\n\nTotal pictures in {category.upper()} list: **{count}**"
    )


# View Custom Image Commands (/view_kiss_img, /view_hug_img, /view_sex_img, /view_pat_img)
@app.on_message(filters.command(["view_kiss_img", "view_hug_img", "view_sex_img", "view_pat_img"]))
async def view_rp_img_handler(_, message: Message):
    cmd = message.command[0].lower()
    category = cmd.replace("view_", "").replace("_img", "")  # kiss, hug, sex, pat

    user_id = message.from_user.id

    # Fetch custom images directly from MongoDB
    doc = await db.db.social_rp.find_one({"_id": category})
    urls = doc.get("urls", []) if doc else []

    if not urls:
        return await message.reply_text(
            f"⚠️ **No custom images/GIFs stored in MongoDB for {category.upper()}!**\n\nUse /set_{category}_img to add custom images."
        )

    status_msg = await message.reply_text(
        f"🔄 **Fetching and sending {len(urls)} custom {category.upper()} pictures/GIFs to your PM...**"
    )

    success_count = 0
    for idx, media_item in enumerate(urls, 1):
        try:
            await send_rp_media(
                chat_id=user_id,
                media_url_or_id=media_item,
                caption=f"💖 **{category.upper()} Custom Media ({idx}/{len(urls)})**"
            )
            success_count += 1
        except Exception as e:
            logger.warning(f"[View RP] Failed to send media item to PM: {e}")

    if success_count > 0:
        await status_msg.edit_text(
            f"✅ **Successfully sent {success_count}/{len(urls)} {category.upper()} pictures/GIFs to your PM!** Check your DM. 📩"
        )
    else:
        await status_msg.edit_text(
            f"❌ **Failed to send media to your PM.** Please make sure you have started the bot in DM (/start)!"
        )


# Remove Single Image Command (/remove)
@app.on_message(filters.command(["remove"]))
async def remove_rp_img_handler(_, message: Message):
    img_url = None
    if message.reply_to_message:
        reply = message.reply_to_message
        if reply.photo:
            img_url = reply.photo.file_id
        elif reply.animation:
            img_url = reply.animation.file_id
        elif reply.sticker:
            img_url = reply.sticker.file_id
        elif reply.video:
            img_url = reply.video.file_id
        elif reply.text and ("http://" in reply.text or "https://" in reply.text):
            img_url = reply.text.strip()
    elif len(message.command) >= 2:
        img_url = message.command[1].strip()

    if not img_url:
        return await message.reply_text(
            "❌ **Usage:** Reply to a Photo, GIF, Sticker, or Video, or send link with /remove to delete it from MongoDB."
        )

    removed_from = []
    for cat in ["kiss", "hug", "sex", "pat"]:
        res = await db.db.social_rp.update_one(
            {"_id": cat},
            {"$pull": {"urls": img_url}}
        )
        if res.modified_count > 0:
            removed_from.append(cat.upper())

    if removed_from:
        cats_str = ", ".join(removed_from)
        await message.reply_text(
            f"? **Successfully removed picture/GIF from MongoDB category: {cats_str}!** ?"
        )
    else:
        await message.reply_text(
            "? **This picture/GIF was not found in any MongoDB category list!**"
        )


# Remove All Custom Images Commands (/removeall_kiss_img, /removeall_hug_img, /removeall_sex_img, /removeall_pat_img)
@app.on_message(filters.command(["removeall_kiss_img", "removeall_hug_img", "removeall_sex_img", "removeall_pat_img"]))
async def removeall_rp_img_handler(_, message: Message):
    cmd = message.command[0].lower()
    category = cmd.replace("removeall_", "").replace("_img", "")  # kiss, hug, sex, pat

    await db.db.social_rp.delete_one({"_id": category})
    await message.reply_text(
        f"? **Successfully cleared ALL custom images for {category.upper()} from MongoDB!** ?"
    )


# Main Command Handler (/kiss, /hug, /sex, /pat)
@app.on_message(filters.command(["kiss", "hug", "pat", "sex"]) & filters.group)
async def rp_command_handler(_, message: Message):
    cmd = message.command[0].lower()

    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply_text(
            f"You need to reply to a user's message to send a {cmd} request."
        )

    sender = message.from_user
    target = message.reply_to_message.from_user

    if sender.id == target.id:
        return await message.reply_text(f"You cannot {cmd} yourself!")

    if target.is_bot:
        return await message.reply_text(f"Bots don't participate in {cmd} requests!")

    # For /pat: Direct photo reply (no approval required)
    if cmd == "pat":
        images = await get_rp_images("pat")
        selected_img = random.choice(images)
        caption = f"? **{sender.mention}** patted **{target.mention}**! ?"
        return await send_rp_media(
            chat_id=message.chat.id,
            media_url_or_id=selected_img,
            caption=caption,
            reply_to_message_id=message.reply_to_message.id
        )

    # For /kiss, /hug, and /sex: ONLY text request message with inline button! (Old anime request GIF removed!)
    callback_data = f"rp_acc:{cmd}:{sender.id}:{target.id}"

    btn_labels = {
        "kiss": "?? Accept",
        "hug": "?? Accept",
        "sex": "?? Accept"
    }
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(btn_labels.get(cmd, "Accept"), callback_data=callback_data)]]
    )

    action_texts = {
        "kiss": f"?? **{target.mention}** see **{sender.mention}** wants to kiss you! ??\n\nWill you accept the kiss?",
        "hug": f"?? **{target.mention}** see **{sender.mention}** wants to give you a warm hug! ??\n\nWill you accept the hug?",
        "sex": f"?? **{target.mention}** see **{sender.mention}** wants to get wild with you! ??\n\nWill you accept the offer?"
    }

    caption_text = action_texts.get(cmd)

    await message.reply_text(
        text=caption_text,
        reply_markup=keyboard,
        quote=True
    )


# Callback Handler for Acceptance (Deletes request text message and sends 1 single accepted photo/GIF with random MongoDB image!)
@app.on_callback_query(filters.regex(r"^rp_acc:(kiss|hug|sex):(\d+):(\d+)$"))
async def rp_accept_callback(_, query: CallbackQuery):
    action, sender_id, target_id = query.data.split(":")[1:]
    sender_id = int(sender_id)
    target_id = int(target_id)

    # Only target user can accept
    if query.from_user.id != target_id:
        return await query.answer(
            "This request is not for you to accept!", show_alert=True
        )

    await query.answer("Request Accepted! ??")

    try:
        sender_user = await app.get_users(sender_id)
        sender_mention = sender_user.mention
    except Exception:
        sender_mention = "User"

    target_mention = query.from_user.mention

    captions = {
        "kiss": f"?? **{target_mention}** accepted the kiss from **{sender_mention}**! ????",
        "hug": f"?? **{target_mention}** accepted the warm hug from **{sender_mention}**! ????",
        "sex": f"?? **{target_mention}** accepted the wild passion from **{sender_mention}**! ????"
    }

    caption = captions.get(action, f"?? **{target_mention}** accepted from **{sender_mention}**! ??")

    # Fetch a RANDOM custom image/GIF from MongoDB!
    images = await get_rp_images(action)
    selected_img = random.choice(images)

    # Delete initial request text message
    try:
        await query.message.delete()
    except Exception:
        pass

    # Send ONLY the accepted photo/GIF with random MongoDB picture!
    await send_rp_media(
        chat_id=query.message.chat.id,
        media_url_or_id=selected_img,
        caption=caption
    )
