from openai import OpenAI

class DeepSeekAgent:
    def __init__(self, api_key):
        # Initialize the DeepSeek client using the OpenAI client interface.
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    def run(self, prompt, image_path=None):
        try:
            # Build the conversation messages
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            if image_path:
                messages.append({
                    "role": "user",
                    "content": "This is the image path: " + image_path
                })
            # Request a completion using DeepSeek's chat model
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False
            )
            # Return the assistant's reply
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"
