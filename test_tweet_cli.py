#!/usr/bin/env python3
import sys
import os
from tools.tweet_tool import post_tweet
import sys
import os
from tools.tweet_tool import post_tweet


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_tweet_cli.py \"Your tweet text\")
        sys.exit(1)

    tweet_text = sys.argv[1]

    result = post_tweet(tweet_text)
    print(result)
