import sys
import os
from tools.tweet_tool import post_tweet

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_tweet_cli.py \"Your tweet text\" [image_path]")
        sys.exit(1)

    tweet_text = sys.argv[1]
    image_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = post_tweet(tweet_text, image_path)
    print(result)
