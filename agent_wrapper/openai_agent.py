import openai
import os

class OpenAIAgent:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def run(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"
