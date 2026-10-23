---
name: website-update
description: Maintain the content of Haruki Yokota's academic website (haruki-yokota.jp, Hugo + Blowfish). Use this for ANY change to what the site says — adding a paper, marking a preprint accepted, early access → published, adding a domestic workshop/研究会 talk, writing a News post, syncing the site with an updated CV or publication list, fixing a typo in a publication/award/education entry, or checking that a deploy went live. Trigger even when the user only pastes a DOI, an arXiv link, an IEICE program link, a citation string, or attaches a CV / 講演論文詳細 PDF and says "update the site".
---

# Website content updates

The site is small, but every fact lives in several files, and the citations have to be
exactly right. Most mistakes in past sessions came from three things: a fact updated in one
place but not another, a detail recalled or guessed instead of checked against a source,
and "done" claimed before the live site was checked. This workflow guards against each one.

Read `CLAUDE.md` first for the repo basics (file map, publication HTML format, git rules).
This skill adds the workflow and the lessons learned on top of it.

## Workflow

### 1. Check the current state first

```bash
git status --short && git log --oneline -5
```

Haruki edits files between sessions, and sometimes between turns (commits such as
`manual: Update content/_index.md`). Re-read any file you are about to edit, even if you
read it earlier in the conversation. If an on-disk change undoes something you fixed
earlier, don't silently put it back. Say what changed and cite the evidence for the correct
version, then fix it.

### 2. Gather the facts from sources, not from memory

Use the bundled lookup for anything with a DOI or arXiv ID:

```bash
python3 .claude/skills/website-update/scripts/lookup.py 10.1109/TSP.2026.3712068
python3 .claude/skills/website-update/scripts/lookup.py https://arxiv.org/abs/2609.36854
```

It queries Crossref / the arXiv API through `curl`. Python's `urllib` fails SSL
verification on this machine. It prints the title, authors, venue and status, plus a
site-formatted author and venue string.

Some sources can't be fetched. See `references/sources.md` for which ones and what to do
instead (IEEE Xplore and ken.ieice.org block automated access).

Check the details the user types, too, not just DOIs. For a recurring venue (信号処理シンポジウム,
SIP研究会, ICASSP, …), look up the official event page for its number, city and dates;
`references/sources.md` lists where. `check.py`'s numbering rule is only a sanity check;
the event page is the source. In a test run, the user's "第40回, 京都, 2026年11月" turned
out to be the 41st, in Hiroshima, Dec 2–4, and only a run that checked the event site
caught the city and date.

Compare the official title with what the user gave you. Titles change during peer review
(for example, "…on **Graph** Temporal Variation" gained a word). The user's own CV can be
wrong too. When official records and the user's document disagree, use the official
version on the site and tell the user their document differs.

When something can't be verified (a presentation date, a city, which of several papers
was accepted), ask. Collect all the open questions into one message, and state the
defaults you plan to use for everything else, so the user only answers what matters.
Never fill a gap with a plausible guess. In a past session, posts with guessed dates were
deleted.

### 3. Make the edits

- **Publications** → `references/publications.md`: entry template, tags, ordering, venue
  wording for each file, and how an entry changes from preprint to published.
- **News posts** → `references/posts.md`: front matter, how to pick the date, and wording.
- **Profile facts** (education, appointments, awards, grants, bio) →
  `references/profile-facts.md`: every file each fact lives in.

If a change sets a new convention (a new tag, a new section, a new layout override),
update `CLAUDE.md` in the same commit so later sessions pick it up.

### 4. Check locally

```bash
python3 .claude/skills/website-update/scripts/check.py
# optionally assert strings that must be gone:
python3 .claude/skills/website-update/scripts/check.py --absent "early access" --absent "Sept. 2024"
```

This builds with Hugo and checks:
- publication titles, tags and authors match between both lists
- tag rules and ordering within each year
- 信号処理シンポジウム numbering against the year
- known name misspellings
- award titles match publication titles
- home, About and Bio agree
- no post has a future date (Hugo would silently skip it)
- no list item uses an indented continuation line (these render as one run-on line)

Fix every ERROR. Read the WARNs: some are long-standing and intentional, so mention
them to the user instead of "fixing" them unasked.

### 5. Commit and push (only when asked)

Haruki usually says "commit & push". If they didn't, finish with the changes staged and
offer to push. Add files by name (never `git add -A`), write a commit message that says
*what changed and how it was verified*, and end it with the attribution trailer from the
current system reminder.

### 6. Check the live site

```bash
python3 .claude/skills/website-update/scripts/verify_live.py --wait \
  --expect "/::SIP2026-45" --expect "/publications/::SIP2026-45" \
  --absent "/::early access"
```

`--wait` finds the GitHub Actions run for `HEAD` and waits for it to finish. Each expected
string is then checked on the live page, after HTML entities are decoded, with retries
while the CDN cache catches up. Only report "live" after this passes.

### 7. Report back

Keep it short:
- what changed
- where each fact was verified
- any decision the user might want to change, with the one-word edit it would take
  (e.g., "群馬 vs 渋川")
- discrepancies you noticed but deliberately left alone

List sources as markdown links when you used the web.
