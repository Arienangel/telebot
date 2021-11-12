import string
import random
import re
import os
import json
import numpy as np

try:
    banlist = os.environ["banlist"].split()
    prob_range = tuple(map(int, os.environ["prob_range"].split()))
    fortune_key = os.environ["fortune_key"].split()
    fortune_prob = tuple(map(float, os.environ["fortune_prob"].split()))
except:
    with open("config.json", encoding="utf-8") as f:
        cfg = json.load(f)
    banlist = cfg["banlist"].split()
    prob_range = tuple(map(int, cfg["prob_range"].split()))
    fortune_key = cfg["fortune_key"].split()
    fortune_prob = tuple(map(float, cfg["fortune_prob"].split()))


def bancheck(banned: list, check: list):
    for i in banned:
        for j in check:
            if re.search(i, j):
                return True
    else:
        return False


def chance(list, format=True, check=True):
    if check:
        if bancheck(banlist, list):
            return "窩不知道"
    n = len(list)
    prob = np.random.randint(*prob_range, size=n if n else 1)
    if n == 0:
        if format:
            return f"預言家算機率: 大約有{prob[0]}%機率發生"
        else:
            return prob
    else:
        if format:
            return "預言家算機率，結果為\n" + "\n".join([f"{list[i]}: {prob[i]}%" for i in range(n)])
        else:
            return prob


def fortune(list, format=True, check=True):
    if check:
        if bancheck(banlist, list):
            return "窩不知道"
    n = len(list)
    rank = np.random.choice(fortune_key, n if n else 1, True, fortune_prob)
    if n == 0:
        if format:
            return f"占卜師測運勢，結果為: 本日{rank[0]}"
        else:
            return rank
    else:
        if format:
            return "占卜師測運勢，結果為\n" + "\n".join([f"{list[i]}:{rank[i]}" for i in range(n)])
        else:
            return rank


def random_string(list, format=True):
    pool = (string.digits, string.ascii_lowercase, string.ascii_letters, string.punctuation + string.ascii_letters)[list[1]]
    getstring = lambda: "".join(np.random.choice(tuple(pool), list[0]))
    L = [getstring() for _ in range(list[2])]
    if format:
        return "亂數產生器\n" + "\n".join(L)
    else:
        return L


def pick(list, format=True, check=True):
    if check:
        if bancheck(banlist, list):
            return "窩不知道"
    if len(list):
        if format:
            return "選項: " + ", ".join(list) + "\n機器喵選擇: " + random.choice(list)
        else:
            return random.choice(list)
    else:
        return "窩不知道"