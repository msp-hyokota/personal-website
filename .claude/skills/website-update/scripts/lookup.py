#!/usr/bin/env python3
"""Look up the official citation for a DOI or arXiv ID.

    python3 lookup.py 10.1109/TSP.2026.3712068
    python3 lookup.py https://doi.org/10.1109/TSP.2026.3712068
    python3 lookup.py 2609.36854
    python3 lookup.py https://arxiv.org/abs/2609.36854v2

DOIs go to Crossref; arXiv IDs go to the arXiv API. Everything is fetched with curl because
Python's urllib fails SSL verification on this machine. No personal data is sent: the
User-Agent is generic.

Besides the raw metadata, it prints the author and venue strings in the site's format so
they can be pasted into a pub-entry.
"""
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

UA = "haruki-yokota.jp-maintenance/1.0"
ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")
DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s?#]+)")


def curl(url):
    r = subprocess.run(["curl", "-sSL", "--max-time", "30", "-A", UA, url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"curl failed for {url}: {r.stderr.strip()}")
    return r.stdout


def initials(given, family):
    """'Haruki', 'Yokota' -> 'H. Yokota'; 'Jun-ya' -> 'J.-Y.'"""
    parts = [p for p in re.split(r"\s+", given.strip()) if p]
    out = []
    for p in parts:
        out.append("-".join(s[0].upper() + "." for s in p.split("-") if s))
    return (" ".join(out) + " " + family).strip()


def split_name(full):
    bits = full.strip().split()
    return (" ".join(bits[:-1]), bits[-1]) if len(bits) > 1 else ("", full.strip())


def en_dash(pages):
    return re.sub(r"\s*[-‐‑‒–—]\s*", "–", pages) if pages else pages


def crossref(doi):
    raw = curl(f"https://api.crossref.org/works/{doi}")
    try:
        m = json.loads(raw)["message"]
    except (json.JSONDecodeError, KeyError):
        sys.exit(f"Crossref has no record for {doi} (response: {raw[:120]!r})")
    title = " ".join(m.get("title") or ["?"])
    authors = m.get("author", [])
    journal = " ".join(m.get("container-title") or [""])
    vol, issue, pages = m.get("volume"), m.get("issue"), en_dash(m.get("page"))
    year = None
    for key in ("published-print", "published-online", "issued", "published"):
        dp = (m.get(key) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            year = dp[0][0]
            break
    status = ("published (volume/pages assigned)" if vol and pages
              else "EARLY ACCESS (no volume/pages yet)")

    print("source   : Crossref")
    print(f"title    : {title}")
    print("authors  : " + ", ".join(f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors))
    print(f"journal  : {journal}")
    print(f"volume   : {vol}   issue: {issue}   pages: {pages}   year: {year}")
    print(f"type     : {m.get('type')}")
    print(f"status   : {status}")
    print()
    print("site authors : " + ", ".join(initials(a.get("given", ""), a.get("family", "")) for a in authors))
    if vol and pages:
        print(f"site venue   : {journal}, vol. {vol}, pp. {pages}, {year}")
    else:
        print(f"site venue   : {journal} (early access)")
    print(f"site link    : <a href=\"https://doi.org/{doi}\">DOI</a>")


def arxiv(aid):
    raw = curl(f"https://export.arxiv.org/api/query?id_list={aid}")
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    try:
        entry = ET.fromstring(raw).find("a:entry", ns)
    except ET.ParseError:
        sys.exit(f"arXiv API returned unparseable data for {aid}")
    if entry is None or entry.find("a:title", ns) is None:
        sys.exit(f"arXiv has no record for {aid}")

    def txt(path):
        el = entry.find(path, ns)
        return re.sub(r"\s+", " ", el.text).strip() if el is not None and el.text else None

    title = txt("a:title")
    names = [re.sub(r"\s+", " ", n.text).strip() for n in entry.findall("a:author/a:name", ns)]
    print("source    : arXiv")
    print(f"title     : {title}")
    print(f"authors   : {', '.join(names)}")
    print(f"v1 date   : {(txt('a:published') or '')[:10]}   (use as the date of a submission post)")
    print(f"latest    : {(txt('a:updated') or '')[:10]}")
    print(f"comment   : {txt('x:comment')}")
    print(f"journalref: {txt('x:journal_ref')}")
    doi = txt("x:doi")
    print(f"doi       : {doi}")
    print()
    print("site authors : " + ", ".join(initials(*split_name(n)) for n in names))
    m = re.search(r"[Ss]ubmitted to (?:the )?(?:IEEE )?([^.;,]+)", txt("x:comment") or "")
    if m:
        print(f"site venue   : Pre-print on arXiv (Submitted to {m.group(1).strip()})")
    print(f"site link    : <a href=\"https://arxiv.org/abs/{aid}\">arXiv</a>")
    if doi:
        print(f"\nThis preprint lists a published DOI; run: lookup.py {doi}")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    arg = sys.argv[1].strip()
    if "arxiv" in arg.lower() and "10.48550" not in arg or ARXIV_RE.fullmatch(arg):
        m = ARXIV_RE.search(arg)
        if not m:
            sys.exit(f"Could not find an arXiv ID in {arg!r}")
        return arxiv(m.group(1))
    m = DOI_RE.search(arg)
    if m:
        doi = m.group(1).rstrip("/.")
        if doi.lower().startswith("10.48550/arxiv."):
            return arxiv(doi.split(".", 2)[-1])
        return crossref(doi)
    sys.exit(f"Not a DOI or arXiv ID: {arg!r}")


if __name__ == "__main__":
    main()
