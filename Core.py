from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from uuid import uuid4
import logging
import os
import json
import Operation

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("Core")


def setup(key, default=""):
    if key in cfg:
        logger.info('Setup "%s" from config.json', key)
        return cfg[key]
    elif key in os.environ.keys():
        logger.info('Setup "%s" from environment variable', key)
        return os.environ.get(key)
    else:
        logger.info('Setup "%s" from default value', key)
        return default


if os.path.exists("config.json"):
    with open("config.json", encoding="utf-8") as f:
        cfg = json.load(f)
else:
    cfg = dict()
Token = setup("Token")
Webhook = setup("Webhook")
PORT = int(setup('PORT', 8443))
debug_max_n = int(setup("debug_max_n", 10000000))


def command_logger(func):
    def log(update, context):
        chat_type = update.effective_chat.type
        if chat_type=="group" or chat_type=="supergroup":
            logger.info('Receive bot command "%s" from "%s" send by "%s"', update.effective_message.text, update.effective_chat.title, update.effective_user.full_name)
        elif chat_type=="private":
            logger.info('Receive bot command "%s" send by "%s"', update.effective_message.text, update.effective_user.full_name)
        message = func(update, context)
        try:
            if chat_type=="group" or chat_type=="supergroup":
                logger.info('Send "%s" to %s', message.replace(r"\n", r"\t"), update.effective_chat.title)
            elif chat_type=="private":
                logger.info('Send "%s" to %s', message.replace(r"\n", r"\t"), update.effective_user.full_name)
        except:
            logger.info(f'{message}')

    return log


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update.effective_message.text, context.error)


@command_logger
def help(update, context):
    text = "\n".join([
        "/meow: ???~",
        "/chance (??????1 ??????2 ??????3...): ?????????:???????????????",
        "/fortune (??????1 ??????2 ??????3...): ?????????:??????or???????",
        "/pick ??????1 (??????2 ??????3...): ?????????????????? ",
        "/string (??????) (0: ??????, 1: ??????, 2: ??????, 3: ??????) (??????): ???????????????",
    ])
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def meow(update, context):
    text = "???~" if len(context.args) == 0 else update.effective_message.text.split(maxsplit=1)[1]
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def chance(update, context):
    text = Operation.chance(*context.args)
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def fortune(update, context):
    text = Operation.fortune(*context.args)
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def randstr(update, context):
    L = context.args
    try:
        L[1] = tuple(L[1])
    except IndexError:
        pass
    try:
        text = Operation.randstr(*L)
    except:
        text = "????"
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def pick(update, context):
    text = Operation.pick(*context.args)
    context.bot.send_message(update.effective_chat.id, text)
    return text

@command_logger
def dice(update, context):
    if context.args:
        emoji=['????', '????', '????', '???', '????', '????'][int(context.args[0])]
    else:
        emoji='????'
    context.bot.send_dice(update.effective_chat.id, emoji=emoji)
    return emoji

@command_logger
def debug(update, context):
    L = context.args
    if len(L):
        type = L[0]
        if type == "cmd":
            n, cmd, options = int(L[1]), L[2], L[3:]
            if n > debug_max_n: n = debug_max_n
            text = Operation.cmd_debugger(cmd, n=n, options=options)
        elif type == "update":
            text = str(update)
        elif type == "help":
            text = "\n".join(["/debug cmd n command [options]", "/debug update", "/debug help"])
        else:
            text = "Not supported debug type"
    else:
        if update.effective_chat.type == "private":
            text = str(update)
        else:
            text = "Not supported"
    context.bot.send_message(update.effective_chat.id, text)
    return text


def Inline(update, context):
    chat_type = update.inline_query.chat_type
    if chat_type=="group" or chat_type=="supergroup":
        logger.info('Receive inline query "%s" from "%s" send by "%s', update.inline_query.query, update.effective_chat.title, update.effective_user.full_name)
    elif chat_type=="private":
        logger.info('Receive inline query "%s" send by "%s"', update.inline_query.query, update.effective_user.full_name)
    input = update.inline_query.query
    L = update.inline_query.query.split()
    results = (
        InlineQueryResultArticle(
            str(uuid4()),
            "Meow~",
            InputTextMessageContent("???~" if len(input) == 0 else input),
        ),
        InlineQueryResultArticle(
            str(uuid4()),
            "?????????: ???????????????",
            InputTextMessageContent(Operation.chance(*L)),
            description="(??????1 ??????2 ??????3...)",
        ),
        InlineQueryResultArticle(
            str(uuid4()),
            "?????????: ??????or???????",
            InputTextMessageContent(Operation.fortune(*L)),
            description="(??????1 ??????2 ??????3...)",
        ),
        InlineQueryResultArticle(
            str(uuid4()),
            "??????????????????",
            InputTextMessageContent(Operation.pick(*L)),
            description="??????1 (??????2 ??????3...)",
        ),
    )
    update.inline_query.answer(results, cache_time=0)


def main():
    updater = Updater(Token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("meow", meow))
    dp.add_handler(CommandHandler("chance", chance))
    dp.add_handler(CommandHandler("fortune", fortune))
    dp.add_handler(CommandHandler("string", randstr))
    dp.add_handler(CommandHandler("pick", pick))
    dp.add_handler(CommandHandler("dice", dice))
    dp.add_handler(CommandHandler("debug", debug))
    dp.add_handler(InlineQueryHandler(Inline))
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=Token, webhook_url=Webhook + Token)
    updater.idle()


if __name__ == '__main__':
    main()