import random

from telegram import ChatAction, ParseMode

from LazyDeveloperr import dispatcher
from LazyDeveloperr.modules.disable import DisableAbleCommandHandler

GIF = (
    "https://telegra.ph/file/ef94f2f61aa4d9394ef23.mp4",
    "https://telegra.ph/file/b82442bf9ebc32534f7a2.mp4",
    "https://telegra.ph/file/70d43e136125f9c120d2e.mp4",
    "https://telegra.ph/file/45354d3e42982f8de78f4.mp4",
    "https://telegra.ph/file/a22a0930f069686a0c4ef.mp4",
)


def wish(update, context):
    message = update.message
    if message.reply_to_message:
        mm = random.randint(1, 100)
        context.bot.send_chat_action(
            chat_id=message.chat_id, action=ChatAction.UPLOAD_VIDEO
        )
        fire = "https://telegra.ph/file/cae00f6c0729da2a93315.mp4"
        try:
            context.bot.send_video(
                chat_id=message.chat_id,
                video=fire,
                caption=f"**ʜᴇʏ [{message.from_user.first_name}](tg://user?id={message.from_user.id}), ᴜsᴇ /wish (ʏᴏᴜʀ ᴡɪsʜ) 🙃**",
                reply_to_message_id=message.reply_to_message.message_id,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as e:
            print(e)
            context.bot.send_message(
                chat_id=message.chat_id,
                text="ᴏᴏᴘs, sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ! ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
            )
    else:
        mm = random.randint(1, 100)
        fire = random.choice(GIF)
        context.bot.send_chat_action(
            chat_id=message.chat_id, action=ChatAction.UPLOAD_VIDEO
        )
        try:
            context.bot.send_video(
                chat_id=message.chat_id,
                video=fire,
                caption=f"**ʜᴇʏ [{message.from_user.first_name}](tg://user?id={message.from_user.id}), ʏᴏᴜʀ ᴡɪsʜ ʜᴀs ʙᴇᴇɴ ᴄᴀsᴛ.💜**\n__ᴄʜᴀɴᴄᴇ ᴏғ sᴜᴄᴄᴇss ⭐ {mm}%__",
                reply_to_message_id=message.message_id,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as e:
            print(e)
            context.bot.send_message(
                chat_id=message.chat_id,
                text="ᴏᴏᴘs, sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ! ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
            )


wish_handler = DisableAbleCommandHandler("wish", wish)
dispatcher.add_handler(wish_handler)


__help__ = """
ᴀ ғᴜɴ ᴡᴀʏ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴡɪsʜ ɢʀᴀɴᴛᴇᴅ...

➢ /wish *:* ᴍᴀᴋᴇ ᴀ ᴡɪsʜ ᴀɴᴅ sᴇᴇ ɪᴛs ᴘᴏssɪʙɪʟɪᴛʏ.
"""

__mod_name__ = "Wɪsʜ 🎋"
