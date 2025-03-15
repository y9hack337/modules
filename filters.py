from pyrogram import Client, filters, enums
import configparser

commands = [
    {
        "cicon": "📝",
        "cinfo": "f",
        "ccomand": "[all or me] + [text] + [reply] - добавить фильтр"
    },
    {
        "cicon": "📜",
        "cinfo": "fl",
        "ccomand": "Список фильтров"
    },
    {
        "cicon": "❌",
        "cinfo": "fr",
        "ccomand": "Удалить фильтр"
    },
    {
        "cicon": "🗑️",
        "cinfo": "frall",
        "ccomand": "Удалить все фильтры"
    },
]

filters_list_all = {}
filters_list_me = {}

config = configparser.ConfigParser()
config.read('userbot.cfg', "utf-8")
prefix_userbot = config['HACK337_USERBOT']['prefix_userbot'].split(',')

def register_commands(app):
    
    @app.on_message(filters.command(list(filters_list_all.keys()), prefixes=""))
    def all_module(client, message):
        if message.text in list(filters_list_all.keys()):
            message.reply_text(filters_list_all[message.text])
    
    @app.on_message(filters.me & filters.command(list(filters_list_me.keys()), prefixes=""))
    def me_module(client, message):
        if message.text in list(filters_list_all.keys()):
            message.edit(filters_list_me[message.text])
    
    @app.on_message(filters.me & filters.command("f", prefixes=prefix_userbot))
    def f_module(client, message):
        global filters_list_all, filters_list_me
        reply = message.reply_to_message
        if reply and reply.text and message.text:
            f_text = reply.text
            
            if len(message.text.split(" ")) < 3:
                message.edit("Ошибка")
                return
            _, mod ,f_user = message.text.split(" ", 2)
            if mod not in ["me", "all"]:
                message.edit("Ошибка")
                return
            if not f_user:
                message.edit("Ошибка")
                return
            
            if mod == "all":
                if f_user in filters_list_me:
                    message.edit("Ошибка")
                    return
                filters_list_all[f_user] = f_text
            elif mod == "me":
                if f_user in filters_list_all:
                    message.edit("Ошибка")
                    return
                filters_list_me[f_user] = f_text
            message.edit("Фильтр добавлен")
            register_commands(app)
        else:
            message.edit("Ошибка")
    
    @app.on_message(filters.me & filters.command("fl", prefixes=prefix_userbot))
    def fl_module(client, message):
        filters_str = ""
        filters_str+="Личные фильтры:\n<blockquote expandable>"
        for f_t, f_s in filters_list_me.items():
            filters_str+=f">{f_t}: {f_s}\n"
        filters_str = filters_str[:-1]+"</blockquote>\n"
        filters_str+="\nОбщие фильтры:\n<blockquote expandable>"
        for f_t, f_s in filters_list_all.items():
            filters_str+=f">{f_t}: {f_s}\n"
        filters_str = filters_str[:-1]+"</blockquote>"
        message.edit(filters_str , parse_mode=enums.ParseMode.HTML)
    
    @app.on_message(filters.me & filters.command("fr", prefixes=prefix_userbot))
    def fr_module(client, message):
        if len(message.text.split(" ")) < 2:
                message.edit("Ошибка")
                return
        _, f_user = message.text.split(" ", 1)
        if f_user in filters_list_me or f_user in filters_list_all:
            if f_user in filters_list_me:
                filters_list_me.pop(f_user)
            if f_user in filters_list_all:
                filters_list_all.pop(f_user)
            message.edit("Фильтр удалён")
            register_commands(app)
            return
        message.edit("Ошибка")
    
    @app.on_message(filters.me & filters.command("frall", prefixes=prefix_userbot))
    def frall_module(client, message):
        if len(message.text.split(" ")) < 2:
                message.edit("Ошибка")
                return
        filters_list_me.clear()
        filters_list_all.clear()
        message.edit("Все фильтры удалены")
        register_commands(app)


print("Модуль filters загружен!")