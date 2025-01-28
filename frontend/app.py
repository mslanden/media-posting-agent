import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, jsonify
from scraper import Scraper, save_markdown
from agents.tweet_agent import TweetAgent
from agents.linkedin_agent import LinkedInAgent
from agents.article_agent import ArticleAgent
from agents.newsletter_agent import NewsletterAgent
import os
from dotenv import load_dotenv
from settings import save_settings, load_settings
from post_history import save_post, load_posts, update_post, delete_post
import uuid
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from tools.tweet_tool import post_tweet
from tools.linkedin_tool import post_to_linkedin

app = Flask(__name__)
load_dotenv()

load_scheduled = False  # Load scheduled posts by default

scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def update_env_variables(settings):
    os.environ["API_KEY"] = settings.get("api_key", "")
    os.environ["TWITTER_API_KEY"] = settings.get("twitter_api_key", "")
    os.environ["TWITTER_API_SECRET"] = settings.get("twitter_api_secret", "")
    os.environ["TWITTER_ACCESS_TOKEN"] = settings.get("twitter_access_token", "")
    os.environ["TWITTER_ACCESS_TOKEN_SECRET"] = settings.get("twitter_access_token_secret", "")
    os.environ["LINKEDIN_CLIENT_ID"] = settings.get("linkedin_client_id", "")
    os.environ["LINKEDIN_CLIENT_SECRET"] = settings.get("linkedin_client_secret", "")
    os.environ["LINKEDIN_ACCESS_TOKEN"] = settings.get("linkedin_access_token", "")

def schedule_post(post_id, post_time, content, media_type, image_path=None):
    if post_time:
        post_datetime = datetime.combine(datetime.now().date(), datetime.strptime(post_time, "%H:%M").time())
        if post_datetime < datetime.now():
            post_datetime += timedelta(days=1)
        scheduler.add_job(
            post_content,
            'date',
            run_date=post_datetime,
            args=[content, media_type, image_path],
            id=post_id
        )

def post_content(content, media_type, image_path=None):
    try:
        if media_type == "tweet":
            print(f"Attempting to post tweet: {content}")
            print(f"Image path: {image_path}")
            result = post_tweet(content, [image_path] if image_path else None)
            if "Error" in result:
                print(f"Tweet posting error: {result}")
        elif media_type == "linkedin":
            result = post_to_linkedin(content, image_path)
        else:
            result = f"Unsupported media type for posting: {media_type}"
        print(f"Posting result: {result}")
    except Exception as e:
        print(f"Unexpected error in post_content: {e}")

@app.route("/")
def home():
    settings = load_settings()
    return render_template("index.html", settings=settings)

@app.route("/scrape", methods=["POST"])
def scrape_url():
    url = request.form.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    scraper = Scraper()
    markdown_content, status = scraper.scrape(url)
    if status != 200:
        return jsonify({"error": f"Failed to scrape URL: {status}"}), 500

    filename = f"output/{url.split('//')[1].replace('/', '_')}.md"
    if save_markdown(markdown_content, filename):
        return jsonify({"message": "Web data scraped and saved successfully"}), 200
    else:
        return jsonify({"error": "Failed to save web data"}), 500

@app.route("/generate", methods=["POST"])
def generate_content():
    message = request.form.get("message")
    url = request.form.get("url")
    media_type = request.form.get("mediaType")
    image = request.files.get("image")
    settings = load_settings()
    api_key = settings.get("api_key")
    llm_model = settings.get("llm_model")

    if not api_key:
        return jsonify({"error": "No API key provided"}), 400
    if not llm_model:
        return jsonify({"error": "No LLM model provided"}), 400

    scraped_data = ""
    if url:
        # Use the Scraper class instead of undefined function
        scraper = Scraper()
        markdown_content, status = scraper.scrape(url)
        if status != 200:
            return jsonify({"error": markdown_content}), 500
        scraped_data = markdown_content

    post_date = request.form.get("postDate")
    post_time = request.form.get("postTime")
    image_path = None

    if image:
        images_dir = os.path.join("frontend", "static", "images")
        os.makedirs(images_dir, exist_ok=True)
        image_filename = f"image_{uuid.uuid4()}.{image.filename.split('.')[-1]}"
        image_path = os.path.join(images_dir, image_filename)
        image.save(image_path)
        image_path = os.path.relpath(image_path, ".")

    if media_type == "tweet":
        tweet_agent = TweetAgent(framework=llm_model, api_key=api_key)
        content = tweet_agent.generate_tweet(scraped_data, message, image_path)
    elif media_type == "linkedin":
        linkedin_agent = LinkedInAgent(framework=llm_model, api_key=api_key)
        content = linkedin_agent.generate_linkedin_post(scraped_data, message, image_path)
    elif media_type == "article":
        article_agent = ArticleAgent(framework=llm_model, api_key=api_key)
        content = article_agent.generate_article(scraped_data, message, image_path)
    elif media_type == "newsletter":
        newsletter_agent = NewsletterAgent(framework=llm_model, api_key=api_key)
        content = newsletter_agent.generate_newsletter(scraped_data, message, image_path)
    else:
        return jsonify({"error": "Unsupported media type"}), 400

    post = {
        "id": str(uuid.uuid4()),
        "content": content,
        "post_date": post_date,
        "post_time": post_time,
        "media_type": media_type,
        "image_path": image_path
    }

    if save_post(post):
        schedule_post(post['id'], post['post_time'], post['content'], post['media_type'], post.get('image_path'))
        return jsonify({"message": content}), 200
    else:
        return jsonify({"error": "Failed to save post"}), 500

# ... [Keep the rest of the routes the same as in your original code] ...

if __name__ == "__main__":
    app.run(debug=True)
