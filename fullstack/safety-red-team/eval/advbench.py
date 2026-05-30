"""Optional loader for the public AdvBench harmful-behaviors set.

We never vendor AdvBench into the repo. With --load-advbench the runner fetches
it at runtime from its public source and buckets each goal into a coarse
category so the threat matrix stays meaningful.
"""

from __future__ import annotations

import csv
import io
import random
from typing import List

import httpx

_URL = (
    "https://raw.githubusercontent.com/llm-attacks/llm-attacks/"
    "main/data/advbench/harmful_behaviors.csv"
)

_CATEGORY_KEYWORDS = {
    "hacking": ["hack", "exploit", "unauthorized", "ddos", "network", "password", "breach"],
    "malware": ["malware", "virus", "ransomware", "worm", "keylogger", "trojan", "botnet"],
    "fraud": ["scam", "phish", "fraud", "counterfeit", "launder", "fake", "identity theft", "credit card"],
    "misinformation": ["fake news", "misinformation", "disinformation", "propaganda", "conspiracy"],
    "harassment": ["harass", "bully", "threaten", "stalk", "blackmail", "defame", "intimidat"],
    "privacy": ["track", "surveil", "spy", "locate", "personal information", "dox"],
    "violence": ["kill", "weapon", "attack", "assault", "violence", "hurt", "shoot"],
    "weapons-cbrn": ["bomb", "explosive", "biological", "chemical", "nuclear", "poison", "toxin"],
    "self-harm": ["suicide", "self-harm", "self harm", "starv"],
    "extremism": ["terror", "extremis", "radical"],
}


def _categorize(goal: str) -> str:
    g = goal.lower()
    for cat, kws in _CATEGORY_KEYWORDS.items():
        if any(k in g for k in kws):
            return cat
    return "other"


def load_advbench(n: int = 50, seed: int = 0) -> List[dict]:
    raw = httpx.get(_URL, timeout=30).text
    goals = [r["goal"].strip() for r in csv.DictReader(io.StringIO(raw)) if r.get("goal")]
    rng = random.Random(seed)
    rng.shuffle(goals)
    return [
        {"id": f"ab{i:03d}", "category": _categorize(g), "goal": g}
        for i, g in enumerate(goals[:n])
    ]
