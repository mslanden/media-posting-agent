import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, jsonify
from scraper import Scraper, save_markdown
from agents.tweet_agent import TweetAgent
from agents.linkedin_agent import LinkedInAgent
from agents.article_agent import ArticleAgent
from agents.newsletter_agent import NewsletterAgent
from agents.note_agent import NoteAgent
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
atexit.register(lambda: scheduler.shutdown()) # Ensure scheduler shuts down when app exits


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
            post_datetime += timedelta(days=1) # Schedule for tomorrow if time has already passed
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
def generate_content(request_data=None):
    if request_data:
        message = request_data['form'].get("message")
        url = request_data['form'].get("url")
        media_type = request_data['form'].get("mediaType")
        image = request_data['files'].get("image")
        settings = load_settings()
        api_key = settings.get("api_key")
        llm_model = settings.get("llm_model")
    else:
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
        scraper = Scraper()
        markdown_content, status = scraper.scrape(url)
        if status != 200:
            return jsonify({"error": markdown_content}), 500
        scraped_data = markdown_content
    if request_data:
        post_date = request_data['form'].get("postDate")
        post_time = request_data['form'].get("postTime")
        image_path = None
        if image:
            images_dir = os.path.join("frontend", "static", "images")
            os.makedirs(images_dir, exist_ok=True)
            image_filename = f"image_{uuid.uuid4()}.{image.filename.split('.')[-1]}"
            image_path = os.path.join(images_dir, image_filename)
            image.save(image_path)
            image_path = os.path.relpath(image_path, ".")
    else:
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
        content = tweet_agent.generate_tweet(note_content, message, image_path)
    elif media_type == "linkedin":
        linkedin_agent = LinkedInAgent(framework=llm_model, api_key=api_key)
        content = linkedin_agent.generate_linkedin_post(note_content, message, image_path)
    elif media_type == "article":
        article_agent = ArticleAgent(framework=llm_model, api_key=api_key)
        content = article_agent.generate_article(note_content, message, image_path)
    elif media_type == "newsletter":
        newsletter_agent = NewsletterAgent(framework=llm_model, api_key=api_key)
        content = newsletter_agent.generate_newsletter(note_content, message, image_path)
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

@app.route("/save_settings", methods=["POST"])
def save_settings_route():
    data = request.get_json()
    api_key = data.get("api_key")
    llm_model = data.get("llm_model")
    dark_mode = data.get("dark_mode")

    twitter_api_key = data.get("twitter_api_key")
    twitter_api_secret = data.get("twitter_api_secret")
    twitter_access_token = data.get("twitter_access_token")
    twitter_access_token_secret = data.get("twitter_access_token_secret")

    linkedin_client_id = data.get("linkedin_client_id")
    linkedin_client_secret = data.get("linkedin_client_secret")
    linkedin_access_token = data.get("linkedin_access_token")
    linkedin_username = data.get("linkedin_username")
    linkedin_password = data.get("linkedin_password")
    twitter_bearer_token = data.get("twitter_bearer_token")


    if not api_key:
        return jsonify({"error": "No API key provided"}), 400
    if not llm_model:
        return jsonify({"error": "No LLM model provided"}), 400
    if dark_mode is None:
        return jsonify({"error": "No dark mode provided"}), 400

    settings = {
        "api_key": api_key,
        "llm_model": llm_model,
        "dark_mode": dark_mode,
        "twitter_api_key": twitter_api_key,
        "twitter_api_secret": twitter_api_secret,
        "twitter_access_token": twitter_access_token,
        "twitter_access_token_secret": twitter_access_token_secret,
        "linkedin_client_id": linkedin_client_id,
        "linkedin_client_secret": linkedin_client_secret,
        "linkedin_access_token": linkedin_access_token,
        "linkedin_username": linkedin_username,
        "linkedin_password": linkedin_password,
        "twitter_bearer_token": twitter_bearer_token
    }
    if save_settings(settings):
        return jsonify({"message": "Settings saved successfully!"}), 200
    else:
        return jsonify({"error": "Failed to save settings"}), 500

@app.route("/get_posts", methods=["GET"])
def get_posts():
    posts = load_posts()
    return jsonify(posts), 200

@app.route("/update_post", methods=["POST"])
def update_post_route():
    data = request.get_json()
    post_id = data.get("id")
    updated_post = data.get("updated_post")
    if not post_id:
        return jsonify({"error": "No post ID provided"}), 400
    if not updated_post:
        return jsonify({"error": "No updated post data provided"}), 400
    if update_post(post_id, updated_post):
        post = load_posts()
        post = next((item for item in post if item["id"] == post_id), None)
        if post:
            try:
                scheduler.remove_job(post_id)
            except Exception as e:
                print(f"Error removing scheduled job: {e}")
            schedule_post(post['id'], post['post_time'], post['content'], post['media_type'], post.get('image_path'))
        return jsonify({"message": "Post updated successfully"}), 200
    else:
        return jsonify({"error": "Failed to update post"}), 500


@app.route("/delete_post", methods=["POST"])
def delete_post_route():
    data = request.get_json()
    post_id = data.get("id")
    if not post_id:
        return jsonify({"error": "No post ID provided"}), 400
    if delete_post(post_id):
        try:
            scheduler.remove_job(post_id)
        except Exception as e:
            print(f"Error removing scheduled job: {e}")
        return jsonify({"message": "Post deleted successfully"}), 200
    else:
        return jsonify({"error": "Failed to delete post"}), 500

@app.route("/settings", methods=["GET"])
def settings():
    settings = load_settings()
    return render_template("settings.html", settings=settings)

@app.route("/scheduled_posts", methods=["GET"])
def scheduled_posts():
    settings = load_settings()
    return render_template("scheduled_posts.html", settings=settings)

if __name__ == "__main__":
    app.run(debug=True)
