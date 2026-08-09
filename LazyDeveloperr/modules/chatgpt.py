import requests
from .. import pbot as Mukesh,BOT_NAME,BOT_USERNAME
import time
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters
from MukeshAPI import api
@Mukesh.on_message(filters.command(["chatgpt", "ai", "ask"], prefixes=["+", ".", "/", "-", "?", "$", "#", "&"]))
async def chat_gpt(bot, message):
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            return await message.reply_text("Usage: /chatgpt <your question>")
        
        query = message.text.split(None, 1)[1]
        r = None
        try:
            res = api.chatgpt(query)
            if isinstance(res, dict):
                r = res.get("results") or res.get("result")
        except Exception:
            pass

        if not r:
            try:
                res = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(query)}", timeout=10)
                if res.status_code == 200 and res.text:
                    r = res.text.strip()
            except Exception:
                pass

        if not r:
            try:
                res = requests.get(f"https://apis.xditya.me/ai?text={requests.utils.quote(query)}", timeout=8)
                if res.status_code == 200:
                    r = res.json().get("result")
            except Exception:
                pass

        if not r:
            r = "Sorry, ChatGPT service is currently busy. Please try again later."

        await message.reply_text(f"{r}\n\n🎉 Powered by @{BOT_USERNAME}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

__mod_name__ = "Cʜᴀᴛɢᴘᴛ"
__help__ = """
 Cʜᴀᴛɢᴘᴛ ᴄᴀɴ ᴀɴsᴡᴇʀ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ  ᴀɴᴅ sʜᴏᴡs ʏᴏᴜ ᴛʜᴇ ʀᴇsᴜʟᴛ

 ❍ /chatgpt  *:* ʀᴇᴘʟʏ ᴛo ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ
 
 """
