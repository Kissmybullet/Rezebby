import asyncio
from pyrogram import filters, enums
from pyrogram.types import Message
from LazyDeveloperr import pbot as app, BOT_USERNAME

spam_chats = []


@app.on_message(filters.command(["tagall", "all", "mention"]) & filters.group)
async def tagall_command(client, message: Message):
    chat_id = message.chat.id

    if not message.from_user:
        return await message.reply_text("__Anonymous admin tagging is not supported.__")

    # Admin check
    try:
        user_member = await client.get_chat_member(chat_id, message.from_user.id)
        if user_member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return await message.reply_text("__Only admins can mention all!__")
    except Exception:
        return await message.reply_text("__Only admins can mention all!__")

    if len(message.command) > 1:
        msg = message.text.split(None, 1)[1]
    elif message.reply_to_message:
        msg = message.reply_to_message.text or message.reply_to_message.caption or "Hi Everyone! 👋"
    else:
        msg = "Hi Everyone! 👋"

    spam_chats.append(chat_id)
    usrnum = 0
    usrtxt = ""

    try:
        async for member in client.get_chat_members(chat_id):
            if chat_id not in spam_chats:
                break
            if member.user.is_bot:
                continue
            usrnum += 1
            usrtxt += f"[{member.user.first_name}](tg://user?id={member.user.id}), "
            if usrnum == 15:
                await client.send_message(chat_id, f"{msg}\n\n{usrtxt}")
                await asyncio.sleep(2)
                usrnum = 0
                usrtxt = ""

        if usrtxt and chat_id in spam_chats:
            await client.send_message(chat_id, f"{msg}\n\n{usrtxt}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
    finally:
        if chat_id in spam_chats:
            spam_chats.remove(chat_id)


@app.on_message(filters.command(["cancel", "stopmention"]) & filters.group)
async def cancel_spam(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in spam_chats:
        return await message.reply_text("There is no tagging process ongoing.")

    if not message.from_user:
        return await message.reply_text("__Only admins can execute this command!__")

    try:
        user_member = await client.get_chat_member(chat_id, message.from_user.id)
        if user_member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return await message.reply_text("__Only admins can execute this command!__")
    except Exception:
        return await message.reply_text("__Only admins can execute this command!__")

    if chat_id in spam_chats:
        spam_chats.remove(chat_id)
    return await message.reply_text("Stopped mention process.")


__mod_name__ = "Tᴀɢᴀʟʟ"
__help__ = """
──「  ᴏɴʟʏ ғᴏʀ ᴀᴅᴍɪɴs 」──

❍ /tagall ᴏʀ /all [text/reply] to mention all group members.
❍ /cancel to stop tagall process.
"""
