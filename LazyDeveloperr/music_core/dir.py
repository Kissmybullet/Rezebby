# ====================================================================================
# 💟 Reach Out @LazyDeveloperr 💟
# ------------------------------------------------------------------------------------
# 👑 Lead Engineer : Intkhab Ahmad (@LazyDeveloperr)
# 🐙 GitHub        : https://github.com/LazyDeveloperr
# 📸 Instagram     : https://instagram.com/LazyDeveloperr
# 📢 Telegram      : https://telegram.me/LazyDeveloperr
# ------------------------------------------------------------------------------------
# ✨ Features & Fixes in this Module:
#   🎥 Automatic FFmpeg binary provisioning using static_ffmpeg fallback for Heroku
# ====================================================================================

import shutil
from pathlib import Path

from LazyDeveloperr import logger


def ensure_dirs():
    """
    Ensure that the necessary directories exist and FFmpeg is available.
    """
    if not shutil.which("ffmpeg"):
        try:
            import static_ffmpeg
            static_ffmpeg.add_paths()
            logger.info("Auto-installed FFmpeg via static_ffmpeg.")
        except Exception as e:
            logger.warning(f"static_ffmpeg auto-install failed: {e}")

    for dir_name in ["cache", "downloads"]:
        p = Path(dir_name)
        p.mkdir(parents=True, exist_ok=True)
        if dir_name == "downloads":
            for f in p.glob("*.*"):
                try:
                    f.unlink()
                except Exception:
                    pass
    logger.info("Cache and downloads directories purged and updated.")
