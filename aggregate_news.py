import feedparser
import requests
import json
import os
from datetime import datetime

# 1. High-Trust RSS Feeds
RSS_FEEDS = [
    "https://www.bleepingcomputer.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://cisa.gov/uscert/ncas/current-activity.xml"
]

# 2. Real-Time API (GNews)
GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY")
GNEWS_URL = f"https://gnews.io/api/v4/search?q=cybersecurity OR infosec OR ransomware&lang=en&max=10&apikey={GNEWS_API_KEY}"

articles_list = []

# --- FETCH RSS FEEDS ---
for url in RSS_FEEDS:
    try:
        feed = feedparser.parse(url)
        source_name = url.split("//")[1].split("/")[0].replace("www.", "")
        
        for entry in feed.entries[:5]: # Top 5 per feed
            # Safely grab description/summary
            desc = getattr(entry, 'summary', getattr(entry, 'description', 'No intel summary available.'))
            
            articles_list.append({
                "title": entry.title,
                "description": f"[{source_name.upper()}] {desc}", # Formatted for your UI
                "url": entry.link,
                "published_raw": getattr(entry, 'published', datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
            })
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# --- FETCH GNEWS API ---
if GNEWS_API_KEY:
    try:
        response = requests.get(GNEWS_URL)
        if response.status_code == 200:
            api_data = response.json().get("articles", [])
            for art in api_data:
                articles_list.append({
                    "title": art["title"],
                    "description": f"[{art['source']['name'].upper()}] {art['description']}",
                    "url": art["url"],
                    "published_raw": art["publishedAt"]
                })
    except Exception as e:
        print(f"API fetch failed: {e}")

# --- SORT & FORMAT FOR FRONTEND ---
# Sort by newest first
articles_list.sort(key=lambda x: x["published_raw"], reverse=True)

# Remove the raw date field as your frontend doesn't need it, keep it clean
for article in articles_list:
    article.pop("published_raw", None)

# Construct the exact JSON structure your index.html expects
output_data = {
    "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    "news": articles_list
}

# Write to data.json
with open("data.json", "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Sentinel Protocol Updated: {len(articles_list)} signals intercepted.")
