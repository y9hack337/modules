from pyrogram import Client, filters
import configparser

commands = [
    {
        "cicon": "👋",
        "cinfo": "hi",
        "ccomand": "Привет!"
    },
    {
        "cicon": "🙋🏻‍♂️",
        "cinfo": "bye",
        "ccomand": "Пока!"
    },
]

config = configparser.ConfigParser()
config.read('userbot.cfg', "utf-8")
prefix_userbot = config['HACK337_USERBOT']['prefix_userbot'].split(',')

def register_commands(app):
    @app.on_message(filters.me & filters.command("hi", prefixes=prefix_userbot))
    async def hi_module(client, message):
        await message.edit("Привет!")
    
    @app.on_message(filters.me & filters.command("bye", prefixes=prefix_userbot))
    async def bye_module(client, message):
        await message.edit("Пока!")
    
    @app.on_message(filters.me & filters.command("test", prefixes=prefix_userbot))
    async def test_module(client, message):
        await message.edit("Пока!")

print("Модуль hi/bye загружен!")