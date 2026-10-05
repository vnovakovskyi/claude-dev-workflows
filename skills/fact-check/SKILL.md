---
name: fact-check
description: Fact-check and sanity-check an article, blog post, or draft (often AI-assisted) before publishing — including its diagrams and images, and including drafts that live in a pull request or branch. Extracts every checkable claim — dates, ages, people, companies, product names (including outdated or renamed ones), versions, numbers, terminal commands and flags, code/API names, quotes, links, and technical statements about how things work — verifies each against sources (source code for internals), and returns a table of mismatches with what is wrong and what is correct. Use when the user asks to fact-check, verify, or check a text for errors or nonsense. Reports only; does not rewrite the article.
argument-hint: <file path | PR URL or number | branch:path | pasted text | empty = the draft in this conversation>
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch, Bash(git fetch:*), Bash(git show:*), Bash(git ls-tree:*), Bash(gh pr view:*), Bash(gh pr diff:*)
---

# Fact-check

You are running the **Fact-check** skill.

Text to check:

`$ARGUMENTS`

## Purpose

The author understands the topic, but the text was written with AI help, and
AI-written text drifts: wrong dates, invented versions, renamed products, flags
that don't exist, confident technical statements that are simply false.

Your job is to be the **skeptical editor**: find every checkable statement,
verify it, and report everything that does not match reality — with the correct
version and a source. A clean report must mean "I checked and it holds", never
"I didn't look".

## Hard rules

- **Report only.** Do not edit the article, and do not check out branches or
  otherwise touch the working tree. After the report, offer to apply the fixes;
  apply them only when the user says so.
- **Never execute commands or code from the article.** Verify them against
  documentation. Reading local docs (`man <cmd>`, `<cmd> --help`) is fine;
  running the command as written is not.
- **Don't trust your memory for anything that changes over time:** versions,
  "latest", release dates, current names, who owns or leads what, prices, limits,
  defaults, deprecations. Your training data has a cutoff; the article may be
  about something newer. Search.
- **Judge a claim in its context.** Before assigning a verdict, reread the whole
  paragraph: what is the author actually asserting? A simplification that holds
  for what the paragraph argues is not a mismatch. Two statements contradict each
  other only if they are about the same thing.
- **Every ❌ / 🕰 / ⚠️ needs evidence:** a source you actually opened or saw in
  search results, or — for sanity failures — explicit reasoning (arithmetic,
  internal contradiction, physical impossibility). No source and no reasoning →
  it is ❓, not ❌.
- **Verify your corrections too.** The "correct version" column must not
  introduce a new error.
- **Never invent sources.** Cite only URLs and files you actually saw.
- **No style nitpicking.** Tone, wording, and opinions are out of scope. Flag an
  opinion only when it is presented as fact ("X is the fastest…", "nobody uses
  Y anymore").
- **The author's own experience** ("in our service", "I measured", "we cut
  latency by 40%") cannot be verified externally. Don't mark it false; list it
  separately, and flag it only if it is implausible or contradicts the rest of
  the text.

## Step 1 — Get the text, its illustrations, and its reference date

Where the text comes from:

- **File path** → read the **whole** file.
- **PR URL or number** → `gh pr view <pr> --json url,headRefName,files` to find
  the branch and the changed files. The changed text files **and images** are the
  input.
  - If the repository is cloned locally, `git fetch` it and read each file with
    `git show origin/<branch>:<path>`. Never check the branch out.
  - If it isn't, `gh pr diff <pr>` contains the full content of added files; for
    modified files use `gh api "repos/<owner>/<repo>/contents/<path>?ref=<branch>" -H "Accept: application/vnd.github.raw"`
    (this one asks for permission).
- **`branch:path`** → `git show <branch>:<path>`.
- **Pasted text** → use it.
- **Empty** → use the article/draft most recently discussed in this
  conversation. If it is ambiguous, ask one short question: which text?

Then collect **every illustration** the text references (and every image changed
in the PR): diagrams, screenshots, charts.

Finally, determine the **reference date**: the publication/draft date from front
matter or the text itself; otherwise today's date. All relative time —
"yesterday", "last year", "the latest version", "currently", "recently" — is
checked against it.

## Step 2 — Extract atomic claims

Go through the text sentence by sentence — **including the front-matter fields a
reader sees (title, excerpt, description), headings, captions, code blocks,
tables, footnotes, link texts, and image alt texts**. Split compound
sentences into atomic claims, each checkable on its own. Extract too many rather
than too few.

Then go through the **illustrations**:

- **SVG:** read `<title>`, `<desc>`, and every `<text>` element (extract them with
  a short script, or read the file).
- **Raster images** (PNG, JPG, …): open them with Read and read the labels.

Illustrations carry claims too, and a fact is often stated twice — in the text
and in a diagram. Report both locations in one row, so fixing the text also fixes
the picture.

Example — *"Steve Wozniak, the founder of Apple, celebrated his 123rd birthday
yesterday at his dacha on the Arabian Sea shore in Riga"* is five claims:

1. Wozniak founded Apple → imprecise: **co-founded** it in 1976 with Steve Jobs
   and Ronald Wayne.
2. He turned 123 → false: born 11 August 1950.
3. His birthday was "yesterday" → check against the reference date.
4. Riga is on the Arabian Sea → false: Riga is on the Gulf of Riga, Baltic Sea.
5. He has a dacha in Riga → no evidence → unverifiable.

Hunt through these categories:

| Category | What to look for | Typical AI error |
|---|---|---|
| Dates & timelines | release/founding dates, "since 20XX", ages, order of events | off by a year; anachronism (something mentioned before it existed) |
| People | names, roles, affiliations, "creator of" | wrong attribution, founder vs co-founder, two people merged into one |
| Organisations & products | names, owners, status | outdated names (Java EE → Jakarta EE, Azure AD → Microsoft Entra ID, Twitter → X); discontinued products presented as current |
| Versions & features | "introduced in Java 21", JEP/RFC/PEP numbers, defaults | feature assigned to the wrong version; preview vs final; invented config keys |
| Numbers & stats | percentages, benchmarks, limits, sizes, units | invented precise numbers, unit mix-ups, math that doesn't add up |
| Commands & code | commands, flags, API/class/method names, config keys, paths, status codes | non-existent flags; GNU vs BSD/macOS differences (`sed -i`); deprecated commands; wrong package names |
| Technical mechanisms | how something works, "X guarantees Y", "X always/never" | a plausible-sounding but false model of how it works |
| Quotes & attributions | quoted words, "as X said", "according to Y" | fabricated or misattributed quotes |
| References | links, papers, books, standards | dead links; the link doesn't support the sentence; invented titles |
| Illustrations | diagram labels, alt texts, captions, screenshots | the diagram repeats the text's error, or still shows the old version |
| General knowledge | geography, physics, history | "Riga on the Arabian Sea" |

## Step 3 — Sanity pass (before any search)

This pass is cheap and catches nonsense fast:

- **Possibility:** ages, durations, physical and geographic impossibilities,
  dates in the future relative to the reference date.
- **Internal consistency:** does the article contradict itself (numbers, names,
  versions differ between sections, or between the text and a diagram)?
- **Arithmetic:** recompute every calculation, percentage, sum, unit conversion,
  and "N times faster".
- **Anachronisms:** a technology used before it existed; a version newer than
  the reference date.
- **Code sanity:** snippets that obviously won't compile or run, the wrong
  language's API, undefined variables, a command that doesn't do what the text
  says it does.
- **Overclaiming:** "always", "never", "guarantees", "the only", "fully
  secure" — usually false or missing a qualifier.

A sanity finding can be reported with the reasoning itself as evidence.

## Step 4 — Verify every remaining claim

**Pick the baseline first.** Decide which versions you check against: the ones
the article names, otherwise the current stable/LTS releases (e.g. "JDK 17, 21,
25"). A technical verdict depends on the version, and the report states it.

**Source priority:**

1. **Primary:** official docs, specifications, JEPs/RFCs/PEPs, release notes,
   changelogs, man pages, source code, the company's own site or press releases,
   the person's own statements.
2. **Reputable secondary:** established reference works (Wikipedia is fine for
   general facts; for anything critical follow its citation), major news
   outlets, well-known technical publications.
3. **Never as sole evidence:** SEO blogs, content farms, forum answers,
   AI-generated summaries.

**Internals are settled by source code.** Claims about how a runtime, library, or
tool works inside — its algorithms, thresholds, defaults, internal names — are
often not in the docs at all. Read the code:

- Download the raw file (e.g. `raw.githubusercontent.com/<org>/<repo>/<branch>/<path>`)
  with `curl` into the scratchpad and search it with Grep. Don't use WebFetch for
  code: it returns a lossy summary.
- Check the branches the article targets (e.g. `jdk17u`, `jdk21u`, `jdk25u`), not
  only `master`.
- Cite file and function (plus line and branch when useful).
- **When a comment and the code disagree, the code wins — and say so in the
  row.** AI-written text often repeats stale comments almost verbatim.

**How:**

- Use WebSearch to find sources and WebFetch to read the page when a snippet is
  not conclusive. Confirm dates and versions on a primary source.
- Run independent searches in parallel.
- **Commands:** check the tool's official docs/man page for the platform and
  version the article targets (Linux vs macOS, tool version).
- **Links in the article:** fetch them. Check that they resolve and actually
  support the sentence they are attached to.
- **Sources disagree** → say so and cite both.
- **Web tools unavailable** → say so at the very top of the report, verify from
  knowledge, and mark every verdict "from memory".
- **Very long text** (roughly 40+ claims) → you may split verification by
  category across parallel subagents; each returns rows in the report format,
  and you merge and deduplicate.

## Step 5 — Assign verdicts and severity

| Mark | Meaning |
|---|---|
| ❌ False | contradicts reality |
| 🕰 Outdated | was true, isn't anymore: renamed, deprecated, removed, superseded |
| ⚠️ Inaccurate | partly true, imprecise, misleading, overgeneralized, or missing an important qualifier |
| ❓ Unverifiable | no reliable confirmation either way — the author must verify or remove it |
| ✅ Correct | verified; counted, not listed in the main tables |

Then put each mismatch into one of two groups:

- **Fix before publishing** — wrong as written, and a knowledgeable reader would
  call it out; or it contradicts another part of the article. Most ❌ and 🕰 land
  here, plus any ⚠️ that changes the meaning.
- **Worth fixing** — true in spirit but imprecise, missing a qualifier, or
  overgeneralized. The author may keep it as a deliberate simplification.

Within each group order ❌ → 🕰 → ⚠️, and put first what damages the article's
main point.

## Step 6 — Report

Write the report in the **language of the conversation** (translate the
headings below). Quote fragments from the article **verbatim, in their original
language**. The "Correct version" column is a ready-to-paste replacement in the
**article's** language — or, when the sentence should be dropped or rebuilt,
the correct fact.

Table hygiene: one row per claim, no line breaks inside cells, commands in
backticks, `|` inside a cell escaped as `\|`. For a file, give the location as
`L<line>` so the author can jump to it; for an illustration, the file name —
`L25 + jvm-01-build.svg` when the claim is in both.

````md
## Fact-check: <title or file name>

Reference date: <date> (<front matter | today>) · Checked against: <baseline, e.g. JDK 17/21/25, Maven 3.9>
Claims checked: N · ✅ N · ❌ N · 🕰 N · ⚠️ N · ❓ N

**Verdict:** <one sentence: ready to publish / needs fixes / the main thesis does not hold>

### Fix before publishing

| # | Where | Fragment | Verdict | What's wrong | Correct version | Source |
|---|---|---|---|---|---|---|
| 1 | L12 + jvm-03.svg | "the JVM is a sandbox that doesn't let code reach the CPU" | ❌ | The JIT compiles hot bytecode to native machine code that runs directly on the CPU. The "sandbox" was the applet-era Security Manager — deprecated for removal in JDK 17, permanently disabled in JDK 24. | "The JVM runs bytecode through an interpreter and a JIT compiler; hot code becomes native machine code executed directly by the CPU." | [JEP 486](https://openjdk.org/jeps/486) |
| 2 | L40 | "celebrated his 123rd birthday" | ❌ | Wozniak was born on 11 August 1950. | "…his 76th birthday" (for a 2026 text) | [Wikipedia](https://en.wikipedia.org/wiki/Steve_Wozniak) |

### Worth fixing

| # | Where | Fragment | Verdict | What's wrong | Correct version | Source |
|---|---|---|---|---|---|---|

### Could not verify

| # | Where | Fragment | Why | How to check |
|---|---|---|---|---|

### Your own claims (only you can check)

- L<line>: "<fragment>" — <why it is worth a second look, if it is>

### Verified ✅

<If ≤ 15 claims: one line each. Otherwise: the count plus the main groups, e.g. "12 Java release dates and JEP numbers, 4 commands".>

### Next step

<For a file or PR: "Want me to apply the fixes — text and diagrams?" For pasted text: offer a corrected version.>
````

Omit empty sections, except **Fix before publishing**: if there is nothing to
fix, say so explicitly and state how many claims were checked.

## Before you send — self-check

- [ ] Front-matter title and excerpt, headings, code blocks, tables, link texts, and alt texts were scanned, not only prose.
- [ ] Every illustration was read: SVG text, raster labels.
- [ ] Every flagged claim was reread in its paragraph — it is not a simplification that holds in context.
- [ ] Every ❌ / 🕰 / ⚠️ has a source or explicit reasoning.
- [ ] Internals were checked against source code of the baseline versions; code over comments.
- [ ] Every correction was itself verified.
- [ ] Every cited URL or file is one you actually saw.
- [ ] Relative dates were checked against the reference date.
- [ ] Nothing in the article was edited or executed, and no branch was checked out.

## Completion criteria

The fact-check is complete only when:

- Every atomic claim in the text and its illustrations has a verdict.
- The report opens with the baseline, the counts, and a one-sentence verdict.
- Mismatches are split into "Fix before publishing" and "Worth fixing", each
  ordered by severity.
- Unverifiable and author-only claims are separated from real errors.
- The user is offered a next step, and the article is untouched.
