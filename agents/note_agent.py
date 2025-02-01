import os
from agent_wrapper.base_agent import AgentWrapper

class NoteAgent:
    def __init__(self, framework="openai", api_key=None):
        self.agent_wrapper = AgentWrapper(framework, api_key)

    def generate_note(self, meta_prompt, scraped_data, image_path=None):
        prompt = f"""
        {meta_prompt}
        """
        if scraped_data and len(scraped_data) > 0:
            prompt += f"Based on the following scraped web page: {scraped_data}\n"
        if image_path:
            prompt += f"Also, use the information from this image: {image_path}\n"
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
