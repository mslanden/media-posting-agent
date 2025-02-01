import openai

class OpenAIAgent:
    def __init__(self, api_key):
        # Set the API key on the openai module
        openai.api_key = api_key

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
                    "content": f"This is the image path: {image_path}"
                })

            # Call the ChatCompletion endpoint directly
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages
            )

            # Extract and return the assistant's reply
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"
