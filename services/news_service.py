import urllib.parse
# pyrefly: ignore [missing-import]
import feedparser

def fetch_recent_news(topic: str, max_items: int = 5) -> list:
    """
    Fetches recent news articles from Google News RSS for the given topic.
    Returns a list of dicts containing the title and link.
    """
    try:
        encoded_topic = urllib.parse.quote(topic)
        url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        
        if not feed.entries:
            return []
            
        news_items = []
        for entry in feed.entries[:max_items]:
            news_items.append({
                "title": entry.title,
                "link": entry.link
            })
            
        return news_items
    except Exception as e:
        print(f"[News Service] Error fetching news for '{topic}': {e}")
        return []
