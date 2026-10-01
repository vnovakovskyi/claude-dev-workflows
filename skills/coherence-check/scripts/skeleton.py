#!/usr/bin/env python3
"""Skeleton of a text for the coherence-check skill.

Prints what a structural editor reads first: the promise (title, excerpt),
every heading, the first sentence of every paragraph and list item, images and
tables as placeholders — all with line numbers. Then two lists to verify by hand:
back-references ("as I said above", "нижче", "далее") and announced counts
("three points:", "два рішення", "четыре шага").

Usage: skeleton.py <file> [--lang en|uk|ru]
Standard library only.
"""
import argparse
import re

BACKREF = {
    "en": r"\b(?:as (?:I|we) (?:said|mentioned|saw)|as mentioned|mentioned (?:above|earlier)|see (?:above|below)"
          r"|above|below|earlier|later|we'll (?:see|get|come)|we will (?:see|get|come)|remember)\b",
    "uk": r"\b(?:як (?:я |ми )?вже|як згадувалося|вище|нижче|далі|раніше|пізніше|побачимо|повернемося|пам'ятаєте)\b",
    "ru": r"\b(?:как (?:я |мы )?уже|как упоминалось|выше|ниже|далее|ранее|позже|увидим|вернёмся|вернемся|помните)\b",
}
NUMBERS = {
    "en": r"\b(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\b",
    "uk": r"\b(?:два|дві|двох|три|трьох|чотири|п'ять|п'яти|шість|сім|вісім|дев'ять|десять|\d+)\b",
    "ru": r"\b(?:два|две|двух|три|трёх|трех|четыре|пять|шесть|семь|восемь|девять|десять|\d+)\b",
}
COUNT_NOUNS = {
    "en": r"points?|steps?|reasons?|things?|ways?|decisions?|levels?|routes?|rules?|questions?|parts?|areas?|cases?",
    "uk": r"момент\w*|крок\w*|причин\w*|реч\w*|способ\w*|рішенн\w*|рів\w*|маршрут\w*|правил\w*|питан\w*|частин\w*|област\w*|випад\w*",
    "ru": r"момент\w*|шаг\w*|причин\w*|вещ\w*|способ\w*|решени\w*|уров\w*|маршрут\w*|правил\w*|вопрос\w*|част\w*|област\w*|случа\w*",
}


def detect_lang(text):
    if re.search(r"[іїєґІЇЄҐ]", text):
        return "uk"
    if re.search(r"[ыэъЫЭЪ]", text):
        return "ru"
    return "en"


def first_sentence(text, limit=160):
    text = re.sub(r"\s+", " ", text).strip()
    m = re.match(r"(.+?[.!?…:])(?:\s|$)", text)
    s = m.group(1) if m else text
    return s if len(s) <= limit else s[:limit].rstrip() + "…"


def clean(line):
    line = re.sub(r"`([^`]+)`", r"\1", line)
    line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
    return line.replace("**", "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--lang", choices=["en", "uk", "ru"])
    args = ap.parse_args()
    lines = open(args.file, encoding="utf-8").read().splitlines()
    lang = args.lang or detect_lang("\n".join(lines))

    print(f"# skeleton — {args.file} (language: {lang})\n")
    i = 0
    if lines and lines[0].strip() == "---":
        print("## promise (front matter)")
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            m = re.match(r"(title|description|excerpt|subtitle):\s*(.+)", lines[i])
            if m:
                value = m.group(2).strip().strip('"')
                print(f"L{i + 1} {m.group(1)}: {value}")
            i += 1
        i += 1
        print()

    print("## skeleton (headings and first sentences)")
    prose = {}  # line -> cleaned prose, for the checks below
    in_code, para_start, para = False, None, []

    def flush():
        nonlocal para_start, para
        if para:
            print(f"L{para_start}   {first_sentence(' '.join(para))}")
        para_start, para = None, []

    for n in range(i, len(lines)):
        raw = lines[n]
        ln = n + 1
        if raw.lstrip().startswith("```"):
            flush()
            if not in_code:
                print(f"L{ln}   [code]")
            in_code = not in_code
            continue
        if in_code:
            continue
        s = raw.strip()
        if not s:
            flush()
            continue
        if s.startswith("#"):
            flush()
            print(f"\nL{ln} {s}")
            continue
        if s.startswith("|"):
            if para_start != "table":
                flush()
                print(f"L{ln}   [table]")
                para_start = "table"
            continue
        if para_start == "table":
            para_start = None
        img = re.search(r'<img[^>]*alt="([^"]*)"', s)
        if img:
            flush()
            print(f"L{ln}   [image] {first_sentence(img.group(1), 90)}")
            continue
        if s in ("---", "***"):
            flush()
            print(f"L{ln}   [rule]")
            continue
        item = re.match(r"(?:[-*+]|\d+\.)\s+(.*)", s)
        text = clean(item.group(1) if item else re.sub(r"^>\s?", "", s))
        prose[ln] = text
        if item:
            flush()
            print(f"L{ln}     • {first_sentence(clean(item.group(1)), 110)}")
            continue
        if para_start is None:
            para_start = ln
        para.append(text)
    flush()

    print("\n## back-references (check that each points at something that is still there)")
    rx = re.compile(BACKREF[lang], re.IGNORECASE)
    hits = [(n, m.group(0), t) for n, t in prose.items() for m in rx.finditer(t)]
    for n, word, t in hits:
        print(f"L{n} «{word}»: {first_sentence(t, 120)}")
    if not hits:
        print("none")

    print("\n## announced counts (check that the count matches what follows)")
    rx = re.compile(rf"{NUMBERS[lang]}\s+(?:\w+\s+){{0,2}}(?:{COUNT_NOUNS[lang]})\b", re.IGNORECASE)
    found = False
    for n, t in prose.items():
        for m in rx.finditer(t):
            found = True
            print(f"L{n} «{m.group(0)}»: {first_sentence(t, 120)}")
    if not found:
        print("none")


if __name__ == "__main__":
    main()
