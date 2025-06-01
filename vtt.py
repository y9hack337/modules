# requires: google-genai

import os
from pyrogram import Client, filters
from pyrogram.types import Message
import configparser, json
from google import genai
from google.genai import types as genai_types

commands = [
    {
        "cicon": "🎙️",
        "cinfo": "vtt",
        "ccomand": "Перевод гс в текст"
    }
]

config = configparser.ConfigParser()
config.read('userbot.cfg', "utf-8")
prefix_userbot = config['HACK337_USERBOT']['prefix_userbot'].split(',')

if 'GEMINI' not in config:
    model = None
    config['GEMINI'] = {'api_key': '<key>'}
    
    with open('userbot.cfg', 'w', encoding="utf-8") as configfile:
        config.write(configfile)
else:
    if config['GEMINI']["api_key"] != "<key>":
        model = genai.Client(api_key=config['GEMINI']["api_key"])
    else:
        model = None


def split_text(text, chunk_size=4000):
  chunks = []
  start = 0
  while start < len(text):
    end = min(start + chunk_size, len(text))
    chunks.append(text[start:end])
    start = end
  return chunks

def register_commands(app):
    @app.on_message(filters.me & filters.command(["мее", "vtt", "v2t"], prefixes=prefix_userbot))
    async def vtt_module(client: Client, message: Message):
        global model
        if message.text and len(message.text.split(" ")) == 3:
            if message.text.split(" ")[1] == "api":
                key = message.text.split(" ")[2]
                config['GEMINI']["api_key"] = key
                with open('userbot.cfg', 'w', encoding="utf-8") as configfile:
                    config.write(configfile)
                try:
                    model = genai.Client(api_key=config['GEMINI']["api_key"])
                    model.files.upload()
                    await message.edit("**✅API ключ установлен**")
                except:
                    await message.edit("**❌Не удалось установить API ключ**")
                return
        if ('GEMINI' not in config) or (config['GEMINI']["api_key"] == "<key>"):
            await message.edit("**🚫 Ключ API не предоставлен**\n`.vtt api <key>`\nhttps://aistudio.google.com/app/apikey", disable_web_page_preview=True)
            return
        try:
            reply = message.reply_to_message
            if reply:
                if reply.voice:
                    buffer_data = await reply._client.download_media( reply.voice.file_id, in_memory=True)
                    buffer_data.seek(0)
                    safety_settings=[
                        genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                        genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                        genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                        genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                        genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                    ]
                    myfile = model.files.upload(file=buffer_data, config=genai_types.UploadFileConfig(mime_type='audio/ogg'))
                    
                    response =  model.models.generate_content(
                        model="gemini-2.0-flash",
                        config=genai_types.GenerateContentConfig( safety_settings=safety_settings),contents=[
                            'Write the audio text in Russian without changes, comments and formatting.',
                            myfile
                        ])
                    
                    response_text = response.text
                    i=1
                    
                    for chunk in split_text(response_text):
                        if i==1:
                            await await message.edit(chunk)
                        else:
                            await reply.reply_text(chunk, reply_to_message_id=reply.id)
                        i+=1
        except Exception as e:
            await message.edit_text(f"```Ошибка!\n{str(e)}\n```")


print("Модуль Voice2text загружен!")
