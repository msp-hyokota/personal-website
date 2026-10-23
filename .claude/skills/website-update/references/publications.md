# Publications

Two lists must stay in step: `content/_index.md` (the home page, under `### YYYY`) and
`content/publications/_index.md` (under `## YYYY`). **Titles, tags, authors and order are
identical in both. Venue wording differs on purpose:**

| File | Venue style | Example |
|---|---|---|
| `content/_index.md` | short | `ICASSP 2025, Hyderabad, India, pp. 1–5` |
| `content/publications/_index.md` | full conference name | `ICASSP 2025 — IEEE International Conference on Acoustics, Speech and Signal Processing, Hyderabad, India, pp. 1–5` |

Journal, preprint and Japanese-language venues are written the same way in both files.

## Entry template

```html
<div class="pub-entry">
<div class="pub-title">Title <span class="pub-tag pub-tag-journal">Journal</span></div>
<div class="pub-authors">H. Yokota, K. Yamada, Y. Tanaka, A. Ortega</div>
<div class="pub-venue">IEEE Transactions on Signal Processing, vol. 74, pp. 3017–3032, 2026</div>
<div class="pub-links"><a href="https://doi.org/…">DOI</a><a href="https://arxiv.org/abs/…">arXiv</a></div>
</div>
```

- Put one blank line between entries.
- Adjacent `<a>` tags need no separator; the CSS spaces them.
- Link labels are `DOI`, `IEEE Xplore` or `arXiv`. When both exist, list the published
  version first.
- Page ranges use an en dash: `pp. 51–56`, not `51-56`.
- Omit `pub-links` entirely when there are no links (most domestic entries).

## Tags

| Class | Label | Use for |
|---|---|---|
| `pub-tag-journal` | Journal | journal / Transactions papers, including early access |
| `pub-tag-intl` | International | international **conference** papers |
| `pub-tag-domestic` | Domestic | Japanese conferences, 研究会, symposia |
| `pub-tag-preprint` | Preprint | arXiv preprints that are submitted but not yet accepted, even if the user calls it "an ICASSP paper" |

International and Domestic are for conference papers only (Haruki set this rule). A
submitted conference paper stays `Preprint` until it is accepted.

## Ordering inside a year

Order by group: **journal → international → preprint → domestic**. Within a group, put
the newest first. A new preprint goes at the top of the preprints, and a new domestic talk
at the top of the domestic entries.

## Status lifecycle — what to change at each step

| Event | Tag | Venue line | Links | Also |
|---|---|---|---|---|
| Posted to arXiv, submitted | Preprint | `Pre-print on arXiv (Submitted to ICASSP 2027)` | arXiv | — |
| Journal accepted, DOI assigned but not yet resolving | Journal | `APSIPA Transactions on Signal and Information Processing (accepted, to appear)` | arXiv only; add the DOI once doi.org resolves it | Haruki's rule: keep the DOI out until it's live. Emerald (ATSIP) posts "EarlyCite", its early-access stage, after proofing. |
| Journal accepted, early access | Journal | `IEEE Transactions on Signal Processing (early access)` | DOI, arXiv | run lookup: the title may have changed |
| Journal issue assigned | Journal | `…, vol. 74, pp. 3017–3032, 2026` | DOI, arXiv | update the News post that mentioned it |
| Conference accepted | International | e.g. `EMBC 2026, Toronto, Canada, July 2026` | arXiv / Xplore | move out of the preprint group |

Whenever the status changes, re-run `scripts/lookup.py` and compare the title word by
word. Also fix the title everywhere it appears: both lists, any News post, and any award
line that cites it.

## Domestic venue formats

- IEICE 研究会:
  `電子情報通信学会信号処理研究会 (IEICE Technical Report), vol. 126, no. 157, SIP2026-45, pp. 51–56, 群馬, 2026年8月`
- 信号処理シンポジウム: `第40回信号処理シンポジウム, 茨城, 2025年11月`.
  The number is **year − 1985** (36th = 2021, 37th = 2022, 38th = 2023, 40th = 2025).
  `check.py` enforces this; the 2022 entry once had the wrong number. The formula only
  catches a wrong number. For the city and month of a new entry, check the official site
  listed in `sources.md`.
- Location: recent entries use the prefecture (茨城, 沖縄, 群馬); older ones use the city
  (吹田, 京都, 新潟). For new entries, use the prefecture and tell the user.
- If the program only gives a building name (e.g. 森秋旅館), search for its address to
  find the prefecture.

## Names

As written on the site (the full given names are confirmed only for Haruki Yokota,
Yuichi Tanaka, Koki Yamada and Antonio Ortega, via arXiv and Crossref):

| English (initials) | Japanese |
|---|---|
| H. Yokota | 横田陽樹 / 横田 陽樹 |
| Y. Tanaka | 田中雄一 / 田中 雄一 |
| H. Higashi | 東広志 / 東 広志 — **広**, never 宏 |
| G. Cheung | (Gene Cheung, written in Latin script in Japanese entries too) |
| K. Yamada | 山田宏樹 |
| J. Hara | 原惇也 / 原 惇也 |
| A. Ortega | — |
| M. Yoshino | 吉野将裕 |
| — | 内海健介 |

English entries use initials. Japanese spacing varies between entries; follow the source
the user gave. Some older entries write "Gene Cheung" in full. This inconsistency is
long-standing, so mention it rather than "fixing" it unasked. For an unfamiliar
co-author, take the romanization from the IEICE 講演論文詳細 page or the paper itself.
Never transliterate kanji yourself.
