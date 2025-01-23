#!/usr/bin/env python3
import sys
import os
from tools.tweet_tool import post_tweet
from settings import load_settings
import os

if __name__ == "__main__":
    settings = load_settings()
    os.environ["TWITTER_API_KEY"] = settings.get("twitter_api_key", "")
    os.environ["TWITTER_API_SECRET"] = settings.get("twitter_api_secret", "")
    os.environ["TWITTER_ACCESS_TOKEN"] = settings.get("twitter_access_token", "")
    os.environ["TWITTER_ACCESS_TOKEN_SECRET"] = settings.get("twitter_access_token_secret", "")
    if len(sys.argv) < 2:
        print("Usage: python test_tweet_cli.py \"Your tweet text\" [image_path]")
        sys.exit(1)

    tweet_text = sys.argv[1]
    image_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = post_tweet(tweet_text, image_path)
    print(result)
