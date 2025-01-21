import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, jsonify
from utils import scrape_and_format_url, save_markdown_file
from agents.tweet_agent import TweetAgent

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

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

@app.route("/generate", methods=["POST"])
def generate_content():
    message = request.form.get("message")
    url = request.form.get("url")
    media_type = request.form.get("mediaType")
    api_key = request.form.get("api_key")
    llm_model = request.form.get("llm_model")

    if not message:
        return jsonify({"error": "No message provided"}), 400

    scraped_data = ""
    if url:
        scraped_data = scrape_and_format_url(url)
        if "Error" in scraped_
            return jsonify({"error": scraped_data}), 500

    if not api_key:
        return jsonify({"error": "No API key provided"}), 400

    if media_type == "tweet":
        tweet_agent = TweetAgent(framework=llm_model, api_key=api_key)
        tweet = tweet_agent.generate_tweet(scraped_data, message)
        if tweet_agent.save_tweet(tweet):
            return jsonify({"message": tweet}), 200
        else:
            return jsonify({"error": "Failed to save tweet"}), 500
    else:
        return jsonify({"error": "Unsupported media type"}), 400

if __name__ == "__main__":
    app.run(debug=True)
