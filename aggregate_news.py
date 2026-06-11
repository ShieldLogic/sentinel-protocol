import feedparser
import requests
import json
import os
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# ── SANITIZER ────────────────────────────────────────────────────────────────
def clean_summary(raw_text, max_length=250):
    if not raw_text:
        return "No intel summary available."
    text_no_html = re.sub(r'<[^>]+>', '', raw_text)
    clean_text = " ".join(text_no_html.split())
    if len(clean_text) > max_length:
        return clean_text[:max_length].rsplit(' ', 1)[0] + '...'
    return clean_text

def parse_date(entry, fallback=None):
    """Try to extract a clean ISO date string from a feed entry."""
    for attr in ('published', 'updated', 'created'):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                pass
            try:
                # Try ISO format directly
                dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
                return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                pass
    return fallback or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── RSS FEEDS ─────────────────────────────────────────────────────────────────
# High-signal cybersecurity intel sources
RSS_FEEDS = [
    "https://www.bleepingcomputer.com/feed/",           # BleepingComputer — breaking breaches & malware
    "https://feeds.feedburner.com/TheHackersNews",       # The Hacker News — CVEs, nation-state, zero-days
    "https://cisa.gov/uscert/ncas/current-activity.xml", # CISA Alerts — federal/gov threat advisories
    "https://feeds.feedburner.com/darkreading",          # Dark Reading — enterprise security
    "https://www.schneier.com/blog/atom.xml",            # Schneier on Security — analysis & commentary
    "https://isc.sans.edu/rssfeed_full.xml",             # SANS ISC — threat intel & indicators
]

# ── GNEWS API ─────────────────────────────────────────────────────────────────
GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY")
GNEWS_URL = (
    f"https://gnews.io/api/v4/search"
    f"?q=cybersecurity+OR+%22zero-day%22+OR+ransomware+OR+%22data+breach%22+OR+%22CISA%22"
    f"&lang=en&max=10&apikey={GNEWS_API_KEY}"
)

articles_list = []

# ── FETCH RSS ─────────────────────────────────────────────────────────────────
for url in RSS_FEEDS:
    try:
        feed = feedparser.parse(url)
        source_name = url.split("//")[1].split("/")[0].replace("www.", "").split(".")[0].upper()
        for entry in feed.entries[:6]:
            raw_desc = getattr(entry, 'summary', getattr(entry, 'description', ''))
            clean_desc = clean_summary(raw_desc)
            articles_list.append({
                "title": entry.title,
                "description": f"[{source_name}] {clean_desc}",
                "url": entry.link,
                "date": parse_date(entry),
                "published_raw": parse_date(entry),
            })
    except Exception as e:
        print(f"RSS error ({url}): {e}")

# ── FETCH GNEWS ───────────────────────────────────────────────────────────────
if GNEWS_API_KEY:
    try:
        response = requests.get(GNEWS_URL, timeout=10)
        if response.status_code == 200:
            for art in response.json().get("articles", []):
                clean_desc = clean_summary(art.get('description', ''))
                pub = art.get("publishedAt", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
                articles_list.append({
                    "title": art["title"],
                    "description": f"[{art['source']['name'].upper()}] {clean_desc}",
                    "url": art["url"],
                    "date": pub,
                    "published_raw": pub,
                })
    except Exception as e:
        print(f"GNews API error: {e}")

# ── DEDUPLICATE by URL ────────────────────────────────────────────────────────
seen = set()
deduped = []
for a in articles_list:
    if a["url"] not in seen:
        seen.add(a["url"])
        deduped.append(a)

# ── SORT newest first ─────────────────────────────────────────────────────────
deduped.sort(key=lambda x: x.get("published_raw", ""), reverse=True)

# ── CLEAN OUTPUT (remove sort key) ───────────────────────────────────────────
for a in deduped:
    a.pop("published_raw", None)

# ── WRITE data.json ───────────────────────────────────────────────────────────
output_data = {
    "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    "news": deduped,
}

with open("data.json", "w") as f:
    json.dump(output_data, f, indent=2)

print(f"Sentinel Protocol Updated: {len(deduped)} signals intercepted.")
