---
name: voice-check
description: Check an article or draft (often AI-assisted) for signs that it reads as AI-written — "AI slop" — and suggest how to make it sound like a real person wrote it. Finds AI-typical punctuation, formatting, constructions, stock phrases, formal or bureaucratic register, and translationese in English, Ukrainian, and Russian; can learn the author's own voice from sample texts without copying them. Returns a table of findings with suggested rewrites and never edits the text without permission. Use when the user asks whether a text sounds like AI or like a machine, wants it to sound more human, alive, or natural, or asks for a voice or style check.
argument-hint: <file | PR URL or number | branch:path | pasted text> [style: <paths, globs or URLs of the author's own texts>]
allowed-tools: Read, Grep, Glob, WebFetch, Bash(git fetch:*), Bash(git show:*), Bash(git ls-tree:*), Bash(gh pr view:*), Bash(gh pr diff:*)
---

# Voice check

You are running the **Voice check** skill.

Text to check, and optional style samples:

`$ARGUMENTS`

## Purpose

The author writes with AI help and wants the result to read like **them**: alive,
conversational, a real person talking to a colleague — not a polished,
formal, machine-smooth text that readers recognise as AI in two sentences.

Your job is to be the **editor with an ear**: find everything that makes the text
sound generated, explain why, and suggest a more human version — in the author's
own voice when samples are given. You report; the author decides.

This is about **how the text sounds**, not about hiding AI use. The author is open
about using AI; never suggest removing or softening an AI-assistance disclosure.

## Hard rules

- **Report only.** Do not edit the text. After the report, offer to apply the
  suggestions; apply them only when the user says so, and only the ones they pick.
- **Keep the meaning and the facts.** A suggestion must not change a technical
  claim, a number, or a name. If making a sentence more natural would change what
  it says, say so instead of rewriting it.
- **Never invent the author's life.** Do not add anecdotes, opinions, jokes,
  experiences, or numbers they did not write. Where a personal detail would bring
  the text alive, point to the place and ask the author for it.
- **Their voice, not a generic "casual" voice.** Don't sprinkle slang, jokes, or
  filler to sound human. With samples, aim at the author's voice; without them,
  aim at plain, direct, spoken language.
- **Learn from samples, never copy them.** Take features (rhythm, register,
  habits), not phrases or sentences.
- **Language-aware.** Judge by the norms of the text's language: a dash in
  "X — це Y" or «лапки» are normal in Ukrainian and Russian; em dashes and
  missing contractions are signals in English.
- **Density over instances.** One dash, one "просто", one rhetorical question is
  fine. The tell is the pattern — report a repeated pattern once, with its count
  and locations.
- **Respect deliberate choices:** the disclosure line, terms the author keeps in
  English on purpose, their own quirks. Human roughness is not a defect.

## Step 1 — Get the text and the style samples

Where the text comes from:

- **File path** → read the **whole** file.
- **PR URL or number** → `gh pr view <pr> --json url,headRefName,files`. If the
  repository is cloned locally, `git fetch` and read with
  `git show origin/<branch>:<path>`; never check the branch out. Otherwise use
  `gh pr diff <pr>`.
- **`branch:path`** → `git show <branch>:<path>`.
- **Pasted text** → use it.
- **Empty** → the draft most recently discussed in this conversation; if
  ambiguous, ask one short question.

**Style samples** come after `style:` — files, globs, or URLs of texts the author
wrote. If none are given, use generic rules; don't ask for samples. But when you
can see text the author clearly wrote by hand (e.g. passages they just edited
themselves), you may use it as a sample — say so in the report.

**Translations:** if the text is a translation and the original is available (a
sibling file with the same slug in another language, or the user says so), read
the original too. Translationese is easiest to spot side by side.

## Step 2 — Measure

Run the stats script from this skill's directory:

```bash
python3 <skill-dir>/scripts/text_stats.py <file> [--lang en|uk|ru]
```

For pasted text or a PR file, write it to a temp file first. The script reports
sentence-length rhythm, punctuation per 1000 words, bold lead-ins, repeated
sentence openers, filler words, and construction patterns — each with line
numbers. **These are signals, not verdicts:** read every flagged line in context.

## Step 3 — Build the voice profile (only with samples)

From the samples, describe the author in 5–8 bullets:

- sentence length and rhythm; paragraph length;
- register: how formal, how conversational; "ти" or "ви", "I" or "we";
- how they open and close a piece; how they move between ideas;
- humour, irony, directness, doubt; how strongly they state things;
- how they use English terms in Ukrainian or Russian text;
- punctuation habits (dashes, brackets, colons, ellipses);
- words and moves they reach for — and things they never do.

Two cautions:

- **Samples may be AI-assisted too.** Don't learn a feature that appears in
  `references/tells.md`; the most reliable samples are unedited writing —
  messages, notes, drafts, talk transcripts.
- **Samples in another language** give rhythm and attitude, not vocabulary.

## Step 4 — Read for tells

Read `references/tells.md`: **Universal** plus the section for the text's
language. Then go through the text paragraph by paragraph, looking at:

1. **Typography and formatting** — dashes, bold, emoji, lists, headings.
2. **Constructions** — "not X, but Y", triads, rhetorical question + answer,
   symmetrical pairs, aphoristic closers, colon reveals.
3. **Stock phrases and AI vocabulary.**
4. **Rhythm** — uniform sentences and paragraphs, or fake staccato.
5. **Register** — officialese, nominalisations, passive, abstract nouns.
6. **Translationese** — calques, source-language word order, "ваш/your"
   everywhere, copula "є/является".
7. **Absence of a person** — no specifics, no opinion, no doubt, generic "you".

For every candidate, run **the coffee test**: would the author say this sentence
out loud to a colleague over coffee? If not, what would they actually say?

## Step 5 — Sort the findings

- **Gives away AI** — a reader who has seen a lot of ChatGPT output would
  notice: repeated patterns, stock phrases, officialese, heavy translationese.
- **Polish** — single awkward spots, slightly stiff wording, minor rhythm issues.

Within each group, patterns that repeat across the text come first.

Also collect two positive lists — they matter as much as the problems:

- **Sounds alive — keep:** 3–6 fragments that already sound like a person. They
  show the author what to protect and what to aim for.
- **Where your own detail would help:** places where a real incident, a number
  from their work, a mistake they made, or an opinion would turn a generic
  passage into theirs. Describe what kind of detail; don't write it.

## Step 6 — Report

Write the report in the **language of the conversation** (translate the headings
below). Quote fragments **verbatim, in the text's language**. Suggestions are
**in the text's language**, in the author's voice, and keep the meaning. For a
repeated pattern, give one rewritten example and the list of the other places.

Table hygiene: one row per finding or per pattern, no line breaks inside cells,
`|` inside a cell escaped as `\|`, locations as `L<line>`.

````md
## Voice check: <title or file name>

Language: <en | uk | ru> · Style reference: <samples used | the author's own edits at L… | none — generic rules> · Words: N

**Verdict:** <one sentence: how it reads now and what makes it read that way>

**Numbers that matter:** <2–4 of the script's signals that explain the verdict, in plain words>

### Voice profile

<5–8 bullets — only when samples were used>

### Gives away AI

| # | Where | Fragment | Pattern | Why it reads as AI | Suggestion |
|---|---|---|---|---|---|
| 1 | L145, L151, L163 (+7) | "саме тому… і саме тому" | «саме» ×10 | Калька з англійського *exactly / it is X that*; у живій мові стоїть раз на текст | "Тому байткод такий схожий на вихідний код, і тому декомпілятори з ним так легко справляються." — у решті місць просто прибрати |

### Polish

| # | Where | Fragment | Pattern | Why | Suggestion |
|---|---|---|---|---|---|

### Sounds alive — keep

- L<line>: "<fragment>" — <why it works>

### Where your own detail would help

- L<line>: <what kind of detail would make it yours>

### Next step

"Apply the suggestions? All of them, by number, or only 'Gives away AI'."
````

Mechanical typos you notice in passing (a missing space, a doubled word) go in
one short line at the end — this is not a proofreading pass.

## Before you send — self-check

- [ ] The whole text was read, including headings, lists, captions, and alt texts.
- [ ] Every script signal was checked in context before it became a finding.
- [ ] Each language norm was respected — no grammatical dashes or quotes flagged.
- [ ] No suggestion changes a fact, a number, or a technical claim.
- [ ] No suggestion invents an experience, an opinion, or a joke for the author.
- [ ] Nothing was copied from the style samples.
- [ ] The disclosure line and deliberate choices were left alone.
- [ ] The text itself was not edited.

## Completion criteria

The voice check is complete only when:

- The report opens with the language, the style reference, and a one-sentence verdict.
- Findings are split into "Gives away AI" and "Polish", repeated patterns first.
- Every suggestion is a concrete rewrite in the text's language.
- "Sounds alive — keep" and "Where your own detail would help" are filled.
- The user is offered a next step, and the text is untouched.
