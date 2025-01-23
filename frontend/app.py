import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, jsonify
from utils import scrape_and_format_url, save_markdown_file
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
from tools.tweet_tool import post_tweet  # Import your tweet posting function
from tools.linkedin_tool import post_to_linkedin # Import your linkedin posting function


app = Flask(__name__)
load_dotenv()

settings = load_settings()
os.environ["API_KEY"] = settings.get("api_key", "")


scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown()) # Ensure scheduler shuts down when app exits

@app.route("/")
def home():
    settings = load_settings()
    return render_template("index.html", settings=settings)

@app.route("/scrape", methods=["POST"])
def scrape_url():
    url = request.form.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    markdown_content = scrape_and_format_url(url)
    if "Error" in markdown_content:
        return jsonify({"error": markdown_content}), 500

    if save_markdown_file(markdown_content):
        return jsonify({"message": "Web data scraped and saved successfully"}), 200
    else:
        return jsonify({"error": "Failed to save web data"}), 500

import uuid

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
        scraped_data = scrape_and_format_url(url)
        if "Error" in scraped_data:
            return jsonify({"error": scraped_data}), 500

    post_date = request.form.get("postDate")
    post_time = request.form.get("postTime")
    image_path = None
    if image:
        images_dir = os.path.join("frontend", "static", "images")
        os.makedirs(images_dir, exist_ok=True)
        image_filename = f"image_{uuid.uuid4()}.{image.filename.split('.')[-1]}"
        image_path = os.path.join(images_dir, image_filename)
        image.save(image_path)
        image_path = os.path.relpath(image_path, "frontend")

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
        "image_path": image_path,
        "media_type": media_type
    }
    if save_post(post):
        return jsonify({"message": content}), 200
    else:
        return jsonify({"error": "Failed to save post"}), 500

@app.route("/save_settings", methods=["POST"])
def save_settings_route():
    data = request.get_json()
    api_key = data.get("api_key")
    llm_model = data.get("llm_model")
    dark_mode = data.get("dark_mode")
    if not api_key:
        return jsonify({"error": "No API key provided"}), 400
    if not llm_model:
        return jsonify({"error": "No LLM model provided"}), 400
    if dark_mode is None:
        return jsonify({"error": "No dark mode provided"}), 400

    settings = {
        "api_key": api_key,
        "llm_model": llm_model,
        "dark_mode": dark_mode
    }
    if save_settings(settings):
        return jsonify({"message": f"{llm_model} API key saved successfully"}), 200
    else:
        return jsonify({"error": f"Failed to save settings"}), 500

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
            print(f"Error removing scheduled job: {e}") # Job might not exist if it already ran
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
