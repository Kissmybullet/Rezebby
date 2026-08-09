from pyrogram import Client, enums, filters
import asyncio
from LazyDeveloperr import pbot as mukesh


@mukesh.on_message(filters.command(["dice", "ludo"]))
async def dice_cmd(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "🎲")
        m = x.dice.value
        user = message.from_user.mention if message.from_user else "User"
        await message.reply_text(f"Hey {user}, your score is : {m}", quote=True)
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@mukesh.on_message(filters.command("dart"))
async def dart_cmd(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "🎯")
        m = x.dice.value
        user = message.from_user.mention if message.from_user else "User"
        await message.reply_text(f"Hey {user}, your score is : {m}", quote=True)
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@mukesh.on_message(filters.command(["basket", "basketball"]))
async def basket_cmd(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "🏀")
        m = x.dice.value
        user = message.from_user.mention if message.from_user else "User"
        await message.reply_text(f"Hey {user}, your score is : {m}", quote=True)
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@mukesh.on_message(filters.command(["jackpot", "slot"]))
async def jackpot_cmd(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "🎰")
        m = x.dice.value
        user = message.from_user.mention if message.from_user else "User"
        await message.reply_text(f"Hey {user}, your score is : {m}", quote=True)
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@mukesh.on_message(filters.command(["ball", "bowling"]))
async def ball_cmd(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "🎳")
        m = x.dice.value
        user = message.from_user.mention if message.from_user else "User"
        await message.reply_text(f"Hey {user}, your score is : {m}", quote=True)
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@mukesh.on_message(filters.command("football"))
async def football_cmd(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "⚽")
        m = x.dice.value
        user = message.from_user.mention if message.from_user else "User"
        await message.reply_text(f"Hey {user}, your score is : {m}", quote=True)
    except Exception as e:
        await message.reply_text(f"Error: {e}")


__help__ = """
 Play Game With Emojis:
/dice - Dice 🎲
/dart - Dart 🎯
/basket - Basket Ball 🏀
/ball - Bowling Ball 🎳
/football - Football ⚽
/jackpot - Spin slot machine 🎰
 """

__mod_name__ = "Dɪᴄᴇ"
