from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from uuid import uuid4
import logging
import os
import json
import Operation
from collections import Counter

try:
    Token = os.environ["Token"]
    Webhook = os.environ["Webhook"]
except:
    with open("config.json", encoding="utf-8") as f:
        cfg = json.load(f)
    Token = cfg["Token"]
    Webhook = cfg["Webhook"]
PORT = int(os.environ.get('PORT', 8443))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


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
        "/string (長度) (0: 數字, 1: 小寫, 2: 大小寫, 3: 大小寫+符號) (數量): 亂數產生器",
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
    list = context.args
    text = Operation.chance(list)
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def fortune(update, context):
    list = context.args
    text = Operation.fortune(list)
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def string(update, context):
    list = context.args
    L = [8, 0, 1]
    try:
        L[0] = int(list[0])
        if 0 <= int(list[1]) <= 3:
            L[1] = int(list[1])
        else:
            raise ValueError
        L[2] = int(list[2])
        text = Operation.random_string(L)
    except IndexError:
        text = Operation.random_string(L)
    except ValueError:
        text = "喵?"
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def pick(update, context):
    list = context.args
    if len(list) == 0:
        text = "喵?"
    else:
        text = Operation.pick(list)
    context.bot.send_message(update.effective_chat.id, text)
    return text


@command_logger
def debug(update, context):
    list = context.args
    if len(list):
        if list[0] == "cmd":
            n = int(list[1])
            if n > 1000000: n = 1000000
            if list[2] == "chance":
                result = Counter(Operation.chance(range(n), format=False, check=False))
                text = f"n={n}\n" + "\n".join(
                    [f"{i}%: {j}, {j/n:.2%}" for i, j in sorted(result.items(), key=lambda x: x[0])])
            elif list[2] == "fortune":
                result = Counter(Operation.fortune(range(n), format=False, check=False))
                text = f"n={n}\n" + "\n".join(
                    [f"{i}: {j}, {j/n:.2%}" for i, j in sorted(result.items(), key=lambda x: x[0])])
            elif list[2] == "pick":
                result = Counter([Operation.pick(list[3:], format=False, check=False) for _ in range(n)])
                text = f"n={n}\n" + "\n".join(
                    [f"{i}: {j}, {j/n:.2%}" for i, j in sorted(result.items(), key=lambda x: list[2:].index(x[0]))])
            else:
                text = "Not supported cmd"
        elif list[0] == "update":
            text = str(update)
        elif list[0] == "help":
            text = "\n".join(["/debug cmd n command [cmd_args]", "/debug update", "/debug help"])
        else:
            text = "Not supported mode"
    else:
        if update.effective_chat.type == "private":
            text = str(update)
        else:
            text = "Not supported"
    try:
        context.bot.send_message(update.effective_chat.id, text)
    except:
        pass
    return text


def Inline(update, context):
    logger.info("Receive inline query: %s", update)
    input = update.inline_query.query
    list = update.inline_query.query.split()
    results = (
        InlineQueryResultArticle(
            str(uuid4()),
            "Meow~",
            InputTextMessageContent("喵~" if len(input) == 0 else input),
        ),
        InlineQueryResultArticle(
            str(uuid4()),
            "預言家: 求發生機率",
            InputTextMessageContent(Operation.chance(list)),
            description="(事項1 事項2 事項3...)",
        ),
        InlineQueryResultArticle(
            str(uuid4()),
            "占卜師: 大吉or大凶?",
            InputTextMessageContent(Operation.fortune(list)),
            description="(事項1 事項2 事項3...)",
        ),
        InlineQueryResultArticle(
            str(uuid4()),
            "機器喵點點名",
            InputTextMessageContent("喵?" if len(input) == 0 else Operation.pick(list)),
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
    dp.add_handler(CommandHandler("string", string))
    dp.add_handler(CommandHandler("pick", pick))
    dp.add_handler(CommandHandler("debug", debug))
    dp.add_handler(InlineQueryHandler(Inline))
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=Token, webhook_url=Webhook + Token)
    updater.idle()


if __name__ == '__main__':
    main()
