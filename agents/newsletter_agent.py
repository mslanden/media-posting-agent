import os
from agent_wrapper.base_agent import AgentWrapper

class NewsletterAgent:
    def __init__(self, framework="openai", api_key=None):
        self.agent_wrapper = AgentWrapper(framework, api_key)

    def generate_newsletter(self, scraped_data, user_comments, image_path=None):
        prompt = f"""
        You are an expert newsletter writer.
        """
        if scraped_data and len(scraped_data) > 0:
            prompt += f"Based on the following scraped web page: {scraped_data}\n"
        prompt += f"And the following user comments: {user_comments}\n"
        if image_path:
            prompt += f"Also, use the information from this image: {image_path}\n"
        prompt += "Generate a newsletter."
        newsletter = self.agent_wrapper.run(prompt, image_path)
        return newsletter

    def save_newsletter(self, newsletter, post_date=None, post_time=None):
        try:
            post = {
                "newsletter": newsletter,
                "post_date": post_date,
                "post_time": post_time
            }
            from post_history import save_post
            save_post(post)
            return True
        except Exception as e:
            print(f"Error saving newsletter: {e}")
            return False
