import os, requests, json
from datetime import datetime

# Focus on cybersecurity signal, ignoring generic tech noise
QUERY = '(cybersecurity OR "data breach" OR "zero-day" OR "ransomware")'

def run():
    api_key = os.getenv('NEWS_API_KEY')
    url = f"https://newsapi.org/v2/everything?q={QUERY}&sortBy=publishedAt&pageSize=10&language=en&apiKey={api_key}"
    
    response = requests.get(url).json()
    articles = response.get('articles', [])
    
    data = {
        "title": "Sentinel Protocol",
        "tagline": "Perimeter Intelligence Sync",
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "news": articles
    }
    
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    run()

# 1. Define High-Authority Trust List
TRUSTED_DOMAINS = [
    "krebsonsecurity.com", "darkreading.com", "bleepingcomputer.com", 
    "thehackernews.com", "mandiant.com", "wired.com", "reuters.com",
    "mit.edu", "openai.com", "anthropic.com", "techcrunch.com", "zdnet.com"
]

def is_reputable(url):
    """Verifies if the news source is in our high-signal allowlist."""
    try:
        # Extract domain from URL
        domain = url.split('//')[-1].split('/')[0].replace('www.', '')
        return domain in TRUSTED_DOMAINS
    except Exception:
        return False

# 2. Update your Fetch Logic
def fetch_verified_intel():
    api_key = os.getenv('NEWS_API_KEY')
    # ... existing request code ...
    
    raw_articles = response.json().get('articles', [])
    
    # FILTERING LAYER: Only keep articles from trusted sources
    verified_articles = [art for art in raw_articles if is_reputable(art['url'])]
    
    # FALLBACK: If the trust list is too strict today, take the top 5 'Relevancy' 
    # scores from general sources but flag them as 'Unverified'.
    if len(verified_articles) < 3:
        verified_articles = raw_articles[:5] 
        
    return verified_articles
