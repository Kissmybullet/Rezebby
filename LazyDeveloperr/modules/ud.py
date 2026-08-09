import requests
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from LazyDeveloperr import dispatcher
from LazyDeveloperr.modules.disable import DisableAbleCommandHandler


def ud(update: Update, context: CallbackContext):
    message = update.effective_message
    if not context.args:
        message.reply_text("Usage: `/ud <search text>`", parse_mode=ParseMode.MARKDOWN)
        return
    text = " ".join(context.args)
    try:
        results = requests.get(
            f"https://api.urbandictionary.com/v0/define?term={text}", timeout=10
        ).json()
        if results.get("list"):
            definition = results["list"][0]["definition"]
            example = results["list"][0]["example"]
            reply_text = f"*{text}*\n\n{definition}\n\n_{example}_"
        else:
            reply_text = "No results found."
    except Exception as e:
        reply_text = f"Error fetching definition: {e}"
    message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)


UD_HANDLER = DisableAbleCommandHandler(["ud"], ud, run_async=True)

dispatcher.add_handler(UD_HANDLER)

__help__ = """
» /ud (text) *:* sᴇᴀʀᴄʜs ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ ᴏɴ ᴜʀʙᴀɴ ᴅɪᴄᴛɪᴏɴᴀʀʏ ᴀɴᴅ sᴇɴᴅs ʏᴏᴜ ᴛʜᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.
"""
__mod_name__ = "Uʀʙᴀɴ"

__command_list__ = ["ud"]
__handlers__ = [UD_HANDLER]
