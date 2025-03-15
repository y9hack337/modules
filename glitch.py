from pyrogram import Client, filters
import configparser, random, os
from pyrogram.types import Message
from pyrogram.enums import MessageMediaType
import io

commands = [
    {
        "cicon": "😈",
        "cinfo": "gl",
        "ccomand": "Глитч всего."
    }
]

config = configparser.ConfigParser()
config.read('userbot.cfg', "utf-8")
prefix_userbot = config['HACK337_USERBOT']['prefix_userbot'].split(',')

def register_commands(app):
    @app.on_message(filters.me & filters.command(["gl", 'glitch', 'glich', "пд", "гл"], prefixes=prefix_userbot))
    async def glitch(client: Client, message: Message):
        html = ["<b>{}<b>", "<code>{}</code>", "<i>{}</i>", "<del>{}</del>", "<u>{}</u>", '<a href="https://bruh.moment">{}</a>']
        headersize = {'jpg': 9, 'png': 8, 'bmp': 54, 'gif': 14, 'tiff': 8}
        reply = message.reply_to_message
        if reply and reply.media:
            file_bytes = io.BytesIO()
            file_bytes = await reply.download(in_memory=True)
            file_bytes.seek(0)
            file_name = file_bytes.name
            try:
                prompt = message.text.split(" ", 1)[1]
            except:
                pass
            percent = 0.1
            try:
                percent = float(prompt)
            except ValueError or TypeError:
                pass
            
            fileext = file_name.split(".")[-1]
            
            glitched_bytes = io.BytesIO()
            
            try:
                if fileext in headersize:
                    for _ in range(headersize[fileext]):
                        byte = file_bytes.read(1)
                        glitched_bytes.write(byte)
                
                while True:
                    byte = file_bytes.read(1)
                    if not byte:
                        break
                    if random.random() < percent / 100:
                        glitched_bytes.write(os.urandom(1))
                    else:
                        glitched_bytes.write(byte)
                
                glitched_bytes.seek(0)
                glitched_bytes.name = file_name
                try:
                    if reply.media == MessageMediaType.ANIMATION:
                        await client.send_animation(message.chat.id, glitched_bytes, reply_to_message_id=reply.id, unsave=True)
                    elif reply.media == MessageMediaType.VIDEO:
                        await reply.reply_video(glitched_bytes)
                    elif reply.media == MessageMediaType.STICKER:
                        await reply.reply_sticker(glitched_bytes)
                    elif reply.media == MessageMediaType.PHOTO:
                        await reply.reply_photo(glitched_bytes)
                    await message.delete()
                except Exception as e:
                    print(e)
                    await message.edit("Invalid arguments")
            except KeyError:
                await message.edit("Unsupported file type")
        else:
            await message.edit("Invalid arguments")


print("Модуль glitch загружен!")