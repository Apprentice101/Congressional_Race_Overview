#!/usr/bin/env python3
"""
Fetches headlines for the news well from Google News RSS (no API key required)
and writes them to news.json at the repo root.

Edit QUERIES below to change what the wire tracks.
Run manually with: python scripts/fetch_news.py
"""

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# --- Edit these to change what the news well tracks ---------------------
QUERIES = [
    "2026 congressional election",
    "2026 midterm elections House",
    "2026 Senate race",
]
MAX_ITEMS = 20
OUTPUT_PATH = "news.json"
# --------------------------------------------------------------------------

USER_AGENT = "Mozilla/5.0 (compatible; NewsWellBot/1.0)"


def fetch_query(query: str):
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read()

    root = ET.fromstring(raw)
    items = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        source_el = item.find("source")
        source = source_el.text.strip() if source_el is not None and source_el.text else ""

        # Google News titles are formatted "Headline - Source"; strip the
        # trailing " - Source" if we already have a cleaner source tag.
        clean_title = title
        if source and title.endswith(" - " + source):
            clean_title = title[: -(len(source) + 3)].strip()

        published_iso = None
        if pub_date:
            try:
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                published_iso = dt.replace(tzinfo=timezone.utc).isoformat()
            except ValueError:
                published_iso = None

        if title and link:
            items.append(
                {
                    "title": clean_title,
                    "link": link,
                    "source": source,
                    "published": published_iso,
                }
            )
    return items


def dedupe(items):
    seen = set()
    out = []
    for it in items:
        key = re.sub(r"\W+", "", it["title"].lower())[:80]
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def main():
    all_items = []
    for q in QUERIES:
        try:
            all_items.extend(fetch_query(q))
        except Exception as exc:  # noqa: BLE001 - keep the workflow resilient
            print(f"Warning: query '{q}' failed: {exc}")

    all_items = dedupe(all_items)
    all_items.sort(key=lambda x: x["published"] or "", reverse=True)
    all_items = all_items[:MAX_ITEMS]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "queries": QUERIES,
        "items": all_items,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(all_items)} items to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
