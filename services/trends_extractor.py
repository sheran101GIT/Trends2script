import requests
# pyrefly: ignore [missing-import]
import feedparser
from datetime import datetime, timezone

def fetch_trends(geo="IN", category="All"):
    """
    Fetches trending searches using the trendspy library (Google Trends Trending Now API).
    
    trendspy returns ~150 trends, each with pre-assigned topic_names like 
    ['Sports'], ['Entertainment'], etc. — which EXACTLY match the dashboard 
    dropdown values. This allows true source-level category filtering without
    relying on the LLM.
    
    Falls back to the RSS feed if trendspy fails (e.g. Google rate-limits).
    
    Returns a list of dicts: [{'topic': ..., 'traffic': ..., 'published': ..., 'source_category': ...}]
    """
    # ── Primary: trendspy (supports category filtering) ──
    try:
        from trendspy import Trends
        tr = Trends()
        results = tr.trending_now(geo=geo)
        
        if results:
            print(f"[DEBUG] trendspy returned {len(results)} trends for geo={geo}")
            
            # Filter by category if a specific one is selected
            if category != "All":
                filtered = [
                    r for r in results
                    if r.topic_names and category in r.topic_names
                ]
                print(f"[DEBUG] After filtering for '{category}': {len(filtered)} trends")
            else:
                filtered = results
            
            if not filtered:
                print(f"[DEBUG] No trends found for category '{category}' — returning empty")
                return []
            
            # Sort by volume (highest first) and take top 20
            filtered.sort(key=lambda r: r.volume or 0, reverse=True)
            top = filtered[:20]
            
            trends = []
            for r in top:
                # Convert timestamp to readable format
                published = ""
                if r.started_timestamp:
                    try:
                        ts = r.started_timestamp[0]
                        published = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
                    except Exception:
                        pass
                
                trends.append({
                    "topic": r.keyword,
                    "traffic": f"{r.volume:,}+" if r.volume else "N/A",
                    "published": published,
                    "source_category": r.topic_names[0] if r.topic_names else "Unknown",
                    "related_keywords": r.trend_keywords[:5] if r.trend_keywords else []
                })
            
            print(f"[DEBUG] Returning {len(trends)} trends from trendspy")
            return trends
        else:
            print("[WARN] trendspy returned empty results, falling back to RSS")
            
    except ImportError:
        print("[WARN] trendspy not installed, falling back to RSS feed")
    except Exception as e:
        print(f"[WARN] trendspy failed ({type(e).__name__}: {e}), falling back to RSS feed")
    
    # ── Fallback: RSS feed (no category support) ──
    return _fetch_trends_rss(geo)


def _fetch_trends_rss(geo="IN"):
    """
    Fallback: Fetches daily trends from the Google Trends RSS feed.
    Does NOT support category filtering — the LLM prompt handles filtering instead.
    """
    print(f"[DEBUG] Fetching trends from RSS feed for geo={geo}")
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch RSS feed. Status code: {response.status_code}")
            return []
            
        feed = feedparser.parse(response.content)
        
        trends = []
        for entry in feed.entries[:20]:  # Fetch top 20, LLM will filter top 10 relevant
            title = entry.title
            traffic = entry.get('ht_approx_traffic', 'N/A')
            published = entry.get('published', '')
            trends.append({
                "topic": title,
                "traffic": traffic,
                "published": published
            })
            
        print(f"[DEBUG] RSS returned {len(trends)} trends (unfiltered)")
        return trends
    except Exception as e:
        print(f"Error fetching trends from RSS: {e}")
        return []
