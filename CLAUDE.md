# CLAUDE.md

## Project Overview

Personal academic website for Haruki Yokota (横田 陽樹), a graduate student at Osaka University MSP Lab.
Built with Hugo + Blowfish theme, deployed to GitHub Pages at **https://haruki-yokota.jp**.

## Tech Stack

- **Static site generator**: Hugo (extended), version pinned in `.github/workflows/deploy.yml`
- **Theme**: Blowfish (git submodule at `themes/blowfish`)
- **Deployment**: GitHub Actions → GitHub Pages (`build_type: workflow`, not legacy Jekyll)
- **Remote**: HTTPS — `https://github.com/msp-hyokota/personal-website.git`

## Key Files

| File | Purpose |
|------|---------|
| `config/_default/hugo.toml` | Base URL, title, site-wide settings |
| `config/_default/params.toml` | Theme options, author profile picture (`[author] image`) |
| `config/_default/menus.en.toml` | Navigation menu links |
| `assets/css/custom.css` | Custom CSS overrides (publication cards, tag badges, alignment fixes) |
| `assets/profile_pic.jpg` | Homepage profile picture |
| `content/_index.md` | **Main single-page layout** — all sections live here |
| `content/about/_index.md` | Standalone About page (mirrors About section on home) |
| `content/publications/_index.md` | Standalone Publications page (mirrors Publications section on home) |
| `static/CNAME` | Custom domain declaration (`haruki-yokota.jp`) |
| `static/.nojekyll` | Prevents GitHub from running Jekyll on the repo |
| `.github/workflows/deploy.yml` | CI/CD: builds with Hugo, deploys to GitHub Pages |

## Site Structure

The site uses a **single-page layout**. All content (About, Publications, Awards, Grants, Contact) is in `content/_index.md`. The navigation menu uses anchor links (`/#about`, `/#publications`, `/#awards`) to jump to sections on the home page.

Individual section pages (`about/`, `publications/`) still exist and are kept in sync manually.

## Publications Format

Publications are rendered as styled HTML cards using custom CSS classes defined in `assets/css/custom.css`. Always use this structure:

```html
<div class="pub-entry">
<div class="pub-title">Paper Title <span class="pub-tag pub-tag-intl">International</span></div>
<div class="pub-authors">Author list</div>
<div class="pub-venue">Venue, location, year</div>
<div class="pub-links"><a href="URL">Label</a></div>
</div>
```

Tag classes:
- `pub-tag-journal` — rose, for journal / transaction papers
- `pub-tag-intl` — purple, for international conferences
- `pub-tag-domestic` — green, for domestic (Japanese) conferences
- `pub-tag-preprint` — amber, for arXiv preprints

`pub-tag-intl` and `pub-tag-domestic` are for **conference papers only**. Journal and
transaction papers (e.g. IEEE Transactions on Signal Processing) use `pub-tag-journal`
regardless of where the publisher is based.

The `pub-links` div is optional (omit if no links available).

Any change to publications must be applied to **both** `content/_index.md` and `content/publications/_index.md`.

## CSS Overrides

`assets/css/custom.css` contains:
- `article .prose { text-align: left; }` — overrides Blowfish profile layout's `text-center` so body content is left-aligned
- Publication card styles (`.pub-entry`, `.pub-title`, `.pub-authors`, `.pub-venue`, `.pub-links`)
- Tag badge styles (`.pub-tag`, `.pub-tag-journal`, `.pub-tag-intl`, `.pub-tag-domestic`, `.pub-tag-preprint`)

Do not remove these — removing the prose override will cause all content to center-align.

## Deployment

Pushing to `main` automatically triggers the deploy workflow. To manually trigger:
```bash
gh workflow run "Deploy Hugo site to Pages" --repo msp-hyokota/personal-website
```

GitHub Pages is set to `build_type: workflow` (GitHub Actions). Do not change this to `legacy` — it will break the build by triggering the Jekyll builder on Hugo source files.

## Git Workflow

```bash
git add <specific files>   # never use git add -A
git commit -m "message"
git push
```

The remote uses HTTPS. Authentication is handled via macOS Keychain (osxkeychain credential helper) with a GitHub Personal Access Token.

## Markdown Linter Warnings

The project has a markdownlint config that flags inline HTML (`MD033`) and duplicate headings (`MD024`). These warnings are expected and safe to ignore — Hugo renders inline HTML correctly. Do not restructure content solely to suppress them.
