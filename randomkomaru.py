
# requires: requests

from pyrogram import Client, filters
import configparser, requests, json
from random import choice

commands = [
    {
        "cicon": "🐈",
        "cinfo": "rk",
        "ccomand": "Случайная гиф с Комару!"
    }
]

komaru = []
last_komaru = []

config = configparser.ConfigParser()
config.read('userbot.cfg', "utf-8")
prefix_userbot = config['HACK337_USERBOT']['prefix_userbot'].split(',')


if 'RANDOMKOMARU' not in config:
    model = None
    config['RANDOMKOMARU'] = {'api_key': '<key>'}
    
    with open('userbot.cfg', 'w', encoding="utf-8") as configfile:
        config.write(configfile)


def random_komaru():
    global komaru,last_komaru
    
    r = requests.get(
    "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % ("komaru cat", config['RANDOMKOMARU']["api_key"], "Hack337 UserBot",  100000)
    )
    if r.status_code == 200:
        top_8gifs = choice(json.loads(r.content)['results'])['media_formats']["gif"]['url']
        komaru = [gif['media_formats']["gif"]['url'] for gif in json.loads(r.content)['results']]
    else:
        if komaru:
            top_8gifs = choice(komaru)
        else:
            top_8gifs = None
    while top_8gifs in last_komaru:
        top_8gifs = choice(komaru)
    return top_8gifs


def register_commands(app):
    @app.on_message(filters.me & filters.command(["randkomaru","rk","рк","кд"], prefixes=prefix_userbot))
    async def randkomaru(client, message):
        global komaru,last_komaru
        
        if len(message.text.split(" ")) == 3:
            if message.text.split(" ")[1] == "api":
                key = message.text.split(" ")[2]
                config['RANDOMKOMARU']["api_key"] = key
                with open('userbot.cfg', 'w', encoding="utf-8") as configfile:
                    config.write(configfile)
                await message.edit("**✅API ключ установлен**")
                return
        
        if config['RANDOMKOMARU']["api_key"] == "<key>":
            await message.edit("**🚫 Ключ API не предоставлен**\n`.rk api <key>`\nhttps://developers.google.com/tenor/guides/quickstart?hl=ru#setup", disable_web_page_preview =True)
            return
        
        random_gif = random_komaru()
        if random_gif:
            try:
                await client.send_animation(message.chat.id, random_gif, unsave=True)
                last_komaru.append(random_gif)
                if len(last_komaru)>10:
                    last_komaru=last_komaru[1:]
            except:
                random_gif = choice(komaru)
                try:
                    await client.send_animation(message.chat.id, random_gif, unsave=True)
                    last_komaru.append(random_gif)
                    if len(last_komaru)>10:
                        last_komaru=last_komaru[1:]
                except:
                    await message.reply('Не удалось получить гифку. Попробуйте позже.')
        else:
            await message.reply('Не удалось получить гифку. Попробуйте позже.')
        await message.delete()

print("Модуль RandomKomaru загружен!")