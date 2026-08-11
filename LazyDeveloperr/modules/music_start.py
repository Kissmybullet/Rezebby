# ====================================================================================
# 💟 Reach Out @LazyDeveloperr 💟
# ------------------------------------------------------------------------------------
# 👑 Lead Engineer : Intkhab Ahmad (@LazyDeveloperr)
# 🐙 GitHub        : https://github.com/LazyDeveloperr
# 📸 Instagram     : https://instagram.com/LazyDeveloperr
# 📢 Telegram      : https://telegram.me/LazyDeveloperr
# ------------------------------------------------------------------------------------
# ✨ Features & Fixes in this Module:
#   🖼️ Removed extra duplicate message on /start so only one clean photo message is sent
# ====================================================================================

import asyncio

from pyrogram import enums, filters, types

from LazyDeveloperr import app, config, db, lang
from LazyDeveloperr.music_helpers import buttons, utils


# Pyrogram /help handler removed so PTB handles /help with Group Management buttons
# @app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
# @lang.language()
# async def _help(_, m: types.Message):
#     await m.reply_text(
#         text=m.lang["help_menu"],
#         reply_markup=buttons.help_markup(m.lang),
#         quote=True,
#     )


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    if message.from_user.id in app.bl_users and message.from_user.id not in db.notified:
        return await message.reply_text(message.lang["bl_user_notify"])

    # start=help handled natively by PTB handler

    private = message.chat.type == enums.ChatType.PRIVATE

    if private:
        if not await db.is_user(message.from_user.id):
            await utils.send_log(message)
            await db.add_user(message.from_user.id)
    else:
        if not await db.is_chat(message.chat.id):
            await utils.send_log(message, True)
            await db.add_chat(message.chat.id)


@app.on_message(
    filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users
)
@lang.language()
async def settings(_, message: types.Message):
    admin_only = await db.get_play_mode(message.chat.id)
    cmd_delete = await db.get_cmd_delete(message.chat.id)
    thumbnail = await db.get_thumb_mode(message.chat.id)
    autoplay = await db.get_autoplay(message.chat.id)
    _language = await db.get_lang(message.chat.id)
    await message.reply_text(
        text=message.lang["start_settings"].format(message.chat.title),
        reply_markup=buttons.settings_markup(
            message.lang,
            admin_only,
            cmd_delete,
            autoplay,
            thumbnail,
            _language,
            message.chat.id,
        ),
        quote=True,
    )


@app.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(_, message: types.Message):
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    await asyncio.sleep(3)
    bot_id = app.me.id if getattr(app, "me", None) else BOT_ID
    for member in message.new_chat_members:
        if member.id == bot_id:
            if await db.is_chat(message.chat.id):
                return
            await utils.send_log(message, True)
            await db.add_chat(message.chat.id)
