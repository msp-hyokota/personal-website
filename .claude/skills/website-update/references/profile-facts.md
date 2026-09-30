# Where each profile fact lives

When a fact changes, update **every** file in its row. `check.py` compares the home page
with the About page, and the Bio award year with the home page.

| Fact | `content/_index.md` (home) | `content/about/_index.md` | `content/biography/_index.md` | Other |
|---|---|---|---|---|
| About paragraph | `## About` | intro paragraph | prose | — |
| Research interests | `**Research Interests**` list | `## Research interests` | "research interests are in…" | — |
| Education | `## Education` | `## Education` | degrees + years in prose | — |
| Appointments | `## Appointment` | `## Personal Appointment` | — | — |
| Awards | `## Awards` | `## Awards` | "received the … Award in YYYY" | — |
| Grants | `## Grants and Funding` | `## Grant and Funding` | "supported by JSPS" | — |
| Contact | `## Contact` | `## Contact` | — | — |
| Publications | `## Publications` | — | — | `content/publications/_index.md` |
| Paper titles | pub entries + award lines | award lines | — | News posts that name the paper |

The heading names differ between home and About; that's long-standing and fine.

## Syncing from a CV or publication-list PDF

Go through the PDF section by section and compare each fact against every row above.
Past sessions found these kinds of drift:

- a missing entry (the Ph.D. candidacy wasn't on the site)
- a wrong end date (lectureship "Sept. 2024" should have been "March 2025")
- a missing qualifier ("(DC2)")
- the same award year written three different ways across home, About and Bio
- 第38回 vs 第37回 for the same symposium

A PDF that **omits** something is not evidence that it should be removed. The publication
PDF had no domestic section at all. Flag omissions and let the user decide.

When the PDF disagrees with an official record (Crossref, the IEICE page), the official
record wins on the site, and you tell the user their PDF needs fixing.

The CV gives English translations of the Japanese paper titles in award lines. The site
keeps the **Japanese** titles in award lines, matching the publication entries; the user
explicitly asked for a Japanese-title typo fix there. The English title is still useful to
confirm which Japanese title is correct (e.g. "Time-varying Graph Learning…" ⇒ 時変グラフ学習).

## Markdown gotcha

`hardWraps` is off, so a list item continued on an indented next line renders as **one
run-on line**. Use `<br>` inside the item instead, the same idiom the About paragraph uses:

```markdown
- **Ph.D. Candidate**, Engineering, University of Osaka, expected March 2027<br>Advisor: Prof. Yuichi Tanaka<br>Thesis: …
```
