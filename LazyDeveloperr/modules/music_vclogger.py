#
# Copyright (C) 2025-present by TheAloneTeam@Github, < https://github.com/TheAloneTeam >.
#
# This file is part of < https://github.com/TheAloneTeam/KartikMusic > project,
# and is released under the "MIT License".
# Please see < https://github.com/TheAloneTeam/KartikMusic/blob/master/LICENSE >
#
# All rights reserved.
#

from pyrogram import filters, types

from LazyDeveloperr import app, db, lang
from LazyDeveloperr.music_helpers import can_manage_vc


@app.on_message(filters.command(["vclogger", "vclog"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _vclogger(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(m.lang["vclog_usage"].format(m.command[0]))

    state = m.command[1].lower()
    if state == "on":
        await db.set_vclogger(m.chat.id, True)
        await m.reply_text(m.lang["vclog_on"].format(m.from_user.mention))
    elif state == "off":
        await db.set_vclogger(m.chat.id, False)
        await m.reply_text(m.lang["vclog_off"].format(m.from_user.mention))
    else:
        await m.reply_text(m.lang["vclog_usage"].format(m.command[0]))
