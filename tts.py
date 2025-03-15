from pyrogram import Client, filters
from pyrogram.types import Message
import configparser
import edge_tts, asyncio
from pydub import AudioSegment
from io import BytesIO
from tempfile import NamedTemporaryFile

commands = [
    {
        "cicon": "👨‍💻",
        "cinfo": "tts",
        "ccomand": "Озвучить текст мужским голосом."
    },
    {
        "cicon": "👩‍💻",
        "cinfo": "ttsg",
        "ccomand": "Озвучить текст женским голосом."
    },
]

config = configparser.ConfigParser()
config.read('userbot.cfg', "utf-8")
prefix_userbot = config['HACK337_USERBOT']['prefix_userbot'].split(',')

async def text_to_ogg(text: str, man: bool) -> BytesIO:
        VOICE = "ru-RU-DmitryNeural" if man else "ru-RU-SvetlanaNeural"
        communicate = edge_tts.Communicate(text, VOICE)
        with NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3:
            audio_fname = temp_mp3.name
            await communicate.save(audio_fname)
        output_ogg = BytesIO()
        sound = AudioSegment.from_mp3(audio_fname)
        sound.export(output_ogg, format="ogg")
        temp_mp3.close()
        output_ogg.seek(0)
        output_ogg.name = "msg.ogg"
        return output_ogg

def register_commands(app):
    @app.on_message(filters.me & filters.command(["tts","ттс","ееы"], prefixes=prefix_userbot))
    async def tts(client: Client, message: Message):
        reply = message.reply_to_message
        if reply and reply.text:
            user = reply.text
        else:
            user = message.text.split(" ",1)[1]
        voice = await text_to_ogg(user, True)
        await client.send_voice(message.chat.id, voice,reply_to_message_id=message.id)

    @app.on_message(filters.me & filters.command(["ttsg","ттсг","ееып"], prefixes=prefix_userbot))
    async def ttsg(client: Client, message: Message):
        reply = message.reply_to_message
        if reply and reply.text:
            user = reply.text.split(" ",1)[1]
        else:
            user = message.text.split(" ",1)[1]
        voice = await text_to_ogg(user, False)
        await client.send_voice(message.chat.id, voice,reply_to_message_id=message.id)

print("Модуль tts загружен!")
