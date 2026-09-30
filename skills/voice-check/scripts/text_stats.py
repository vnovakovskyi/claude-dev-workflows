#!/usr/bin/env python3
"""Rough text statistics for the voice-check skill.

Prints signals, not verdicts: the things a reader notices but a model is bad at
counting by eye — sentence rhythm, punctuation density, repeated openers, filler
words, and a few construction patterns, each with line numbers.

Usage: text_stats.py <file> [--lang en|uk|ru]
Standard library only. Code blocks, front matter, HTML tags, tables and inline
code are excluded from the prose.
"""
import argparse
import re
import statistics
from collections import Counter, defaultdict

WATCH = {
    "en": ["just", "really", "actually", "simply", "basically", "essentially", "truly",
           "crucial", "powerful", "robust", "seamless", "leverage", "delve", "moreover",
           "furthermore", "additionally", "ultimately", "notably", "importantly"],
    "uk": ["саме", "просто", "лише", "насправді", "тож", "отже", "таким чином", "власне",
           "фактично", "по суті", "справді", "дійсно", "варто", "слід", "дозволя",
           "здійсню", "забезпечу", "ключов", "важлив", "ефективн", "потужн", "даний",
           "наступним чином", "у рамках", "в рамках", "у свою чергу"],
    "ru": ["именно", "просто", "лишь", "на самом деле", "по сути", "таким образом",
           "действительно", "фактически", "стоит", "следует", "позволя", "осуществля",
           "обеспечива", "ключев", "важн", "эффективн", "мощн", "данный", "является",
           "являются", "в рамках", "в свою очередь"],
}

PATTERNS = {
    "en": {
        "not X, but Y": r"\bnot (?:just|only)\b[^.?!]{0,80}\bbut\b|\bisn't (?:just|about)\b"
                        r"|\b(?:is|are|was|does)\s+not\b[^.?!]{0,80}[.;—]\s*(?:it|they|this|that)\s+(?:is|are|was|does)\b",
        "colon reveal": r"\b(?:here's|here is|the (?:rule|answer|trick|point|thing|catch) is)\b[^.?!:]{0,40}:",
        "signposting": r"\blet's (?:break|dive|unpack|look|start|take)\b|\bin this (?:article|post)\b|\bit(?:'s| is) worth noting\b",
    },
    "uk": {
        "не X, а Y": r"\bне\b[^.?!]{1,80},\s*а\b|\bце не\b[^.?!]{1,80}[.—]\s*це\b|\bа не\b",
        "давайте / розгляньмо": r"\bдавайте\b|\bрозгляньмо\b|\bрозглянемо\b|\bрозберімо\b|\bзануримося\b",
        "є як зв'язка": r"\b(?:є|являє собою|являється)\s+[\w'ʼ-]+(?:им|ою|ом|ими|ою)\b",
        "двокрапка-розкриття": r"\b(?:ось що|ось як|правило таке|насправді правило)\b[^.?!:]{0,40}:",
    },
    "ru": {
        "не X, а Y": r"\bне\b[^.?!]{1,80},\s*а\b|\bэто не\b[^.?!]{1,80}[.—]\s*это\b|\bа не\b",
        "давайте / рассмотрим": r"\bдавайте\b|\bрассмотрим\b|\bразбер[её]мся\b|\bпогрузимся\b",
        "является": r"\bявля(?:ется|ются)\b",
        "двоеточие-раскрытие": r"\b(?:вот что|вот как|правило такое)\b[^.?!:]{0,40}:",
    },
}

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
WORD = re.compile(r"[\w'ʼ’-]+", re.UNICODE)


def detect_lang(text):
    if re.search(r"[іїєґІЇЄҐ]", text):
        return "uk"
    if re.search(r"[ыэъЫЭЪ]", text):
        return "ru"
    return "en"


def prose_lines(raw):
    """Yield (line_no, kind, text) for prose, with markup stripped."""
    lines = raw.splitlines()
    i = 0
    if lines and lines[0].strip() == "---":  # front matter
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    in_code = False
    for n in range(i, len(lines)):
        line = lines[n]
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or line.lstrip().startswith("|") or not line.strip():
            yield n + 1, "blank", ""
            continue
        kind = "heading" if line.startswith("#") else "item" if re.match(r"\s*(?:[-*+]|\d+\.)\s", line) else "para"
        text = re.sub(r"<[^>]+>", " ", line)
        text = re.sub(r"`[^`]+`", "CODE", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"^\s*(?:#+|>|[-*+]|\d+\.)\s*", "", text)
        if text.strip():
            yield n + 1, kind, text
        else:
            yield n + 1, "blank", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--lang", choices=["en", "uk", "ru"])
    args = ap.parse_args()
    raw = open(args.file, encoding="utf-8").read()
    lang = args.lang or detect_lang(raw)

    units, cur = [], None  # paragraphs / list items: {start, kind, text}
    raw_lines = {}
    for n, kind, text in prose_lines(raw):
        raw_lines[n] = text
        if kind in ("blank", "heading", "item") or cur is None:
            if cur:
                units.append(cur)
            cur = None if kind in ("blank", "heading") else {"start": n, "kind": kind, "text": text}
        else:
            cur["text"] += " " + text
    if cur:
        units.append(cur)

    sentences = []
    for u in units:
        for s in re.split(r"(?<=[.!?…])\s+", u["text"].replace("**", "")):
            words = WORD.findall(s)
            if words:
                sentences.append((u["start"], len(words), s.strip()))
    lens = [w for _, w, _ in sentences]
    prose = " ".join(u["text"] for u in units)
    nwords = len(WORD.findall(prose.replace("**", "")))
    if not lens:
        print("No prose found.")
        return

    print(f"# text_stats — {args.file}")
    print(f"language: {lang} · words: {nwords} · sentences: {len(lens)} · paragraphs/items: {len(units)}")
    mean, sd = statistics.mean(lens), statistics.pstdev(lens)
    band = sum(10 <= x <= 25 for x in lens) / len(lens)
    print(f"sentence length: mean {mean:.1f}, median {statistics.median(lens)}, stdev {sd:.1f}, "
          f"CV {sd / mean:.2f} (below ~0.45 reads uniform), in 10–25 words: {band:.0%}")
    plen = [len(WORD.findall(u["text"])) for u in units if u["kind"] == "para"]
    if len(plen) > 1:
        print(f"paragraph length (words): mean {statistics.mean(plen):.0f}, stdev {statistics.pstdev(plen):.0f}")
    short = [f"L{n}" for n, w, _ in sentences if w <= 3]
    print(f"fragments (≤3 words): {len(short)} {' '.join(short[:15])}")

    per_k = lambda c: c * 1000 / max(nwords, 1)
    marks = {"em dash —": prose.count("—"), "en dash –": prose.count("–"), "colon": prose.count(":"),
             "semicolon": prose.count(";"), "question": prose.count("?"), "exclamation": prose.count("!"),
             "ellipsis …": prose.count("…"), "parentheses": prose.count("("),
             "emoji": len(EMOJI.findall(raw)), "bold spans": raw.count("**") // 2}
    print("per 1000 words: " + ", ".join(f"{k} {per_k(v):.1f}" for k, v in marks.items()))
    bold_lead = [f"L{u['start']}" for u in units if u["text"].lstrip().startswith("**")]
    print(f"paragraphs/items opening with bold: {len(bold_lead)} {' '.join(bold_lead[:20])}")

    openers = defaultdict(list)
    for n, _, s in sentences:
        first = WORD.findall(s.lower())
        if first:
            openers[first[0]].append(n)
    rep = sorted(((k, v) for k, v in openers.items() if len(v) >= 3 and k != "code"), key=lambda kv: -len(kv[1]))
    print("\n## repeated sentence openers (≥3)")
    for k, v in rep[:15]:
        print(f"- «{k}» ×{len(v)}: " + " ".join(f"L{x}" for x in v))

    print("\n## watch words (fillers, stock words)")
    low = {n: t.lower() for n, t in raw_lines.items() if t}
    for w in WATCH[lang]:
        pat = re.compile(r"(?<![\w'ʼ])" + re.escape(w), re.UNICODE)
        hits = [n for n, t in low.items() for _ in pat.finditer(t)]
        if hits:
            print(f"- «{w}» ×{len(hits)}: " + " ".join(f"L{x}" for x in hits))

    print("\n## construction patterns")
    for name, rx in PATTERNS[lang].items():
        pat = re.compile(rx, re.IGNORECASE | re.UNICODE)
        hits = [(n, m.group(0)) for n, t in raw_lines.items() if t for m in pat.finditer(t)]
        if hits:
            print(f"- {name} ×{len(hits)}:")
            for n, g in hits[:12]:
                print(f"    L{n}: …{g[:70]}…")

    counts = Counter(w.lower() for w in WORD.findall(prose) if len(w) > 3 and w != "CODE")
    print("\n## most frequent words (length > 3) — look for fillers among them")
    print(", ".join(f"{w} {c}" for w, c in counts.most_common(30)))


if __name__ == "__main__":
    main()
