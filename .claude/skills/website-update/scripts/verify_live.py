#!/usr/bin/env python3
"""Confirm a change actually reached https://haruki-yokota.jp. Run from the repo root.

    python3 verify_live.py --wait --expect "/::SIP2026-45" --absent "/::early access"

--wait        find the GitHub Actions deploy run for the current HEAD and wait for it
--expect P::S string S must appear on page P (P is a path such as / or /publications/)
--absent P::S string S must NOT appear on page P
--status P    page P must return HTTP 200 (e.g. a new post's URL). Use --status P::404
              for a page that should be gone.

Page HTML is minified and entity-encoded (&ndash; etc.), so each page is entity-decoded
and matched both raw and with tags stripped. Missing expectations are retried for about
two minutes in case the Pages CDN still serves the old copy.
Exit status is 1 if any check fails.
"""
import argparse
import html
import json
import re
import subprocess
import sys
import time

SITE = "https://haruki-yokota.jp"
REPO = "msp-hyokota/personal-website"


def sh(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def wait_for_deploy():
    head = sh("git", "rev-parse", "HEAD").stdout.strip()
    run = None
    for _ in range(24):  # up to ~2 min for the run to be registered
        r = sh("gh", "run", "list", "--repo", REPO, "--limit", "10",
               "--json", "databaseId,headSha,status,conclusion,displayTitle")
        runs = json.loads(r.stdout or "[]")
        run = next((x for x in runs if x["headSha"] == head), None)
        if run:
            break
        time.sleep(5)
    if not run:
        print(f"FAIL   no workflow run found for HEAD {head[:7]}. Was it pushed?")
        return False
    sh("gh", "run", "watch", str(run["databaseId"]), "--repo", REPO, "--exit-status")
    r = sh("gh", "run", "view", str(run["databaseId"]), "--repo", REPO, "--json", "conclusion,url")
    info = json.loads(r.stdout or "{}")
    ok = info.get("conclusion") == "success"
    print(f"{'OK   ' if ok else 'FAIL '}  deploy {head[:7]} → {info.get('conclusion')}  {info.get('url', '')}")
    return ok


def fetch(path):
    r = sh("curl", "-sSL", "--max-time", "30", "-H", "Cache-Control: no-cache",
           "-w", "\n%{http_code}", SITE + path)
    body, _, code = r.stdout.rpartition("\n")
    decoded = html.unescape(body)
    stripped = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", decoded))
    return int(code or 0), decoded, stripped


def split(spec):
    if "::" not in spec:
        sys.exit(f"expected PAGE::TEXT, got {spec!r}")
    page, text = spec.split("::", 1)
    return (page if page.startswith("/") else "/" + page), text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--expect", action="append", default=[])
    ap.add_argument("--absent", action="append", default=[])
    ap.add_argument("--status", action="append", default=[])
    a = ap.parse_args()

    ok = True
    if a.wait:
        ok = wait_for_deploy() and ok

    checks = [("expect",) + split(s) for s in a.expect] + [("absent",) + split(s) for s in a.absent]
    pending = list(checks)
    for attempt in range(7):
        cache, still = {}, []
        for kind, page, text in pending:
            if page not in cache:
                cache[page] = fetch(page)
            _, dec, stripped = cache[page]
            present = text in dec or text in stripped
            if present != (kind == "expect"):
                still.append((kind, page, text))
        pending = still
        if not pending:
            break
        if attempt < 6:
            time.sleep(20)
    for kind, page, text in checks:
        failed = (kind, page, text) in pending
        ok = ok and not failed
        verb = "present" if kind == "expect" else "absent "
        print(f"{'FAIL ' if failed else 'OK   '}  {verb} {page:<32} {text}")

    for spec in a.status:
        page, want = (spec.split("::", 1) + ["200"])[:2]
        page = page if page.startswith("/") else "/" + page
        code = fetch(page)[0]
        good = code == int(want)
        ok = ok and good
        print(f"{'OK   ' if good else 'FAIL '}  HTTP {code} (want {want}) {page}")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
