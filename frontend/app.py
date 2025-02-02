import sys
import os
import uuid
import atexit
from datetime import datetime, timedelta

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your modules and agents
from scraper import Scraper, save_markdown
from agents.tweet_agent import TweetAgent
from agents.linkedin_agent import LinkedInAgent
from agents.article_agent import ArticleAgent
from agents.newsletter_agent import NewsletterAgent
from agents.note_agent import NoteAgent
from settings import save_settings, load_settings
from post_history import save_post, load_posts, update_post, delete_post
from tools.tweet_tool import post_tweet
from tools.linkedin_tool import post_to_linkedin

app = Flask(__name__)
load_dotenv()

load_scheduled = False  # Load scheduled posts by default

scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())  # Ensure scheduler shuts down when app exits


def schedule_post(post_id, post_date, post_time, content, media_type, image_path=None):
    """
    Schedule a post using both post_date (YYYY-MM-DD) and post_time (HH:MM).
    If post_date is not provided, today's date will be used.
    """
    scheduled_datetime = None
    try:
        if post_date and post_time:
            scheduled_datetime = datetime.strptime(f"{post_date} {post_time}", "%Y-%m-%d %H:%M")
        elif post_time:
            scheduled_datetime = datetime.combine(datetime.now().date(), datetime.strptime(post_time, "%H:%M").time())
            if scheduled_datetime < datetime.now():
                scheduled_datetime += timedelta(days=1)  # Schedule for tomorrow if time has passed
        else:
            scheduled_datetime = datetime.now()
    except Exception as e:
        print(f"Error parsing date/time: {e}")
        scheduled_datetime = datetime.now()

    scheduler.add_job(
        post_content,
        'date',
        run_date=scheduled_datetime,
        args=[content, media_type, image_path],
        id=post_id
    )
    print(f"Scheduled post {post_id} for {scheduled_datetime}")


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
    """
    This route accepts content from either request_data (for testing) or Flask's request.
    It generates content using a NoteAgent when a URL is provided and passes the note
    to the appropriate agent (tweet, linkedin, article, newsletter).
    """
    # Use provided test data or the actual Flask request
    if request_data is None:
        data = request.form
        files = request.files
    else:
        data = request_data.get('form', {})
        files = request_data.get('files', {})

    # Extract common parameters
    message = data.get("message")
    url = data.get("url")
    media_type = data.get("mediaType")
    post_date = data.get("postDate")  # Expected format: YYYY-MM-DD
    post_time = data.get("postTime")  # Expected format: HH:MM
    image = files.get("image")

    settings = load_settings()
    api_key = settings.get("api_key")
    llm_model = settings.get("llm_model")

    if not api_key:
        return jsonify({"error": "No API key provided"}), 400
    if not llm_model:
        return jsonify({"error": "No LLM model provided"}), 400

    # If URL is provided, scrape its content
    scraped_data = ""
    image_path = None
    if url:
        scraper = Scraper()
        markdown_content, status = scraper.scrape(url)
        if status != 200:
            return jsonify({"error": markdown_content}), 500
        scraped_data = markdown_content

    # Handle image file upload (if provided)
    if image:
        images_dir = os.path.join("frontend", "static", "images")
        os.makedirs(images_dir, exist_ok=True)
        image_filename = f"image_{uuid.uuid4()}.{image.filename.split('.')[-1]}"
        image_path = os.path.join(images_dir, image_filename)
        image.save(image_path)
        image_path = os.path.relpath(image_path, ".")

    # Generate note content using the NoteAgent if URL is provided,
    # otherwise use the user's message.
    note_agent = NoteAgent(framework=llm_model, api_key=api_key)
    if url:
        try:
            note_content = note_agent.generate_note(scraped_data)
        except Exception as e:
            return jsonify({"error": f"Failed to generate note: {str(e)}"}), 500
    else:
        note_content = message

    # Pass the note_content (and optionally the message) to the appropriate agent.
    try:
        if media_type == "tweet":
            tweet_agent = TweetAgent(framework=llm_model, api_key=api_key)
            content = tweet_agent.generate_tweet(note_content, image_path=image_path)
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
    except Exception as e:
        return jsonify({"error": f"Error generating content: {str(e)}"}), 500

    # Build the post dictionary
    post = {
        "id": str(uuid.uuid4()),
        "content": content,
        "post_date": post_date,
        "post_time": post_time,
        "media_type": media_type,
        "image_path": image_path
    }

    if save_post(post):
        schedule_post(post['id'], post_date, post_time, post['content'], post['media_type'], post.get('image_path'))
        return jsonify({"message": content}), 200
    else:
        return jsonify({"error": "Failed to save post"}), 500


@app.route("/save_settings", methods=["POST"])
def save_settings_route():
    data = request.get_json()
    # Only update the settings exposed to the UI.
    llm_model = data.get("llm_model")
    dark_mode = data.get("dark_mode")

    if llm_model is None:
        return jsonify({"error": "No LLM model provided"}), 400
    if dark_mode is None:
        return jsonify({"error": "No dark mode setting provided"}), 400

    # Load the current settings from the JSON file.
    current_settings = load_settings()
    current_settings["llm_model"] = llm_model
    current_settings["dark_mode"] = dark_mode

    if save_settings(current_settings):
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
        posts = load_posts()
        post = next((item for item in posts if item["id"] == post_id), None)
        if post:
            try:
                scheduler.remove_job(post_id)
            except Exception as e:
                print(f"Error removing scheduled job: {e}")
            schedule_post(post['id'], post.get('post_date'), post['post_time'], post['content'], post['media_type'], post.get('image_path'))
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
