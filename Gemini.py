# requires: google-genai

from pyrogram import Client, filters
import configparser
from google import genai
from google.genai import types as genai_types

import os

commands = [
    {
        "cicon": "🤖",
        "cinfo": "gmn",
        "ccomand": "Gemini 2.0 Flash"
    },
    {
        "cicon": "🔍",
        "cinfo": "gmns",
        "ccomand": "Gemini с поиском"
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


def register_commands(app):
    @app.on_message(filters.me & filters.command(["gmn", "гмн", "пьт", "gemini", "gmns", "гмнс"], prefixes=prefix_userbot))
    async def gemini(client, message):
        global model
        
        if message.text and len(message.text.split(" ")) == 3:
            if message.text.split(" ")[1] == "api":
                key = message.text.split(" ")[2]
                config['GEMINI']["api_key"] = key
                with open('userbot.cfg', 'w', encoding="utf-8") as configfile:
                    config.write(configfile)
                try:
                    model = genai.Client(api_key=config['GEMINI']["api_key"])
                    await message.edit("**✅API ключ установлен**")
                except:
                    await message.edit("**❌Не удалось установить API ключ**")
                return
        if ('GEMINI' not in config) or (config['GEMINI']["api_key"] == "<key>"):
            await message.edit("**🚫 Ключ API не предоставлен**\n`.gmn api <key>`\nhttps://aistudio.google.com/app/apikey", disable_web_page_preview=True)
            return
        reply = message.reply_to_message
        have_img = False
        if reply and (reply.text or reply.caption):
            user = reply.text or reply.caption
            if (message.text or message.caption).count(" ") > 0:
                user = (message.text or message.caption).split(" ",1)[1] + "\n" + (reply.text or reply.caption)
            else:
                user = (reply.text or reply.caption)
            if reply.photo:
                have_img = await reply._client.download_media(reply.photo.file_id)
        elif reply and reply.photo:
            if (message.text or message.caption).count(" ") > 0:
                user = (message.text or message.caption).split(" ",1)[1]
            else:
                await message.edit("❌**Invalid arguments**")
                return
            have_img = await reply._client.download_media(reply.photo.file_id)
        else:
            if (message.text or message.caption).count(" ") > 0:
                user = (message.text or message.caption).split(" ",1)[1]
            else:
                await message.edit("❌**Invalid arguments**")
                return
            if message.photo:
                have_img = await message._client.download_media(message.photo.file_id)
        use_search = message.command[0].lower() in ["gmns", "гмнс"]
        model_name = "Gemini 2.0 Flash" + (" с поиском" if use_search else "")
        await message.edit_text(f'```User\n{user}\n``````{model_name}\nГенерация...\n```')
        try:
            if have_img:
                with open(have_img, 'rb') as f:
                    img_bytes = f.read()
                tools = None
                if use_search:
                    tools = genai_types.ToolListUnion([genai_types.Tool(google_search=genai_types.GoogleSearch)])
                
                safety_settings=[
                    genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                    genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                    genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                    genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                    genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                ]
                
                contents = [
                    {"role": "user", "parts": [
                        {"text": user},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_bytes}}
                    ]}
                ]
                
                response =  model.models.generate_content(
                    model="gemini-2.0-flash",
                    config=genai_types.GenerateContentConfig( safety_settings=safety_settings, tools=tools),contents=contents)
                
                response_text = response.text
                try:
                    os.remove(have_img)
                except:
                    pass
                have_img = None
            else:
                tools = None
                if use_search:
                    tools = genai_types.ToolListUnion([genai_types.Tool(google_search=genai_types.GoogleSearch)])
                
                safety_settings=[
                    genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                    genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                    genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                    genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                    genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,),
                ]
                
                contents = [
                    {"role": "user", "parts": [{"text": user}]}
                ]
                
                response =  model.models.generate_content(
                    model="gemini-2.0-flash",
                    config=genai_types.GenerateContentConfig( safety_settings=safety_settings, tools=tools),contents=contents)
                
                response_text = response.text
        except Exception as e:
            if have_img:
                try:
                    os.remove(have_img)
                except:
                    pass
            print(e)
            await message.edit_text(f'```User\n{user}\n``````{model_name}\n{str(e)}\n```')
            return
        if have_img:
            try:
                os.remove(have_img)
            except:
                pass
        if '`' in response_text:
            await message.edit_text(f'```User\n{user}\n```\n{response_text}')
        else:
            await message.edit_text(f'```User\n{user}\n``````{model_name}\n{response_text}\n```')


print("Модуль Gemini загружен!")