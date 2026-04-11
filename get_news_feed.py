from flask import Flask, render_template
from datetime import datetime
from dateutil import parser
import requests
import feedparser

app = Flask(__name__)

def fetch_rss(feed_url, limit=1000):
    feed = feedparser.parse(feed_url)
    
    articles = []
    for entry in feed.entries[:limit]:
        article = {
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", "N/A")
        }
        articles.append(article)
    
    return articles


def print_articles(source, articles):
    print("\n" + "="*50)
    print(f"{source}")
    print("="*50)
    
    for i, art in enumerate(articles, 1):
        print(f"\n{i}. {art['title']}")
        print(f"   Published: {art['published']}")
        print(f"   Link: {art['link']}")


def fetch_and_print():
    articles = fetch_rss("https://www.daijiworld.com/rssfeed/rssfeed.xml")
    filtered_articles = []
    for entry in articles:
        if any(keyword in entry["title"] for keyword in ["Udupi", "Mangaluru", "Kundapura", "Brahmavara"]):
            filtered_articles.append(entry)
    print_articles("Daijiworld", filtered_articles)
    feeds = {
        "Karnataka News (The Hindu)": "https://www.thehindu.com/news/national/karnataka/feeder/default.rss",
        "National News (The Hindu)": "https://www.thehindu.com/news/national/feeder/default.rss",
        "International News (The Hindu)": "https://www.thehindu.com/news/international/feeder/default.rss"
    }

    for name, url in feeds.items():
        articles = fetch_rss(url)
        print_articles(name, articles[:10])


def group_articles_by_date(articles):
    """Groups articles by published date in DD-MMM-YYYY format."""
    if not articles:
        return {}

    grouped = {}

    for article in articles:
        date_str = article.get("published", "").strip()

        try:
            # Automatically parse almost any date format
            date_obj = parser.parse(date_str)

            # Convert to required format
            date_key = date_obj.strftime("%d-%b-%Y").upper()

        except (ValueError, TypeError):
            date_key = "UNKNOWN DATE"

        grouped.setdefault(date_key, []).append(article)

    return grouped


@app.route("/")
def home():
    local_feeds = {
        "Daiji World": "https://www.daijiworld.com/rssfeed/rssfeed.xml",
        "The Hindu": "https://www.thehindu.com/news/cities/Mangalore/feeder/default.rss"
    }
    all_articles = []
    for name, url in local_feeds.items():
        articles = fetch_rss(url)
        all_articles.extend(articles)

    filters = ["Udupi", "Mangaluru", "Kundapura", "Brahmavara"]
    filtered_articles = []
    for entry in all_articles:
        if any(keyword in entry.get("title", "") for keyword in filters):
            filtered_articles.append(entry)

    feeds = {
        "Karnataka News (The Hindu)": "https://www.thehindu.com/news/national/karnataka/feeder/default.rss",
        "National News (The Hindu)": "https://www.thehindu.com/news/national/feeder/default.rss",
        "International News (The Hindu)": "https://www.thehindu.com/news/international/feeder/default.rss"
    }

    top_articles = []
    for name, url in feeds.items():
        articles = fetch_rss(url)
        top_articles.append(articles[:100])

    # Filter top_articles lists to remove articles already present in filtered_articles,
    # and ensure cross-feed exclusivity.
    local_links = {entry["link"] for entry in filtered_articles}

    # State articles must not be in local feed
    state_articles = [art for art in top_articles[0] if art["link"] not in local_links]
    state_links = {art["link"] for art in state_articles}

    # National articles must not be in local OR state feeds
    all_state_and_local_links = local_links.union(state_links)
    national_articles = [art for art in top_articles[1] if art["link"] not in all_state_and_local_links]
    national_links = {art["link"] for art in national_articles}

    # International articles must not be in local, state, OR national feeds
    all_previous_links = local_links.union(state_links).union(national_links)
    international_articles = [art for art in top_articles[2] if art["link"] not in all_previous_links]

    # Grouping articles by date
    local_grouped = group_articles_by_date(filtered_articles)
    state_grouped = group_articles_by_date(state_articles)
    national_grouped = group_articles_by_date(national_articles)
    international_grouped = group_articles_by_date(international_articles)

    return render_template("index.html", local=local_grouped, state=state_grouped, national=national_grouped,
                           international=international_grouped)



def main():
    # fetch_and_print()
    app.run(debug=True)

if __name__ == "__main__":
    main()