#!/usr/bin/env python3
"""
TrustLens — Standalone Reddit Marketplace Complaint Scraper.
Collects public user complaint posts and scam reports from Indian subreddits
to ground empirical marketplace fraud taxonomies.

Usage:
    python scripts/scrape_reddit_complaints.py --query "olx scam" --limit 50 --output data/reddit_scraped.json
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List
import urllib.request
import urllib.parse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("trustlens.reddit_scraper")

DEFAULT_SUBREDDITS = [
    "IsThisAScamIndia",
    "LegalAdviceIndia",
    "delhi",
    "bangalore",
    "mumbai",
    "india",
    "IndianCyberHub",
    "ps5india",
]

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 TrustLens/1.0 (Research)"


def fetch_subreddit_search(
    subreddit: str, query: str, limit: int = 25, after: str = None
) -> Dict[str, Any]:
    """Fetch search results from Reddit's public JSON API."""
    params = {
        "q": query,
        "sort": "new",
        "restrict_sr": "1",
        "limit": str(min(limit, 100)),
    }
    if after:
        params["after"] = after

    encoded_params = urllib.parse.urlencode(params)
    url = f"https://www.reddit.com/r/{subreddit}/search.json?{encoded_params}"

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("data", {})
    except Exception as e:
        logger.warning(f"Failed to fetch r/{subreddit} with query '{query}': {e}")
    return {}


def scrape_reddit_complaints(
    subreddits: List[str], query: str = "olx scam", max_per_sub: int = 25
) -> List[Dict[str, Any]]:
    """Scrape and structure complaint posts across specified subreddits."""
    posts: List[Dict[str, Any]] = []
    seen_ids = set()

    for sub in subreddits:
        logger.info(f"Searching r/{sub} for '{query}'...")
        data = fetch_subreddit_search(sub, query, limit=max_per_sub)
        children = data.get("children", [])

        for child in children:
            post_data = child.get("data", {})
            post_id = post_data.get("id")
            if not post_id or post_id in seen_ids:
                continue

            seen_ids.add(post_id)
            cleaned_record = {
                "id": post_id,
                "title": post_data.get("title", ""),
                "selftext": post_data.get("selftext", ""),
                "subreddit": post_data.get("subreddit", sub),
                "author": post_data.get("author", "[deleted]"),
                "score": post_data.get("score", 0),
                "num_comments": post_data.get("num_comments", 0),
                "url": post_data.get("url", ""),
                "permalink": f"https://reddit.com{post_data.get('permalink', '')}",
                "created_utc": post_data.get("created_utc", 0),
                "is_video": post_data.get("is_video", False),
                "media_metadata": list(post_data.get("media_metadata", {}).keys()),
            }
            posts.append(cleaned_record)

        # Respectful rate-limiting between subreddit requests
        time.sleep(1.5)

    logger.info(f"Total unique posts collected: {len(posts)}")
    return posts


def main():
    parser = argparse.ArgumentParser(description="TrustLens Reddit Marketplace Complaint Scraper")
    parser.add_argument("--query", default="olx scam", help="Search query (e.g. 'olx scam', 'army olx')")
    parser.add_argument("--subreddits", nargs="+", default=DEFAULT_SUBREDDITS, help="Subreddits to search")
    parser.add_argument("--limit-per-sub", type=int, default=25, help="Max posts per subreddit")
    parser.add_argument("--output", type=str, default="data/reddit_complaints_scraped.json", help="Output JSON path")
    args = parser.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    posts = scrape_reddit_complaints(args.subreddits, args.query, args.limit_per_sub)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(posts)} complaint records to {out_path}")


if __name__ == "__main__":
    main()
