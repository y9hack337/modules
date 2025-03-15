from pyrogram import Client, filters
import configparser
import re

commands = [
    {
        "cicon": "📸",
        "cinfo": "shot",
        "ccomand": "Сделать фото сайта."
    }
]

def links(text):
  url_pattern = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
  return re.findall(url_pattern, text)

config = configparser.ConfigParser()
config.read('userbot.cfg', "utf-8")
prefix_userbot = config['HACK337_USERBOT']['prefix_userbot'].split(',')

def register_commands(app):
    @app.on_message(filters.me & filters.command(["shot","ырще"], prefixes=prefix_userbot))
    async def shot_module(client, message):
        
        reply = message.reply_to_message 
        if reply and reply.text:
            link = links(reply.text)
        elif len(message.text.split(" ")) > 1:
            link = links(message.text)
        else:
            await message.edit("❌Ссылка не найдена.")
            return
        if link:
            await message.edit(f"📸Фоткаю сайт ({link[0]}) ...")
            await message.reply_photo(f"https://mini.s-shot.ru/1024x768/JPEG/1024/Z100/?{link[0]}")
            await message.delete()
        else:	
            await message.edit("❌Ссылка не найдена.")

print("Модуль shot загружен!")
