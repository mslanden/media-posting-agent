import requests
import json

class GeminiAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    def run(self, prompt):
        try:
            response = requests.post(
                self.url,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                },
                json={
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "maxOutputTokens": 2048
                    }
                }
            )
            response.raise_for_status()
            return response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response")
        except Exception as e:
            return f"Error: {str(e)}"
