# ?? **LazyLady Telegram Bot Engine**
### *The Ultimate Dual Voice Chat Music + Group Management + Interactive Social RP Bot*

> **Maintained & Created By:** [LazyDeveloper (t.me/LazyDeveloperr)](https://t.me/LazyDeveloperr)  
> **Repository:** [github.com/lazyindu/lazylady](https://github.com/lazyindu/lazylady)

---

## ?? **Key Features**
- ?? **PyTgCalls Voice Chat Music Engine**: High-quality audio/video streaming in voice chats with queue, pause, resume, skip, seek, and loop controls.
- ?? **Spotify Full Support**: Play single songs, albums, and playlists with automatic public oEmbed & HTML scraper fallbacks (100% working without API keys!).
- ?? **Interactive Social RP Engine (/kiss, /hug, /sex, /pat)**: Interactive roleplay commands with [ Accept ] button prompt, target callback validation, in-memory stream bytes fallback, and custom MongoDB image management (/set_*_img, /view_*_img, /remove, /removeall_*_img).
- ??? **Group Management**: Antiban, filters, welcome messages, locks, warns, reporting, and blacklist controls.
- ?? **Auto-Database File Logger**: Automatically backs up played audio & video files to your Database Channel (LOGGER_ID).

---

## ??? **Environment Variables Setup**

Create a .env file or set the following variables in your hosting provider:

| Variable | Description | Required |
|---|---|---|
| API_ID | Telegram API ID from [my.telegram.org](https://my.telegram.org) | **Yes** |
| API_HASH | Telegram API Hash from [my.telegram.org](https://my.telegram.org) | **Yes** |
| TOKEN | Bot Token from [@BotFather](https://t.me/BotFather) | **Yes** |
| OWNER_ID | Telegram User ID of the Bot Owner | **Yes** |
| LOGGER_ID | Database / Log Channel ID (e.g. -100123456789) | **Yes** |
| DATABASE_URL | PostgreSQL Database Connection URI | **Yes** |
| MONGO_DB_URI | MongoDB Connection URI (Atlas / Local) | **Yes** |
| SPOTIFY_CLIENT_ID | Optional Spotify Client ID | Optional |
| SPOTIFY_CLIENT_SECRET | Optional Spotify Client Secret | Optional |

---

## ?? **Deploy to Heroku**

Click the button below to deploy directly on Heroku:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/lazyindu/lazylady)

### **Heroku Deployment Steps:**
1. Click on the **Deploy to Heroku** button above.
2. Fill in all required environment variables (API_ID, API_HASH, TOKEN, OWNER_ID, LOGGER_ID, DATABASE_URL, MONGO_DB_URI).
3. Click **Deploy App**.
4. Once deployment finishes, go to the **Resources** tab and enable the worker dyno (worker: python3 -m LazyDeveloperr).
5. Your bot is now live!

---

## ?? **Deploy to VPS (Linux / Ubuntu / Debian)**

Follow these step-by-step commands to deploy on any VPS (DigitalOcean, AWS, Linode, Hetzner, Vultr):

### **Step 1: Update & Install System Dependencies**
`ash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv ffmpeg libopus0 libopus-dev git -y
`

### **Step 2: Clone the Repository**
`ash
git clone https://github.com/lazyindu/lazylady.git
cd lazylady
`

### **Step 3: Create & Activate Virtual Environment**
`ash
python3 -m venv env
source env/bin/activate
`

### **Step 4: Install Python Requirements**
`ash
pip3 install -r requirements.txt
`

### **Step 5: Create .env Configuration File**
`ash
nano .env
`
*Paste your environment variables into .env (Press Ctrl+O, Enter, Ctrl+X to save).*

### **Step 6: Run the Bot**
`ash
python3 -m LazyDeveloperr
`

### **Step 7: Keep Bot Running 24/7 in Background using screen or systemd**
`ash
# Using Screen:
screen -S lazybot
python3 -m LazyDeveloperr
# Press Ctrl+A then D to detach.

# To re-attach screen:
screen -r lazybot
`

---

## ?? **Credits & Channel**
- **Created & Maintained By:** [LazyDeveloper](https://t.me/LazyDeveloperr)
- **Telegram Channel:** [t.me/LazyDeveloperr](https://t.me/LazyDeveloperr)
- **GitHub Repository:** [github.com/lazyindu/lazylady](https://github.com/lazyindu/lazylady)
