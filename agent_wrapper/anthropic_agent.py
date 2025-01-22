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
            if response.status_code != 200:
                print(f"Anthropic API Error: {response.status_code}")
                print(f"Response content: {response.text}")
                return f"Error: Anthropic API returned status code {response.status_code}"
            return response.json().get("completion", "No response")
        except Exception as e:
            return f"Error: {str(e)}"
