# insights/utils.py

def analyze_website(url):
    # Dummy placeholder: replace with your actual analyze logic
    # e.g., scrape the website, analyze content, return summary or categories
    return {
        "url": url,
        "description": (
            "This website focuses on cutting-edge technology, "
            "software engineering, and developer tools. "
            "It features in-depth tutorials, industry news, "
            "and product reviews aimed at both beginners and professionals."
        ),
        "keywords": [
            "technology", "programming", "software development", "AI", "machine learning",
            "developer tools", "coding tutorials", "tech news"
        ]
    }


def fetch_reddit_data(query):
    # Dummy placeholder: replace with your actual reddit scraping/API logic
    # e.g., search subreddits and posts matching the query and return results
    return {
        "query": query,
        "subreddits": [
            "r/learnprogramming",
            "r/python",
            "r/coding",
            "r/developers",
            "r/artificial"
        ],
        "top_posts": [
            {
                "title": "How to learn Python efficiently in 2025?",
                "url": "https://reddit.com/r/learnprogramming/comments/abc123"
            },
            {
                "title": "Best programming tutorials and free resources",
                "url": "https://reddit.com/r/python/comments/def456"
            },
            {
                "title": "What are the most underrated Python tricks?",
                "url": "https://reddit.com/r/coding/comments/ghi789"
            }
        ]
    }
