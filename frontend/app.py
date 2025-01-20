import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent_wrapper import base_agent
from flask import Flask, request, render_template, jsonify
import json

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/task", methods=["POST"])
def handle_task():
    data = request.json
    task = data.get("task")
    agent_type = data.get("agent", "openai")  # Default to OpenAI if no agent specified
    with open("api_keys.json", "r") as f:
        api_keys = json.load(f)
    agent = base_agent.AgentWrapper(agent_type)
    if agent_type == "anthropic":
        agent.agent.api_key = api_keys.get("anthropic")
    elif agent_type == "gemini":
        agent.agent.api_key = api_keys.get("gemini")
    elif agent_type == "openai":
        openai.api_key = api_keys.get("openai")
    response = agent.run(task)
    return jsonify({"message": response})

@app.route("/api/scheduled", methods=["GET"])
def get_scheduled():
    scheduled_posts = [
        {"platform": "Twitter", "content": "AI news tweet example", "time": "2025-01-18T10:00:00Z"},
        {"platform": "LinkedIn", "content": "LinkedIn post example", "time": "2025-01-18T12:00:00Z"}
    ]
    return jsonify(scheduled_posts)

@app.route("/api/keys", methods=["POST"])
def set_api_keys():
    data = request.json
    keys = data.get("keys")
    with open("api_keys.json", "w") as f:
        json.dump(keys, f)
    return jsonify({"message": "API keys updated successfully!"})

@app.route("/api/keys", methods=["GET"])
def get_api_keys():
    try:
        with open("api_keys.json", "r") as f:
            keys = json.load(f)
        return jsonify(keys)
    except FileNotFoundError:
        return jsonify({}), 404

if __name__ == "__main__":
    app.run(debug=True)
