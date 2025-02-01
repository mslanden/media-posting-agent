import os
from agent_wrapper.base_agent import AgentWrapper

class NoteAgent:
    def __init__(self, framework="openai", api_key=None):
        self.agent_wrapper = AgentWrapper(framework, api_key)
        self.meta_prompt = self.load_prompt("meta_prompts/note_prompt.xml")

    def load_prompt(self, filepath):
        """Load the meta prompt from the specified XML file."""
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                prompt = file.read()
            return prompt
        except Exception as e:
            print(f"Error loading meta prompt from {filepath}: {e}")
            return ""

    def generate_note(self, scraped_data, image_path=None):
        # Start with the meta prompt loaded from file
        prompt = self.meta_prompt

        # Append additional context from scraped data if available
        if scraped_data and len(scraped_data) > 0:
            prompt += f"\nBased on the following scraped web page: {scraped_data}\n"

        # Generate the note using the agent wrapper
        note = self.agent_wrapper.run(prompt, image_path)
        return note

    def save_note(self, note, post_date=None, post_time=None):
        try:
            post = {
                "note": note,
                "post_date": post_date,
                "post_time": post_time
            }
            from post_history import save_post
            save_post(post)
            return True
        except Exception as e:
            print(f"Error saving note: {e}")
            return False
