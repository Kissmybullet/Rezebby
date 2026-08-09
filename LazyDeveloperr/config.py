
class Config(object):
    LOGGER = True
    # REQUIRED
    # Login to https://my.telegram.org and fill in these slots with the details given by it

    API_ID = "" # integer value, dont use ""
    API_HASH = ""
    TOKEN = ""  # This var used to be API_KEY but it is now TOKEN, adjust accordingly.
    OWNER_ID = 2145093972 # If you dont know, run the bot and do /id in your private chat with it, also an integer
    
    SUPPORT_CHAT = "the_support_chat"  # Your own group for support, do not add the @
    START_IMG = ""
    EVENT_LOGS = ()  # Prints information like gbans, sudo promotes, AI enabled disable states that may help in debugging and shit
    MONGO_DB_URI= ""
    # RECOMMENDED
    DATABASE_URL = ""  # A sql database url from elephantsql.com
    CASH_API_KEY = (
        ""  # Get your API key from https://www.alphavantage.co/support/#api-key
    )
    TIME_API_KEY = ""
    
    # Get your API key from https://timezonedb.com/api


    # Optional fields
    BL_CHATS = []  # List of groups that you want blacklisted.
    DRAGONS = []  # User id of sudo users
    DEV_USERS = []  # User id of dev users
    DEMONS = []  # User id of support users
    TIGERS = []  # User id of tiger users
    WOLVES = []  # User id of whitelist users

    ALLOW_CHATS = True
    ALLOW_EXCL = True
    DEL_CMDS = True
    INFOPIC = True
    LOAD = []
    NO_LOAD = []
    STRICT_GBAN = True
    TEMP_DOWNLOAD_DIRECTORY = "./"
    WORKERS = 8

    # Music Bot Settings
    MONGO_URL = ""
    SESSION = ""
    SESSION2 = ""
    SESSION3 = ""
    DURATION_LIMIT = 3600
    QUEUE_LIMIT = 20
    PLAYLIST_LIMIT = 20
    AUTO_LEAVE = False
    AUTO_END = False
    THUMB_GEN = True
    VIDEO_PLAY = True
    LANG_CODE = "en"
    COOKIES_URL = []
    DEFAULT_THUMB = "https://te.legra.ph/file/3e40a408286d4eda24191.jpg"
    PING_IMG = "https://files.catbox.moe/haagg2.png"
    LOGGER_ID = 0
    

class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
