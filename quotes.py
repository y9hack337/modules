
# requires: requests imageio Pillow regex

from pyrogram import filters
import configparser
from pyrogram.types import Message, User
from base64 import b64encode
import requests
from dataclasses import dataclass
from html import escape
from io import BytesIO
import imageio as iio
from PIL import Image
import regex
import json
import time

def _create_regexp(group_name: str, group_regexp: str, isRequired: bool) -> str:
    try: regex.compile(group_regexp)
    except regex.error as ex: raise ValueError(f"regexp {group_regexp!r} is invalid! {ex!r}.")
    formatter = r"(?:(?P<{}>{})(?: |$)){}".format(group_name, group_regexp, "" if isRequired else "?")
    return formatter

session = requests.Session()

settings = {"bg_color": "#162330", "text_color": "#ffffff"}
defaults_settings = {"bg_color": "#162330", "text_color": "#ffffff"}

QUOTE_ARGUMENTS = dict(command=r"[\.ю]\w+", count=r"\d+", reply=r"r|-r|reply|-reply", file=r"!file|file", hex=r"#[\dA-Fa-f]{6}")
FQUOTE_ARGUMENTS = dict(command=r"\.\w+", reply=r"r|-r|reply|-reply", file=r"!file|file", hex=r"#[\dA-Fa-f]{6}", text=r".+")

quote_regexp = "".join([_create_regexp(n, v, n in ["command"]) for (n, v) in QUOTE_ARGUMENTS.items()])
fquote_regexp = "".join([_create_regexp(n, v, n in ["command", "text"]) for (n, v) in FQUOTE_ARGUMENTS.items()])

commands = [
    {
        "cicon": "👋",
        "cinfo": "q",
        "ccomand": "[5] [-r/-reply/reply] [!file/file] [#ANYHEX] — создать цитату из сообщений"
    },
    {
        "cicon": "🙋🏻‍♂️",
        "cinfo": "fq",
        "ccomand": "[-r/-reply/reply] [!file/file] [#ANYHEX] текст — создать фейк цитату"
    },
]

config = configparser.ConfigParser()
config.read('userbot.cfg', "utf-8")
prefix_userbot = config['HACK337_USERBOT']['prefix_userbot'].split(',')

def register_commands(app):
    @app.on_message(filters.me & filters.command(["q","й"], prefixes=prefix_userbot))
    async def q_module(client, message):
        result = await quote_cmd(message)
        if isinstance(result, str):
            await message.reply_text(escape(result))
            await message.delete()

        elif isinstance(result, BytesIO):
            await message.reply_to_message.reply_document(result, quote=True)
            await message.delete()
    
    @app.on_message(filters.me & filters.command("fq", prefixes=prefix_userbot))
    async def fq_module(client, message):
        result = await fake_quote_cmd(message)
        if isinstance(result, str):
            await message.reply_text(escape(result))
            await message.delete()

        elif isinstance(result, BytesIO):
            await message.reply_to_message.reply_document(result, quote=True)
            await message.delete()

print("Модуль quotes загружен!")


def quote_set_cmd(message):
    args = message.text.split(" ")[1:]

    if not args:
        bg_color = settings['bg_color']
        text_color = settings['text_color']
        result = f"""Текущие цвета:
    • Цвет фона: {bg_color}
    • Цвет текста: {text_color}

Изменить цвет: .qset bg_color/text_color #ANYHEX
Поставить цвета по-умолчанию: .qset reset
"""
        return result
    
    color_parameters = ["bg_color", "text_color"]
    possible_parameters = color_parameters + ['reset']
    
    parameter = args[0]
    argument = args[1] if len(args) > 1 else None
    
    parameterIsValid = parameter in possible_parameters
    parameterIsColor = parameter in color_parameters
    parameterIsReset = parameter == "reset"
    
    argumentIsColor = argument and (argument.startswith("#") and argument.removeprefix("#").isalnum())
    argumentIsColorParameter = argument in color_parameters
    
    if not parameterIsValid:
        return f'Неизвестный параметр. Принимаются только значения {", ".join(possible_parameters)}.' 
        
    elif parameterIsColor and not argumentIsColor:
        return 'Неизвестный цвет. Формат цвета: #AbCdEf'
    
    elif parameterIsColor and argumentIsColor:
        hexColor = argument
        settings[parameter] = hexColor
        result = f'Для {parameter} установлено значение {hexColor}'
        return result
    
    elif parameterIsReset and argumentIsColorParameter:
        string = dict(bg_color="фона", text_color="текста")[argument]
        settings.update(string, defaults_settings[string])
        result = f"Цвет {string} сброшен с {settings[string]} на {defaults_settings[string]}"
        return result
    
    elif parameterIsReset and argument is None:
        settings = defaults_settings
        return "Настройки сброшены!"
    
    else:
        return "Что ты захотел, сам то понял?"


async def quote_cmd(message):
    if not (rtm:=message.reply_to_message):
        return "Required reply!"
    
    count, isReply, isFile, textColor = _parse_quote_args(message)
    messages = await _get_messages(rtm, count)
    
    print(" *  creating quote...")
    result = await _rpost(messages, text_color=textColor, isFile=isFile, isReply=isReply)
    return result


async def fake_quote_cmd(message):
    if not (rtm:=message.reply_to_message):
        return "Required reply!"
    
    isReply, isFile, textColor, text = _parse_fquote_args(message)

    print(" *  creating fake quote...")
    result = await _fpost(rtm, text, textColor, isFile, isReply)
    return result


def _parse_quote_args(message):
    quote_argument_parser = regex.compile(quote_regexp, flags=regex.MULTILINE)

    matched = quote_argument_parser.match(message.text)
    if matched is None:
        print(quote_argument_parser.pattern)
        return f"WTH anekdot with pattern..."

    # print(repr(matched.groups(None)), "\n\n")
    _count, _isReply, _isFile, _hexColor = matched.group(2), matched.group(3), matched.group(4), matched.group(5)
    count = int(_count) if _count else 1
    isReply = bool(_isReply)
    isFile = bool(_isFile)
    textColor = _hexColor or "#FFFFFF"
    return [count, isReply, isFile, textColor]


def _parse_fquote_args(message):
    fquote_argument_parser = regex.compile(fquote_regexp, flags=regex.MULTILINE)
    
    matched = fquote_argument_parser.match(message.text)
    if matched is None:
        print(fquote_argument_parser.pattern)
        return f"WTH anekdot with pattern..."

    # print(repr(matched.groups(None)), "\n\n")
    _, _isReply, _isFile, _hexColor, _text = matched.groups(None)
    isReply = bool(_isReply)
    isFile = bool(_isFile)
    textColor = _hexColor or "#FFFFFF"
    text = _text
    return (isReply, isFile, textColor, text)

@dataclass(frozen=True, unsafe_hash=True, eq=True)
class _MyAuthor:
    id: int
    """from_user.id"""
    name: str
    """display name"""
    avatar: str = ""
    """base64 encoded avatar"""
    rank: str = ""
    """admin's rank (ex creator, admin or empty)"""
    via_bot: str = ""
    """if message created via bot, when bot's username"""

    def to_json(self) -> dict:
        return dict(
            id = self.id,
            name = self.name,
            avatar = self.avatar,
            rank = self.rank,
            via_bot = self.via_bot
        )

@dataclass(frozen=True, unsafe_hash=True, eq=True)
class _MyReply:
    id: int
    """some id (idk)"""
    name: str
    """reply's author display name"""
    text: str = ""
    """reply's text"""

    def to_json(self) -> dict:
        return dict(
            id = self.id,
            name = self.name,
            text = self.text
        )

@dataclass(frozen=True, unsafe_hash=True, eq=True)
class _MyMessage:
    text: str
    """message's text"""
    media: str
    """base64 encoded media"""
    author: _MyAuthor
    """message's author"""
    reply: _MyReply | None
    """message which this replied to"""

    async def from_message(message, isReply=False):
        text = message.text or message.caption 
        if text is None:
            text= ""
        media = await _download_media(message) or ""
        author_id = message.from_user.id
        author_name = message.from_user.full_name
        author_avatar = await _download_avatar(message.from_user) or ""
        author_rank = await _get_rank(message)
        author_via_bot = (message.via_bot and message.via_bot.username) or ""
        author = _MyAuthor(author_id, author_name, author_avatar, author_rank, author_via_bot)
        rtm = message.reply_to_message
        
        if rtm and isReply:
            reply_id = rtm.id
            reply_name = rtm.from_user.full_name

            reply_media_text = _get_message_text(rtm, True)
            reply_text = "{}{}".format(reply_media_text, (rtm.text if rtm.text and reply_media_text else rtm.text or ""))
            reply = _MyReply(reply_id, reply_name, reply_text)
        else:
            reply = _MyReply(0, "", "")

        msg = _MyMessage(text, media, author, reply)
        return msg

    def to_json(self):
        return dict(
            text = self.text,
            media = self.media,
            author = self.author.to_json(),
            reply = (self.reply and self.reply.to_json())
        )

@dataclass(frozen=True, unsafe_hash=True, eq=True)
class _MessageForPost:
    messages: list[_MyMessage]
    """Messages in quote"""
    quote_color: str = settings['bg_color']
    """Background color in HEX"""
    text_color: str = settings['text_color']
    """Foreground color in HEX"""

    async def from_messages(messages, bg_color=None, text_color=None, isReply=False):
        msgs = [ await _MyMessage.from_message(msg, isReply) for msg in messages]
        return _MessageForPost(msgs, bg_color or settings['bg_color'], text_color or settings['text_color'])
    
    def to_json(self) -> dict:
        return dict(
            messages = [msg.to_json() for msg in self.messages],
            quote_color = self.quote_color,
            text_color = self.text_color
        )


async def _get_messages(message, count: int = 1):
    gen = message._client.get_chat_history(message.chat.id, limit=count, offset_id=(message).id + count, offset=0)
    messages_list = []
    async for msg in gen:
        messages_list.append(msg.id)
    messagesWithoutReply = messages_list[::-1]
    messages = await message._client.get_messages(message.chat.id, messagesWithoutReply)
    return messages


async def _get_rank(message):
    client = message._client
    user = message.from_user
    chat = message.chat
    try:
        member = await client.get_chat_member(chat.id, user.id)
        rank = member.custom_title or ""
    except Exception:
        rank = ""
    return rank


async def _rpost(messages, text_color=None, isFile=False, isReply=False):
    payload = (await _MessageForPost.from_messages(messages, text_color=text_color, isReply=isReply)).to_json()
    
    return _post(payload, isFile)


async def _fpost(message, msg_text, text_color=None, isFile=False, isReply=False):
    fake_message_dict = message.__dict__.copy()
    fake_message_dict['text'] = msg_text
    fake_message_dict.pop('_client', None)
    fake_message = Message(**fake_message_dict)
    payload = await _MessageForPost.from_messages([fake_message], text_color=text_color, isReply=isReply).to_json()

    return _post(payload, isFile)

def _post(payload, isFile):
    request = session.post("https://quotes.fl1yd.su/generate", timeout=600, json=payload)

    if request.status_code != 200:
        return f"Error with parsing. \n{json.dumps(request.json(), indent=2)}"

    response = request.content
    response_io = BytesIO(response)
    response_io.name = "Quote" + (".png" if isFile else ".webp")
    return response_io


async def _download_avatar(user):
    """Download user's avatar as base64 encoded string"""
    photo = user.photo
    if photo is None:
        return None
    photo_bytes: BytesIO = await user._client.download_media(photo.big_file_id, in_memory=True)
    result = b64encode(photo_bytes.getbuffer()).decode()
    return result

def mp4_to_png(video_bytesio):
    reader = iio.v3.imread(video_bytesio, extension=".mp4")
    first_frame = reader[0]
    if first_frame.ndim == 3 and first_frame.shape[2] in (4,):
        first_frame = first_frame[:, :, :3]
    output_bytesio = BytesIO()
    iio.v3.imwrite(output_bytesio, first_frame, extension=".png", format="PNG")
    output_bytesio.seek(0)
    image = Image.open(output_bytesio)
    width, height = image.size
    new_width = 128
    new_height = int((new_width / width) * height)
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
    output_bytesio_v2 = BytesIO()
    resized_image.save(output_bytesio_v2, format='PNG')
    output_bytesio_v2.seek(0)
    return output_bytesio_v2

async def _download_media(message):
    """Download message's media as base64 encoded string"""
    file_id = await _get_media(message)
    if file_id is None:
        return ""
    media = await message._client.download_media(file_id, in_memory=True)
    #print(media.name)
    #if media.name.endswith(".mp4") or media.name.endswith(".webp"):
    #    media = mp4_to_png(media)
    
    result = b64encode(media.getbuffer()).decode()
    return result


async def _get_media(message):
    """Get some downloadable media from message"""
    file_ids = [
        n.thumbs[-1].file_id for n in [
            message.animation,
            message.video,
            message.video_note,
            message.web_page,
            message.sticker
        ] if n and n.thumbs
    ] or None

    if file_ids is None and message.photo:
        file_ids = [ message.photo.file_id ]
    
    if file_ids is None:
        return None
    file_id = file_ids[0]
    return file_id


def _get_message_text(message, reply = False):
    if message.photo and reply:
        return "📷 Фото"
        
    elif message.sticker and reply:
        return (message.sticker.emoji or "") + " Стикер"
        
    elif message.video_note and reply:
        return "📹 Видеосообщение"
    
    elif message.video and reply:
        return "📹 Видео"
    
    elif message.animation and reply:
        return "🖼 GIF"
    
    elif message.poll:
        return "📊 Опрос"
    
    elif message.location:
        return "📍 Местоположение"
    
    elif message.contact:
        return "👤 Контакт"
    
    elif message.voice:
        return f"🎵 Голосовое сообщение: {_time_to_string(message.voice.duration)}"
    
    elif message.audio:
        return f"🎧 Музыка: {_time_to_string(message.audio.duration)} | {message.audio.title}"
    
    elif message.document and not _get_media(message):
        return f"💾 Файл: {message.document.file_name}"
    
    elif message.dice:
        return f"{message.dice.emoji} Дайс: {message.media.value}"
    
    elif message.service:
        return f"Service message: {message.service.__dict__['_value_']}"
    
    else:
        return ""


def _time_to_string(_time):
    t = time.gmtime(_time)
    result = ":".join([str(n).rjust(2, "0") for n in [t.tm_yday-1, t.tm_hour, t.tm_min, t.tm_sec] if n > 0])
    # result = (f"{t.tm_hour:0>2}:" if t.tm_hour > 0 else "") + f"{t.tm_min:0>2}:{t.tm_sec::0>2}"
    return result




