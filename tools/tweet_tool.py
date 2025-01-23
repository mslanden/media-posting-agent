import tweepy
import os

def post_tweet(tweet_text):
    # Replace with your actual API keys and secrets
    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

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
