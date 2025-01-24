import tweepy
from settings import load_settings

def post_tweet(tweet_text, media_paths=None):
    settings = load_settings()
    bearer_token = settings.get("twitter_bearer_token")
    consumer_key = settings.get("twitter_api_key")
    consumer_secret = settings.get("twitter_api_secret")
    access_token = settings.get("twitter_access_token")
    access_token_secret = settings.get("twitter_access_token_secret")

    if not bearer_token or not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        return "Error: Missing Twitter API credentials. Please configure them in settings."

    try:
        # Authenticate
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # Create V1.1 API for media upload
        v1_api = tweepy.API(auth)

        # Create V2 Client
        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        # Upload media files
        media_ids = []
        if media_paths:
            for media_path in media_paths:
                full_media_path = os.path.join("frontend", media_path)
                uploaded_media = v1_api.media_upload(full_media_path)
                media_ids.append(uploaded_media.media_id)

        # Post tweet with media
        if media_ids:
            response = client.create_tweet(text=tweet_text, media_ids=media_ids)
        else:
            response = client.create_tweet(text=tweet_text)

        return f"Tweet posted successfully! Tweet ID: {response.data['id']}"

    except Exception as e:
        return f"Error posting tweet: {e}"
