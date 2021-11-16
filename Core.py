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
        logger.info("Receive update: %s", update)
        message = func(update, context)
        try:
            logger.info('Send "%s" to %s', message.replace(r"\n", r"\t"), update.effective_chat)
        except:
            logger.info(message)

    return log


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


@command_logger
def help(update, context):
    text = "\n".join([
        "/meow: 喵~",
        "/chance (事項1 事項2 事項3...): 預言家:求發生機率",
        "/fortune (事項1 事項2 事項3...): 占卜師:大吉or大凶?",
        "/pick 選項1 (選項2 選項3...): 機器喵點點名 ",
        "/string (長度) (0: 數字, 1: 小寫, 2: 大寫, 3: 符號) (數量): 亂數產生器",
    ])
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def meow(update, context):
    text = "喵~" if len(context.args) == 0 else update.message.text.split(maxsplit=1)[1]
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
        text = "喵?"
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def pick(update, context):
    text = Operation.pick(*context.args)
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def debug(update, context):
    L = context.args
    if len(L):
        type = L[0]
        if type == "cmd":
            n, cmd, options = int(L[1]), L[2], L[3:]
            if n > debug_max_n: n = debug_max_n
            text = Operation.debug_cmd(cmd, n=n, options=options)
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
    logger.info("Receive inline query: %s", update)
    input = update.inline_query.query
    L = update.inline_query.query.split()
    results = (
        InlineQueryResultArticle(
            str(uuid4()),
            "Meow~",
            InputTextMessageContent("喵~" if len(input) == 0 else input),
        ),
        InlineQueryResultArticle(
            str(uuid4()),
            "預言家: 求發生機率",
            InputTextMessageContent(Operation.chance(*L)),
            description="(事項1 事項2 事項3...)",
        ),
        InlineQueryResultArticle(
            str(uuid4()),
            "占卜師: 大吉or大凶?",
            InputTextMessageContent(Operation.fortune(*L)),
            description="(事項1 事項2 事項3...)",
        ),
        InlineQueryResultArticle(
            str(uuid4()),
            "機器喵點點名",
            InputTextMessageContent("喵?" if len(input) == 0 else Operation.pick(*L)),
            description="選項1 (選項2 選項3...)",
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
    dp.add_handler(CommandHandler("debug", debug))
    dp.add_handler(InlineQueryHandler(Inline))
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=Token, webhook_url=Webhook + Token)
    updater.idle()


if __name__ == '__main__':
    main()