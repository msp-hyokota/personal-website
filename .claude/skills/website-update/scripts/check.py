#!/usr/bin/env python3
"""Local consistency checks for the website. Run from the repo root.

    python3 .claude/skills/website-update/scripts/check.py
    python3 .claude/skills/website-update/scripts/check.py --absent "early access"
    python3 .claude/skills/website-update/scripts/check.py --no-build

ERROR = must fix before committing. WARN = look at it; it may be long-standing and
intentional, in which case mention it to the user instead of changing it.
Exit status is 1 if there are any ERRORs.

Each check exists because the problem it catches actually happened on this site.
"""
import argparse
import datetime as dt
import pathlib
import re
import subprocess
import sys

HOME = pathlib.Path("content/_index.md")
PUBS = pathlib.Path("content/publications/_index.md")
ABOUT = pathlib.Path("content/about/_index.md")
BIO = pathlib.Path("content/biography/_index.md")
POSTS = pathlib.Path("content/posts")

TAGS = {"pub-tag-journal": "Journal", "pub-tag-intl": "International",
        "pub-tag-domestic": "Domestic", "pub-tag-preprint": "Preprint"}
GROUP_ORDER = ["pub-tag-journal", "pub-tag-intl", "pub-tag-preprint", "pub-tag-domestic"]
MISSPELLINGS = {"東 宏志": "東 広志", "東宏志": "東広志"}
# home heading -> about heading (the names differ; that's intentional)
SECTION_PAIRS = [("Education", "Education"), ("Appointment", "Personal Appointment"),
                 ("Awards", "Awards"), ("Grants and Funding", "Grant and Funding")]

errors, warns = [], []
err = lambda m: errors.append(m)
warn = lambda m: warns.append(m)


def parse_pubs(path):
    """Return a list of dicts: year, title, tag, label, authors, venue, line."""
    out, year, cur = [], None, None
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = re.match(r"^#{2,3} (\d{4})\s*$", line)
        if m:
            year = int(m.group(1))
            continue
        if line.strip() == '<div class="pub-entry">':
            cur = {"year": year, "line": n, "title": None, "tag": None, "label": None,
                   "authors": None, "venue": None}
            continue
        if cur is None:
            continue
        m = re.match(r'<div class="pub-title">(.*?) <span class="pub-tag (pub-tag-[a-z]+)">([^<]*)</span></div>', line)
        if m:
            cur.update(title=m.group(1).strip(), tag=m.group(2), label=m.group(3))
        elif line.startswith('<div class="pub-title">'):
            err(f"{path}:{n} pub-title line not in the expected format")
        m = re.match(r'<div class="pub-authors">(.*)</div>', line)
        if m:
            cur["authors"] = m.group(1).strip()
        m = re.match(r'<div class="pub-venue">(.*)</div>', line)
        if m:
            cur["venue"] = m.group(1).strip()
        if line.strip() == "</div>":
            out.append(cur)
            cur = None
    return out


def check_publications():
    home, pubs = parse_pubs(HOME), parse_pubs(PUBS)
    if not home or not pubs:
        err("could not parse any publication entries; has the entry format changed?")
        return home
    # 1. both lists in step
    key = lambda e: (e["year"], e["title"], e["tag"], e["authors"])
    if [key(e) for e in home] != [key(e) for e in pubs]:
        hs, ps = [key(e) for e in home], [key(e) for e in pubs]
        for k in hs:
            if k not in ps:
                err(f"in {HOME} but not {PUBS} (or differs): {k[0]} | {k[1]} | {k[2]} | {k[3]}")
        for k in ps:
            if k not in hs:
                err(f"in {PUBS} but not {HOME} (or differs): {k[0]} | {k[1]} | {k[2]} | {k[3]}")
        if sorted(hs) == sorted(ps):
            err("both lists have the same entries but in a different order")

    for path, entries in ((HOME, home), (PUBS, pubs)):
        by_year = {}
        for e in entries:
            where = f"{path}:{e['line']}"
            # 2. tag class and label
            if e["tag"] not in TAGS:
                err(f"{where} unknown tag class {e['tag']}")
            elif e["label"] != TAGS[e["tag"]]:
                err(f"{where} tag {e['tag']} should be labelled {TAGS[e['tag']]!r}, not {e['label']!r}")
            v = e["venue"] or ""
            # 3. tag rules
            if re.search(r"Transactions|Journal|Letters", v) and e["tag"] != "pub-tag-journal":
                err(f"{where} venue looks like a journal but tag is {e['tag']}: {e['title']}")
            if re.search(r"Pre-?print|arXiv", v, re.I) and e["tag"] != "pub-tag-preprint":
                err(f"{where} venue says preprint but tag is {e['tag']}: {e['title']}")
            if e["tag"] == "pub-tag-preprint" and not re.search(r"Pre-?print", v, re.I):
                warn(f"{where} Preprint tag but venue doesn't say 'Pre-print on arXiv (Submitted to …)': {e['title']}")
            if "early access" in v.lower():
                warn(f"{where} still early access; run lookup.py on its DOI to see if it's in an issue now: {e['title']}")
            if re.search(r"pp\. \d+-\d+", v):
                err(f"{where} page range uses a hyphen; use an en dash (–): {v}")
            # 4. symposium number = year - 1985
            for num, yr in re.findall(r"第(\d+)回信号処理シンポジウム[^0-9]*?(\d{4})年", v):
                if int(num) != int(yr) - 1985:
                    err(f"{where} 第{num}回信号処理シンポジウム in {yr}; expected 第{int(yr) - 1985}回")
            by_year.setdefault(e["year"], []).append(e)
        # 5. group order within each year
        for yr, es in by_year.items():
            ranks = [GROUP_ORDER.index(e["tag"]) for e in es if e["tag"] in GROUP_ORDER]
            if ranks != sorted(ranks):
                seq = " → ".join(TAGS[e["tag"]] for e in es if e["tag"] in TAGS)
                warn(f"{path} {yr}: order is {seq}; convention is Journal → International → Preprint → Domestic")
    return home


def bullets_under(text, heading):
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.S | re.M)
    if not m:
        return None
    items = [l for l in m.group(1).splitlines() if l.startswith("- ")]
    # Treat "2024-2026"/"2024–2026" and " - "/" – " as equal, but leave "Part-time" alone.
    norm = lambda s: re.sub(r"\s+", " ", re.sub(r"\s+-\s+", " - ", s.replace("–", "-").replace("—", "-"))).strip()
    return [norm(i) for i in items]


def check_profile(home_pubs):
    home, about = HOME.read_text(encoding="utf-8"), ABOUT.read_text(encoding="utf-8")
    # 6. home vs about sections
    for h, a in SECTION_PAIRS:
        hb, ab = bullets_under(home, h), bullets_under(about, a)
        if hb is None or ab is None:
            warn(f"section missing: home '## {h}' {'found' if hb is not None else 'MISSING'}, "
                 f"about '## {a}' {'found' if ab is not None else 'MISSING'}")
            continue
        if hb != ab:
            for x in hb:
                if x not in ab:
                    err(f"'{h}' differs, home only: {x}")
            for x in ab:
                if x not in hb:
                    err(f"'{a}' differs, about only: {x}")
    # 7. award lines cite existing publication titles
    titles = {e["title"] for e in home_pubs}
    for path, text in ((HOME, home), (ABOUT, about)):
        for t in re.findall(r'for ["“]([^"”]+)["”]', text):
            if t not in titles:
                warn(f"{path}: award cites \"{t}\", which matches no publication title")
    # 8. bio award years agree with home
    if BIO.exists():
        bio = BIO.read_text(encoding="utf-8")
        for yr, name in re.findall(r"^- \*\*(\d{4})\*\* [–-] ([^,]+),", home, re.M):
            m = re.search(re.escape(name.strip()) + r"[^.]*?\b(\d{4})\b", bio)
            if m and m.group(1) != yr:
                err(f"{BIO}: '{name.strip()}' year is {m.group(1)}, home says {yr}")


def check_text():
    files = [p for p in pathlib.Path("content").rglob("*.md")]
    for p in files:
        lines = p.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            # 9. known misspellings
            for bad, good in MISSPELLINGS.items():
                if bad in line:
                    err(f"{p}:{i + 1} '{bad}' should be '{good}'")
            # 10. list item continued on an indented line renders as one run-on line
            if (line.startswith("- ") and i + 1 < len(lines)
                    and re.match(r"^ {2,}[^\s\-\*\d<]", lines[i + 1])):
                err(f"{p}:{i + 2} indented continuation renders as a run-on line (hardWraps is off); join it with <br>")


def check_posts():
    today = dt.date.today()
    for p in sorted(POSTS.glob("*.md")):
        fm = p.read_text(encoding="utf-8").split("---")
        if len(fm) < 3:
            err(f"{p}: missing front matter")
            continue
        head = fm[1]
        for field in ("title", "date", "summary"):
            if not re.search(rf"^{field}:", head, re.M):
                err(f"{p}: front matter has no '{field}'")
        m = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", head, re.M)
        # 11. Hugo skips future-dated posts (buildFuture is off)
        if m and dt.date.fromisoformat(m.group(1)) > today:
            err(f"{p}: date {m.group(1)} is in the future; Hugo will not build it")
        if re.search(r"^draft:\s*true", head, re.M):
            warn(f"{p}: draft: true, so it won't be published")


def check_build():
    r = subprocess.run(["hugo", "--gc", "--minify", "--quiet"], capture_output=True, text=True)
    if r.returncode != 0:
        err("hugo build failed:\n" + (r.stderr or r.stdout).strip())
    elif r.stderr.strip():
        warn("hugo printed warnings:\n" + r.stderr.strip())


def check_absent(strings):
    for s in strings:
        hits = []
        for p in pathlib.Path("content").rglob("*.md"):
            for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if s in line:
                    hits.append(f"{p}:{n}")
        if hits:
            err(f"'{s}' should be gone but is still at: {', '.join(hits)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--absent", action="append", default=[], help="string that must not appear in content/")
    ap.add_argument("--no-build", action="store_true", help="skip the hugo build")
    a = ap.parse_args()
    if not HOME.exists():
        sys.exit("Run this from the repository root (content/_index.md not found).")

    home_pubs = check_publications()
    check_profile(home_pubs)
    check_text()
    check_posts()
    check_absent(a.absent)
    if not a.no_build:
        check_build()

    n = len(parse_pubs(HOME))
    for m in errors:
        print("ERROR  " + m)
    for m in warns:
        print("WARN   " + m)
    print(f"\n{n} publications parsed · {len(errors)} error(s) · {len(warns)} warning(s)"
          + ("" if a.no_build else " · hugo build ran"))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
