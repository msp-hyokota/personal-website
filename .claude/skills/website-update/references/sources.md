# Verifying facts: which sources work

| Source | Automated access | Use it for |
|---|---|---|
| Crossref API (`api.crossref.org/works/<DOI>`) | ✅ via `scripts/lookup.py` | Official title, authors, journal, volume, pages, year for any DOI. Missing volume/pages means the paper is still in early access. |
| arXiv API (`export.arxiv.org/api/query`) | ✅ via `scripts/lookup.py` | Title, authors, v1 date, comment ("Submitted to …"), and journal-ref/DOI once added |
| arXiv abs page | ✅ WebFetch | fallback |
| doi.org | redirects to IEEE Xplore | only to learn the Xplore document number |
| IEEE Xplore | ❌ returns an empty page | nothing; use Crossref instead |
| ken.ieice.org (IEICE program / 講演論文詳細) | ❌ HTTP 403, even with curl and a browser UA | Ask the user for a PDF/screenshot of the 講演論文詳細 page. It has 発表日時, 開催地, 文献情報 (vol/no/pp), and the official English title and romanized author names. |
| Web search | ✅ | the address of a venue building (e.g. a ryokan); general confirmation |

## Machine quirks

- **Python `urllib` fails SSL verification on this Mac.** Fetch with `curl`
  (via `subprocess`) instead; the bundled scripts already do this.
- Don't put the user's email in request headers (e.g. Crossref's "polite" User-Agent)
  unless they ask. The scripts use a generic User-Agent.
- The built site is minified. Attribute quotes are dropped (`href=/biography/`), and en
  dashes may be literal `–` or `&ndash;`. `verify_live.py` decodes entities before
  matching. If you grep by hand, search for the literal character.
- Local Hugo (Homebrew) is newer than the version pinned in
  `.github/workflows/deploy.yml`. If CI fails but the local build passes, compare versions
  first.
