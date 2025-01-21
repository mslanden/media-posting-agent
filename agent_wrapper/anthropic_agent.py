import requests

class AnthropicAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def run(self, prompt, image_path=None):
        try:
            if image_path:
                prompt += f" Also, use the information from this image: {image_path}"
            response = requests.post(
                "https://api.anthropic.com/completion",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "prompt": prompt,
                    "max_tokens": 100,
                },
            )
            response.raise_for_status()
            return response.json().get("completion", "No response")
        except Exception as e:
            return f"Error: {str(e)}"
