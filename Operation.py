import logging
import string
import random
import re
import os
import json
import numpy as np
from collections import Counter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("Operation")


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
banlist = setup("banlist").split()
prob_range = tuple(map(int, setup("prob_range").split()))
fortune_key = setup("fortune_key").split()
fortune_prob = tuple(map(float, setup("fortune_prob").split()))


def bancheck(banned: list, check: list):
    for i in banned:
        for j in check:
            if re.search(str(i), str(j), flags=re.IGNORECASE):
                return True
    else:
        return False


def chance(*args, format=True, check=True):
    if check:
        if bancheck(banlist, args):
            return "窩不知道"
    n = len(args)
    prob = np.random.randint(*prob_range, size=n if n else 1)
    if format:
        if n == 0:
            return f"預言家算機率: 大約有{prob[0]}%機率發生"
        else:
            return "預言家算機率，結果為\n" + "\n".join([f"{args[i]}: {prob[i]}%" for i in range(n)])
    else:
        return prob


def fortune(*args, format=True, check=True):
    if check:
        if bancheck(banlist, args):
            return "窩不知道"
    n = len(args)
    rank = np.random.choice(fortune_key, size=n if n else 1, replace=True, p=fortune_prob)
    if format:
        if n == 0:
            return f"占卜師測運勢，結果為: 本日{rank[0]}"
        else:
            return "占卜師測運勢，結果為\n" + "\n".join([f"{args[i]}:{rank[i]}" for i in range(n)])
    else:
        return rank


def randstr(length: int = 8, type: list = [0], n: int = 1, format=True):
    pool = str()
    for i in type:
        try:
            pool += (string.digits, string.ascii_lowercase, string.ascii_uppercase, string.punctuation)[int(i)]
        except IndexError:
            continue
    getstring = lambda: "".join(np.random.choice(tuple(pool), int(length)))
    L = [getstring() for _ in range(int(n))]
    if format:
        return "亂數產生器\n" + "\n".join(L)
    else:
        return L


def pick(*args, format=True, check=True):
    if check:
        if bancheck(banlist, args):
            return "窩不知道"
    if len(args):
        if format:
            return "選項: " + ", ".join(args) + "\n機器喵選擇: " + random.choice(args)
        else:
            return random.choice(args)
    else:
        return "窩不知道"


def cmd_debugger(cmd, **kwargs):
    if cmd == "chance":
        n = int(kwargs["n"])
        result = Counter(chance(*range(n), format=False, check=False))
        text = f"n={n}\n" + "\n".join([f"{i}%: {j}, {j/n:.2%}" for i, j in sorted(result.items(), key=lambda x: x[0])])
    elif cmd == "fortune":
        n = kwargs["n"]
        result = Counter(fortune(*range(n), format=False, check=False))
        text = f"n={n}\n" + "\n".join([f"{i}: {j}, {j/n:.2%}" for i, j in sorted(result.items(), key=lambda x: x[0])])
    elif cmd == "pick":
        n = kwargs["n"]
        options = kwargs["options"]
        result = Counter([pick(*options, format=False, check=False) for _ in range(n)])
        text = f"n={n}\n" + "\n".join(
            [f"{i}: {j}, {j/n:.2%}" for i, j in sorted(result.items(), key=lambda x: options.index(x[0]))])
    else:
        text = "Not supported cmd"
    return text