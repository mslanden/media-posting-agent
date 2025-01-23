import tweepy
import os
from settings import load_settings


def post_tweet(tweet_text):
    settings = load_settings()
    api_key = settings.get("twitter_api_key")
    api_secret = settings.get("twitter_api_secret")
    access_token = settings.get("twitter_access_token")
    access_token_secret = settings.get("twitter_access_token_secret")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        return "Error: Missing Twitter API credentials. Please configure them in settings."

    try:
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        api.update_status(status=tweet_text)
        return "Tweet posted successfully!"
    except Exception as e:
        return f"Error posting tweet: {e}"
