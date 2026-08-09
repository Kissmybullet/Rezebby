import os
from time import sleep

from telethon import *
from telethon.errors import *
from telethon.errors import FloodWaitError, UserNotParticipantError
from telethon.tl import *
from telethon.tl import functions, types
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import *
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantCreator,
    ChatBannedRights,
)

from LazyDeveloperr import *
from LazyDeveloperr import LOGGER
from LazyDeveloperr.events import register

BOT_ID = 5285688815
CMD_HELP = "/ !"


# ================================================


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await telethn(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


@register(pattern=r"^/unbanall(?:@\w+)?$")
async def _(event):
    chat = await event.get_chat()
    admin_rights = getattr(chat, 'admin_rights', None)
    admin = getattr(admin_rights, 'ban_users', False) if admin_rights else False
    creator = getattr(chat, 'creator', False)
    if event.is_private:
        return await event.respond(
            "__ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜsᴇ ɪɴ ɢʀᴏᴜᴘs ᴀɴᴅ ᴄʜᴀɴɴᴇʟs!__"
        )

    is_admin = False
    try:
        LazyDeveloperr = await telethn(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            LazyDeveloperr.participant,
            (
                ChannelParticipantAdmin,
                ChannelParticipantCreator,
            ),
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("__ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴʙᴀɴᴀʟʟ!__")

    if not admin and not creator:
        await event.reply("`ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴘᴇʀᴍɪssɪᴏɴs!`")
        return

    done = await event.reply("sᴇᴀʀᴄʜɪɴɢ ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ ʟɪsᴛs")
    p = 0
    async for i in telethn.iter_participants(
        event.chat_id, filter=ChannelParticipantsKicked, aggressive=True
    ):
        rights = ChatBannedRights(until_date=None, view_messages=False)
        try:
            await telethn(
                functions.channels.EditBannedRequest(event.chat_id, i, rights)
            )
        except FloodWaitError as ex:
            LOGGER.warn(f"sʟᴇᴇᴘɪɴɢ ғᴏʀ {ex.seconds} sᴇᴄᴏɴᴅs")
            sleep(ex.seconds)
        except Exception as ex:
            await event.reply(str(ex))
        else:
            p += 1

    if p == 0:
        await done.edit("ɴᴏ ᴏɴᴇ ɪs ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ")
        return
    required_string = "sᴜᴄᴇssғᴜʟʟʏ ᴜɴʙᴀɴɴᴇᴅ **{}** ᴜsᴇʀs"
    await event.reply(required_string.format(p))


@register(pattern=r"^/unmuteall(?:@\w+)?$")
async def _(event):
    if event.is_private:
        return await event.respond(
            "__This command can be use in groups and channels!__"
        )

    is_admin = False
    try:
        LazyDeveloperr = await telethn(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            LazyDeveloperr.participant,
            (
                ChannelParticipantAdmin,
                ChannelParticipantCreator,
            ),
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("__ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴍᴜᴛᴇᴀʟʟ!__")
    chat = await event.get_chat()
    admin_rights = getattr(chat, 'admin_rights', None)
    admin = getattr(admin_rights, 'ban_users', False) if admin_rights else False
    creator = getattr(chat, 'creator', False)

    # Well
    if not admin and not creator:
        await event.reply("`I don't have enough permissions!`")
        return

    done = await event.reply("Working ...")
    p = 0
    async for i in telethn.iter_participants(
        event.chat_id, filter=ChannelParticipantsBanned, aggressive=True
    ):
        rights = ChatBannedRights(
            until_date=None,
            send_messages=False,
        )
        try:
            await telethn(
                functions.channels.EditBannedRequest(event.chat_id, i, rights)
            )
        except FloodWaitError as ex:
            LOGGER.warn(f"sʟᴇᴇᴘɪɴɢ ғᴏʀ {ex.seconds} sᴇᴄᴏɴᴅs")
            sleep(ex.seconds)
        except Exception as ex:
            await event.reply(str(ex))
        else:
            p += 1

    if p == 0:
        await done.edit("ɴᴏ ᴏɴᴇ ɪs ᴍᴜᴛᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ")
        return
    required_string = "sᴜᴄᴇssғᴜʟʟʏ ᴜɴᴍᴜᴛᴇᴅ **{}** ᴜsᴇʀs"
    await event.reply(required_string.format(p))


@register(pattern=r"^/users(?:@\w+)?$")
async def get_users(show):
    if not show.is_group:
        return
    if not await is_register_admin(show.input_chat, show.sender_id):
        return
    info = await telethn.get_entity(show.chat_id)
    title = info.title or "this chat"
    mentions = f"ᴜsᴇʀs ɪɴ {title}: \n"
    async for user in telethn.iter_participants(show.chat_id):
        mentions += (
            f"\nᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs  {user.id}"
            if user.deleted
            else f"\n[{user.first_name}](tg://user?id={user.id}) ❣ {user.id}"
        )

    with open("userslist.txt", "w+") as file:
        file.write(mentions)
    await telethn.send_file(
        show.chat_id,
        "userslist.txt",
        caption=f"ᴜsᴇʀs ɪɴ {title}",
        reply_to=show.id,
    )

    os.remove("userslist.txt")


__mod_name__ = "Aᴅᴠᴀɴᴄᴇ"
__help__ = """

➥ /unbanall : ᴜɴʙᴀɴ ᴀʟʟ ᴍᴀᴍʙᴇʀ 

➥ /unmuteall : ᴜɴᴍᴜᴛᴇ ᴀʟʟ ᴍᴀᴍʙᴇʀ

➥ /users : ɢᴇᴛ ɢʀᴏᴜᴘ ᴜsᴇʀs ʟɪsᴛ

"""
