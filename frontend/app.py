from flask import Flask, render_template, request, jsonify
from utils import scrape_and_format_url, save_markdown_file

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

if __name__ == "__main__":
    app.run(debug=True)
