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
