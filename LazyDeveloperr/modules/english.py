import json
import requests
from telethon import events
from LazyDeveloperr.events import register


@register(pattern=r"^/spell(?:@\w+)?(?:\s+(.*))?")
async def _(event):
    ctext = await event.get_reply_message()
    msg = (event.pattern_match.group(1) or "").strip()
    if not msg and ctext:
        msg = ctext.text or ""
    if not msg:
        return await event.reply("Reply to a message or provide text for spell checking!")

    try:
        url = f"https://api.datamuse.com/words?sp={requests.utils.quote(msg)}&max=1"
        res = requests.get(url, timeout=5).json()
        if res:
            await event.reply(f"Suggested Spelling: {res[0]['word']}")
        else:
            await event.reply(f"No spelling corrections found for: {msg}")
    except Exception as e:
        await event.reply(f"Spell check error: {e}")


@register(pattern=r"^/define(?:@\w+)?(?:\s+(.+))?")
async def _(event):
    word = (event.pattern_match.group(1) or "").strip()
    if not word:
        return await event.reply("Usage: `/define <word>`")
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{requests.utils.quote(word)}"
        res = requests.get(url, timeout=8).json()
        if isinstance(res, list) and res:
            meanings = res[0].get("meanings", [])
            out = f"**Word:** {word.capitalize()}\n"
            for m in meanings[:2]:
                pos = m.get("partOfSpeech", "")
                defs = [d["definition"] for d in m.get("definitions", [])[:2]]
                out += f"\n_{pos}_:\n• " + "\n• ".join(defs)
            await event.reply(out)
        else:
            await event.reply(f"No definition found for `{word}`.")
    except Exception as e:
        await event.reply(f"Error fetching definition: {e}")


@register(pattern=r"^/synonyms(?:@\w+)?(?:\s+(.+))?")
async def _(event):
    word = (event.pattern_match.group(1) or "").strip()
    if not word:
        return await event.reply("Usage: `/synonyms <word>`")
    try:
        url = f"https://api.datamuse.com/words?rel_syn={requests.utils.quote(word)}&max=10"
        res = requests.get(url, timeout=5).json()
        if res:
            syns = ", ".join([w["word"] for w in res])
            await event.reply(f"**Synonyms for `{word}`:**\n{syns}")
        else:
            await event.reply(f"No synonyms found for `{word}`.")
    except Exception as e:
        await event.reply(f"Error: {e}")


@register(pattern=r"^/antonyms(?:@\w+)?(?:\s+(.+))?")
async def _(event):
    word = (event.pattern_match.group(1) or "").strip()
    if not word:
        return await event.reply("Usage: `/antonyms <word>`")
    try:
        url = f"https://api.datamuse.com/words?rel_ant={requests.utils.quote(word)}&max=10"
        res = requests.get(url, timeout=5).json()
        if res:
            ants = ", ".join([w["word"] for w in res])
            await event.reply(f"**Antonyms for `{word}`:**\n{ants}")
        else:
            await event.reply(f"No antonyms found for `{word}`.")
    except Exception as e:
        await event.reply(f"Error: {e}")


__help__ = """
 ❍ /define <word> : Type the word or expression you want to search
 ❍ /spell : Reply to a message or pass text to get spelling suggestion
 ❍ /synonyms <word> : Find synonyms of a word
 ❍ /antonyms <word> : Find antonyms of a word
"""

__mod_name__ = "Eɴɢʟɪsʜ"
