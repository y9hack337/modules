import asyncio
import logging
import subprocess, os
import random
from pyrogram import Client, filters
from pyrogram.types import Message

from .. import loader, utils  # Assuming 'loader' and 'utils' are in the parent directory

logger = logging.getLogger(__name__)


@loader.tds
class DataMoshMod(loader.Module):
    """DataMosh effect to video"""
    strings = {
        "name": "DataMosh",
        "reply": "Reply to video!",
        "error": "ERROR! TRY AGAIN!!",
        "processing": "DataDataMoshMosh!",
    }

    @loader.unrestricted
    async def datamoshcmd(self, client: Client, message: Message):
        """. datamosh lvl: int <reply to video>"""
        fn = "if_you_see_it_then_delete_it"
        reply = await message.reply_to_message

        if not reply:
            await message.edit("".join([random.choice(html).format(ch) for ch in self.strings("reply", message)]))
            return
        if not reply.video:
            await message.edit("".join([random.choice(html).format(ch) for ch in self.strings("reply", message)]))
            return
        else:
            await client.download_media(reply, file_name=fn + "1.mp4")

        lvl = 1
        fp = False
        args = utils.get_args(message)
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

        await message.edit("".join([random.choice(html).format(ch) for ch in self.strings("processing", message)]))
        try:
            subprocess.run(
                f'ffmpeg -loglevel quiet -y -i {fn}1.mp4 -crf 0 -bf 0 {fn}1.avi',
                shell=True,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            await message.edit(f"FFmpeg error: {e.stderr.decode()}")
            os.system(f"rm -f {fn}*")
            return

        try:
            with open(fn + '1.avi', 'rb') as _f, open(fn + '2.avi', 'wb') as f_:
                frs = _f.read().split(b'00dc')
                fi = b'\x00\x01\xb0'
                cf = 0
                for _, fr in enumerate(frs):
                    if fp == False:
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
            await message.edit("".join([random.choice(html).format(ch) for ch in self.strings("error", message)]))
            os.system(f"rm -f {fn}*")
            return

        try:
            subprocess.run(
                f'ffmpeg -loglevel quiet -y -i {fn}2.avi {fn}2.mp4',
                shell=True,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            await message.edit(f"FFmpeg error: {e.stderr.decode()}")
            os.system(f"rm -f {fn}*")
            return
        
        try:
            await client.send_document(message.chat.id, document=fn + "2.mp4", caption="datamoshed") # Use send_document for general files
        except Exception as e:
            await message.edit(f"Error sending file: {e}")
            os.system(f"rm -f {fn}*")
            return

        os.system(f"rm -f {fn}*")
        await message.delete()


html = [
    "<b>{}</b>",
    "<code>{}</code>",
    "<i>{}</i>",
    "<del>{}</del>",
    "<u>{}</u>",
    '<a href="https://bruh.moment">{}</a>',
]