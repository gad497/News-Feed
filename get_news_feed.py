from flask import Flask, render_template
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
        top_articles.append(articles[:10])

    return render_template("index.html", local=filtered_articles, state=top_articles[0], national=top_articles[1],
                           international=top_articles[2])



def main():
    # fetch_and_print()
    app.run(debug=True)

if __name__ == "__main__":
    main()