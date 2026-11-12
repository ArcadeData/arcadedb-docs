#!/usr/bin/env python3
"""
Tell IndexNow (Bing, Yandex, Seznam, Naver, ...) which docs URLs changed in
a deploy. Google does not use IndexNow.

Two steps, run by .github/workflows/cloudflare-deploy.yml around the deploy:

  indexnow.py snapshot DIR        before the deploy: save the live sitemaps
  indexnow.py submit DIR SITE     after the deploy: diff SITE's sitemaps
                                  against DIR and submit what changed

A URL counts as changed when it is new, when its <lastmod> differs (lastmod
is the page source's last git commit date, see sitemap-lastmod.py), or when
it left the sitemap (a removed or redirected page, so engines recrawl it and
see the 404 or 301). Without a snapshot nothing is submitted: resubmitting
every URL on every deploy is what IndexNow asks sites not to do.

The key is public by design: scripts/templates/<key>.txt holds it and
`npm run redirects` copies it to the site root. Exit status is 0 unless the
command line is wrong; the workflow step is non-blocking anyway.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HOST = "docs.arcadedb.com"
SITE_URL = f"https://{HOST}"
ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_DIR = Path(__file__).resolve().parent / "templates"
MAX_URLS = 10_000
UA = "arcadedb-docs-deploy"

URL_RE = re.compile(r"<url>(.*?)</url>", re.S)
LOC_RE = re.compile(r"<loc>([^<]+)</loc>")
LASTMOD_RE = re.compile(r"<lastmod>([^<]+)</lastmod>")


def key() -> str:
    keys = [p.stem for p in KEY_DIR.glob("*.txt") if re.fullmatch(r"[a-f0-9]{32}", p.stem)]
    if len(keys) != 1:
        sys.exit(f"expected one IndexNow key file in {KEY_DIR}, found {len(keys)}")
    return keys[0]


def get(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, ""


def parse(xml: str) -> dict[str, str]:
    entries = {}
    for body in URL_RE.findall(xml):
        loc = LOC_RE.search(body)
        if loc:
            mod = LASTMOD_RE.search(body)
            entries[loc.group(1).strip()] = mod.group(1).strip() if mod else ""
    return entries


def snapshot(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    status, index = get(f"{SITE_URL}/sitemap.xml")
    if status != 200:
        print(f"indexnow: live sitemap.xml returned {status}, no snapshot")
        return 0
    for loc in re.findall(r"<loc>([^<]+)</loc>", index):
        name = loc.rsplit("/", 1)[-1]
        status, xml = get(loc)
        if status == 200:
            (out / name).write_text(xml, encoding="utf-8")
        print(f"indexnow: snapshot {name}: {status}")
    return 0


def load(directory: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for f in sorted(directory.glob("sitemap-*.xml")):
        entries.update(parse(f.read_text(encoding="utf-8")))
    return entries


def changed(old: dict[str, str], new: dict[str, str]) -> list[str]:
    urls = [u for u, mod in new.items() if old.get(u) != mod]
    urls += [u for u in old if u not in new]
    return sorted(set(urls))


def wait_for(url: str, expect: str, attempts: int = 10, delay: int = 15) -> bool:
    for i in range(attempts):
        status, body = get(url)
        if status == 200 and body.strip() == expect:
            return True
        print(f"indexnow: {url} -> {status}, waiting ({i + 1}/{attempts})")
        time.sleep(delay)
    return False


def post(urls: list[str], k: str) -> int:
    payload = json.dumps({
        "host": HOST,
        "key": k,
        "keyLocation": f"{SITE_URL}/{k}.txt",
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=payload, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except urllib.error.URLError as e:
        print(f"indexnow: {e.reason}")
        return 0


def submit(previous: Path, site: Path) -> int:
    old = load(previous) if previous.is_dir() else {}
    if not old:
        print("indexnow: no snapshot of the previous sitemaps, nothing submitted")
        return 0
    urls = changed(old, load(site))
    print(f"indexnow: {len(urls)} changed URLs")
    for u in urls:
        print(f"  {u}")
    if not urls:
        return 0
    k = key()
    if not wait_for(f"{SITE_URL}/{k}.txt", k):
        print("indexnow: key file not live, nothing submitted")
        return 0
    for start in range(0, len(urls), MAX_URLS):
        batch = urls[start:start + MAX_URLS]
        for attempt in range(3):
            status = post(batch, k)
            print(f"indexnow: POST {len(batch)} URLs -> HTTP {status}")
            if status in (200, 202):
                break
            if status in (400, 403, 422):  # bad request or key: retrying will not help
                break
            time.sleep(30 * (attempt + 1))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "snapshot":
        return snapshot(Path(argv[1]))
    if len(argv) == 3 and argv[0] == "submit":
        return submit(Path(argv[1]), Path(argv[2]))
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
