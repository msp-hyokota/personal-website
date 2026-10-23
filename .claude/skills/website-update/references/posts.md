# News posts

Files in `content/posts/` appear as the **News** list directly under the profile header
on the home page. Up to `showRecentItems` posts show there (5, set in
`config/_default/params.toml`); older posts stay reachable at `/posts/`. Posts are ordered
by their `date` front matter.

Only write posts the user asked for. They once deleted a batch of posts that had guessed
dates, plus a "Hello, World" placeholder. Treat News as announcements they explicitly want.

## Template

File name: `content/posts/<venue>-<year>-<topic>.md`, lowercase kebab-case, for example
`icassp-2027-submission-multifold-graph.md`.

```markdown
---
title: "Manuscript submitted to ICASSP 2027"
date: 2026-09-29
draft: false
summary: "We submitted \"Multivariate signal restoration via Multifold Graph Learning\" to ICASSP 2027; the preprint is on arXiv."
tags: ["publication", "preprint", "graph signal processing"]
---

We submitted our manuscript **"Multivariate signal restoration via Multifold
Graph Learning"** to IEEE ICASSP 2027. The preprint is available on arXiv.

Authors: H. Yokota, Y. Tanaka

- [arXiv preprint](https://arxiv.org/abs/2609.36854)
```

- `summary` appears on the News card: one sentence, with the paper title in escaped quotes.
- Voice: "Our paper…", "We submitted…", "I presented…" (first person, as Haruki).
- The body contains only facts from sources: the title, authors, citation and links.
  No claims about impact and no speculation.
- For Japanese titles, give the Japanese title in bold, followed by the official English
  title from the IEICE page in italics if you have it.

## Choosing the date — the event, not today

| Post type | Date |
|---|---|
| Submission + preprint | arXiv v1 submission date (from `lookup.py`) |
| Presentation at 研究会 / conference | the day of the talk (発表日時 on the IEICE page) |
| Acceptance | acceptance / early-access date, or today if the user just heard |
| Published in an issue | keep the original post and update it in place (see below) |

Hugo does not build posts dated in the future (`buildFuture` is off). A post dated even
one day ahead silently disappears. `check.py` flags this.

If the event date isn't in any source, ask. Don't estimate it from month-level data.

## When a status changes

Update the existing post rather than adding a second one: change the title
(e.g. "accepted" → "published"), the summary and the citation line. Keep the file name so
the URL stays stable. This is how the TSP post went from early access to published.

Tense matters: say "was presented" or "presented" only if the date has passed, and
"has been accepted to" when you only know it was accepted.

## Standard titles used so far

- `Paper published in IEEE Transactions on Signal Processing`
- `Presented at the IEICE SIP Workshop` (Haruki calls a 研究会 talk a workshop presentation, not a "technical committee meeting")
- `Manuscript submitted to ICASSP 2027`
