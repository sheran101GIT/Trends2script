import urllib.parse
# pyrefly: ignore [missing-import]
import feedparser

def fetch_recent_news(topic: str, max_items: int = 5) -> str:
    """
    Fetches recent news articles from Google News RSS for the given topic.
    Returns a formatted string containing the headlines and their links.
    """
    try:
        encoded_topic = urllib.parse.quote(topic)
        url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        
        if not feed.entries:
            return "No recent news found."
            
        news_items = []
        for entry in feed.entries[:max_items]:
            title = entry.title
            link = entry.link
            news_items.append(f"- {title}\n  Source Link: {link}")
            
        return "\n\n".join(news_items)
    except Exception as e:
        print(f"[News Service] Error fetching news for '{topic}': {e}")
        return "Failed to fetch recent news."
