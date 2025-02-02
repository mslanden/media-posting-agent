import requests

class AnthropicAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def run(self, prompt, image_path=None):
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2024-01-01",  # Updated version header
                "content-type": "application/json"
            }

            payload = {
                "model": "claude-3-sonnet-20240229",  # Updated model name
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }

            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload
            )

            # More detailed error handling
            if response.status_code != 200:
                error_content = response.json() if response.content else "No error content"
                print(f"Anthropic API Error: {response.status_code}")
                print(f"Response content: {error_content}")
                return f"Error: Anthropic API returned status code {response.status_code}\nDetails: {error_content}"

            result = response.json()
            return result['content'][0]['text']

        except requests.exceptions.RequestException as e:
            return f"Network Error: {str(e)}"
        except ValueError as e:
            return f"JSON Parsing Error: {str(e)}"
        except Exception as e:
            return f"Unexpected Error: {str(e)}"
