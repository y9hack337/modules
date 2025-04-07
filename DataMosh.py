from pyrogram import Client, filters
from pyrogram.types import Message
import configparser
import asyncio
import logging
import subprocess, os
import random

logger = logging.getLogger(__name__)

commands = [
    {
        "cicon": "😵‍💫",
        "cinfo": "datamosh",
        "ccomand": "datamosh"
    },
]

config = configparser.ConfigParser()
config.read('userbot.cfg', "utf-8")
prefix_userbot = config['HACK337_USERBOT']['prefix_userbot'].split(',')

strings = {
    "reply": "Reply to video!",
    "error": "ERROR! TRY AGAIN!!",
    "processing": "DataDataMoshMosh!"
}

html = ["<b>{}<b>", "<code>{}</code>", "<i>{}</i>", "<del>{}</del>", "<u>{}</u>", '<a href="https://bruh.moment">{}</a>']

# Define the register_commands function outside of any class or conditional
def register_commands(app):
    @app.on_message(filters.me & filters.command("datamosh", prefixes=prefix_userbot))
    async def datamosh_module(client: Client, message: Message):
        """Datamosh effect to video. .datamosh lvl: int <reply to video>"""
        fn = "if_you_see_it_then_delete_it"
        reply = message.reply_to_message
        if not reply:
            await message.edit("".join([ random.choice(html).format(ch) for ch in strings["reply"]]))
            return
        if not reply.video and not reply.video_note:
            await message.edit("".join([ random.choice(html).format(ch) for ch in strings["reply"]]))
            return

        lvl = 1
        fp = False
        args = message.text.split()[1:]  # Split message text and remove command

        if args:
            if len(args) == 1:
                if args[0].isdigit():
                    lvl = int(args[0])
                    if lvl <= 0:
                        lvl = 1
                else:
                    fp = True
            if len(args) > 1:
                fp = True
                if args[0].isdigit():
                    lvl = int(args[0])
                    if lvl <= 0:
                        lvl = 1
                elif args[1].isdigit():
                    fp = True
                    lvl = int(args[1])
                    if lvl <= 0:
                        lvl = 1

        await message.edit("".join([ random.choice(html).format(ch) for ch in strings["processing"]]))
        
        try:
            await reply.download(fn + "1.mp4")
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            await message.edit("".join([ random.choice(html).format(ch) for ch in strings["error"]]))
            os.system(f"rm -f {fn}*")
            return
            

        subprocess.call(f'ffmpeg -loglevel quiet -y -i {fn}1.mp4 -crf 0 -bf 0 {fn}1.avi', shell=True)
        try:
            with open(fn+'1.avi', 'rb') as _f, open(fn+'2.avi', 'wb') as f_:
                frs = _f.read().split(b'00dc')
                fi = b'\x00\x01\xb0'
                cf = 0
                for _, fr in enumerate(frs):
                    if not fp:
                        f_.write(fr + b'00dc')
                        cf += 1
                        if fr[5:8] == fi:
                            fp = True
                    else:
                        if fr[5:8] != fi:
                            cf += 1
                            for i in range(lvl):
                                f_.write(fr + b'00dc')

        except FileNotFoundError:
            await message.edit("".join([ random.choice(html).format(ch) for ch in strings["error"]]))
            os.system(f"rm -f {fn}*")
            return
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            await message.edit("".join([ random.choice(html).format(ch) for ch in strings["error"]]))
            os.system(f"rm -f {fn}*")
            return
        

        subprocess.call(f'ffmpeg -loglevel quiet -y -i {fn}2.avi {fn}2.mp4', shell=True)
        try:
            await client.send_video(message.chat.id, video=fn+"2.mp4", video_note=reply.video_note)
        except Exception as e:
            logger.error(f"Error sending video: {e}")
            await message.edit("".join([ random.choice(html).format(ch) for ch in strings["error"]]))
            os.system(f"rm -f {fn}*")
            return

        os.system(f"rm -f {fn}*")
        await message.delete()

print("Модуль DataMosh загружен!")
