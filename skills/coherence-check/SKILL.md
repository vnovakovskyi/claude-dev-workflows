---
name: coherence-check
description: Check whether an article or draft holds together as one piece — one through-line from the promise in the title and intro to the ending — especially after AI drafting and human editing, which often tear the narrative. Builds a map of the argument (promise, through-line, what each section does), then finds broken promises, lost threads, detours, jumps without a bridge, wrong order, repeats, drift, an ending that misses the opening, and editing seams (terms that change mid-text, references to removed passages, announced counts that no longer match). Returns the map and a table of findings with structural fixes; never edits the text without permission. Use when the user asks whether a text holds together, flows, stays on one thought, keeps its promise, or reads as a whole.
argument-hint: <file | PR URL or number | branch:path | pasted text> [draft: <earlier version — file, commit, or branch>]
allowed-tools: Read, Grep, Glob, WebFetch, Bash(git fetch:*), Bash(git show:*), Bash(git log:*), Bash(git diff:*), Bash(git ls-tree:*), Bash(gh pr view:*), Bash(gh pr diff:*)
---

# Coherence check

You are running the **Coherence check** skill.

Text to check, and an optional earlier draft:

`$ARGUMENTS`

## Purpose

When AI writes a draft and a person edits it, the sentences get better and the
whole gets worse: a paragraph is rewritten and no longer leads into the next one,
a term changes halfway through, a promise from the intro is never kept, the
ending answers a different question from the one the title asked.

Your job is to be the **structural editor**: read the text the way a reader does,
from the first line to the last, and check that it is **one piece** — that it
keeps one thought all the way through and delivers what it announced. You report;
the author decides.

This skill is about the **whole**. Wording and voice belong to `voice-check`,
facts to `fact-check`. Recommended order: fact-check → coherence-check →
voice-check — fix the structure before polishing sentences that may move or go.

## Hard rules

- **Report only.** Do not edit the text. After the report, offer to apply the
  fixes; apply them only when the user says so, and only the ones they pick.
- **Structural fixes, not rewrites.** Suggest what to move, cut, merge, split,
  or bridge. A bridge is one short sentence, in the text's language; don't
  rewrite paragraphs.
- **Never write missing content.** If a promised topic is not in the text, the
  options are to drop the promise or for the author to write it. Don't draft the
  missing section, and don't invent experiences or conclusions.
- **Judge against the author's promise,** not against the article you would
  have written. A different structure that works is not a finding.
- **Keep the facts.** A move or a bridge must not change what a passage claims.
- **Respect deliberate structure:** an aside the author marks as an aside, a
  teaser for a next article, a list that is meant to be skimmed.

## Step 1 — Get the text and, if there is one, the earlier draft

Where the text comes from:

- **File path** → read the **whole** file.
- **PR URL or number** → `gh pr view <pr> --json url,headRefName,files`; if the
  repo is local, `git fetch` and `git show origin/<branch>:<path>` (never check
  out); otherwise `gh pr diff <pr>`.
- **`branch:path`** → `git show <branch>:<path>`.
- **Pasted text** → use it.
- **Empty** → the draft most recently discussed in this conversation; if
  ambiguous, ask one short question.

**The earlier draft** is what makes seams visible. Take it from, in this order:

1. `draft:` in the arguments (a file, a commit, or a branch);
2. the file's git history — `git log --follow --oneline -- <path>`, then
   `git diff <old> <new> -- <path>` against the first AI-written version;
3. the PR's commits, when the text lives in a PR;
4. for a translation, the original — its structure should match.

If there is no earlier version (an untracked file, pasted text), say so in the
report and find seams by reading alone.

## Step 2 — Measure the skeleton

Run the skeleton script from this skill's directory:

```bash
python3 <skill-dir>/scripts/skeleton.py <file> [--lang en|uk|ru]
```

For pasted text, write it to a temp file first. It prints the promise (title,
excerpt), every heading, and the first sentence of every paragraph and list item
with line numbers, then two lists to verify: **back-references** ("as I said
above", "нижче", "далее") and **announced counts** ("three points:", "два
рішення"). Read the skeleton on its own first: **headings and first sentences
should tell the story by themselves.** Where they don't, the text has a gap.

## Step 3 — Build the map (before judging anything)

- **Promise:** what the title, the excerpt or subtitle, and the intro tell the
  reader they will get. List it item by item; note the question the text
  implicitly promises to answer.
- **Through-line:** the one thought the text carries from start to finish, in
  one sentence. If you cannot write that sentence, that is the first finding.
- **Sections:** for each section, its job for the through-line in one line, and
  how it connects to the previous one (bridge / none).
- **Threads:** everything set up to be picked up later — a question, a named
  item in a list, a term, a "we'll see later", a personal frame in the intro —
  and whether it is picked up.
- **Ending:** what it says, and whether it answers the promise.

## Step 4 — Look for breaks

1. **Broken promise** — announced in the title, excerpt, or intro and never
   delivered, or delivered as something else.
2. **Lost thread** — a question, term, or setup introduced and dropped; a
   personal frame in the intro that never comes back.
3. **Detour** — a passage that doesn't serve the through-line, or takes more
   room than its role deserves.
4. **Jump** — a paragraph or section that starts a new idea with no bridge; the
   reader doesn't know why they are here.
5. **Order** — something used before it is explained; the literal answer to the
   title buried in the middle; sections that would read better swapped.
6. **Repeat** — the same point made twice in different places, often after
   edits: a human adds a sentence the draft already had elsewhere.
7. **Drift** — the stance, the claim, or the framing shifts between sections;
   the excerpt promises one thing and the body delivers its neighbour.
8. **Ending** — a new idea in the conclusion, a summary that doesn't match the
   body, an ending on a side topic, or no ending at all.
9. **Seams** — where an edit doesn't meet its neighbours:
   - a term that changes mid-text (the same thing called two names);
   - a back-reference to something removed or moved;
   - an **announced count that no longer matches** ("two decisions" followed by
     four points) — edits add items without updating the announcement;
   - a paragraph answering a question that is no longer asked;
   - a sudden shift of person (I / we / you), register, or tense.
   With a draft, check the boundaries of every edited region.
10. **Proportion** — a side topic gets more room than the main one.

Two reader tests, for every section:

- **Why am I here?** Can you say in one sentence what this section gives the
  reader for the through-line? If not, it is a detour or it is missing a bridge.
- **Where was I?** Read the first sentence of the section right after the last
  sentence of the previous one. Does the reader follow, or fall into a gap?

## Step 5 — Sort the findings

- **Breaks the whole** — the reader loses the thread, a promise is broken, the
  ending misses the opening, the structure hides the main answer.
- **Joints and seams** — local: a missing bridge, a small repeat, a term
  change, an announced count that is off.

Also collect **Holds well — keep:** 2–4 structural moves that work (a callback
from the ending to the intro, a thread picked up at the right moment), so fixes
don't break them.

## Step 6 — Report

Write the report in the **language of the conversation** (translate the headings
below). Quote fragments **verbatim, in the text's language**; bridges and
reworded announcements are **in the text's language** too.

Table hygiene: one row per finding, no line breaks inside cells, `|` inside a
cell escaped as `\|`, locations as `L<line>`.

````md
## Coherence check: <title or file name>

Words: N · Sections: N · Earlier draft: <what was compared | none — seams found by reading>

**Verdict:** <one sentence: does it read as one piece, and what breaks it most>

### Map

- **Promise:** <item by item: title, excerpt, intro>
- **Through-line:** <one sentence>
- **Ending:** <what it says> → answers the promise: <yes / partly / no>

| # | Section | Its job for the through-line | Link to the previous one |
|---|---|---|---|

### Breaks the whole

| # | Where | What breaks | Why the reader loses the thread | Fix |
|---|---|---|---|---|

### Joints and seams

| # | Where | What breaks | Why | Fix |
|---|---|---|---|---|

### Holds well — keep

- <structural move> — <why it works>

### Next step

"Apply the fixes? All, by number, or only 'Breaks the whole'. Fixes marked ✍️ need your content — I'll leave a placeholder there."
````

Mark with ✍️ every fix that needs content only the author can give (a missing
section, a personal ending).

## Before you send — self-check

- [ ] The whole text was read in order, not only the skeleton.
- [ ] The promise was taken from the title, excerpt, and intro — all three.
- [ ] The through-line fits in one sentence, or its absence is finding #1.
- [ ] Every back-reference and announced count from the script was checked.
- [ ] The earlier draft was used when it exists, or its absence is stated.
- [ ] No fix rewrites a paragraph, changes a fact, or writes missing content.
- [ ] Wording and style issues were left to voice-check.
- [ ] The text itself was not edited.

## Completion criteria

The coherence check is complete only when:

- The report opens with the map: promise, through-line, ending, sections.
- Findings are split into "Breaks the whole" and "Joints and seams".
- Every fix is concrete: what moves where, what goes, or the bridge sentence.
- Fixes that need the author's content are marked ✍️.
- The user is offered a next step, and the text is untouched.
