import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

def post_tweet(tweet_text, media_paths=None):
    consumer_key = os.getenv("TWITTER_API_KEY")
    consumer_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        return "Error: Missing Twitter API credentials. Please configure them in settings."

    try:
        # Authenticate
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # Create V1.1 API for media upload
        v1_api = tweepy.API(auth)

        # Create V2 Client with more verbose authentication
        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            bearer_token=bearer_token
        )

        # Upload media files
        media_ids = []
        if media_paths:
            for media_path in media_paths:
                full_media_path = os.path.join(".", media_path)
                if not os.path.exists(full_media_path):
                    print(f"Warning: Media file not found - {full_media_path}")
                    continue
                uploaded_media = v1_api.media_upload(full_media_path)
                media_ids.append(uploaded_media.media_id)

        # Check if any media was uploaded
        if media_paths and not media_ids:
            return "Error: No valid media files found."

        # Post tweet with media
        if media_ids:
            response = client.create_tweet(text=tweet_text, media_ids=media_ids)
        else:
            response = client.create_tweet(text=tweet_text)

        return f"Tweet posted successfully! Tweet ID: {response.data['id']}"

    except tweepy.TooManyRequests:
        return "Error: Rate limit exceeded. Please wait and try again."
    except tweepy.Unauthorized:
        return "Error: Authentication failed. Check your API credentials."
    except Exception as e:
        return f"Error posting tweet: {type(e).__name__} - {e}"
