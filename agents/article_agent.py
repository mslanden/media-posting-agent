import os
from agent_wrapper.base_agent import AgentWrapper

class ArticleAgent:
    def __init__(self, framework="openai", api_key=None):
        self.agent_wrapper = AgentWrapper(framework, api_key)
        self.meta_prompt = self.load_prompt("meta_prompts/article_prompt.xml")

    def load_prompt(self, filepath):
        """Load the meta prompt from the specified XML file."""
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                prompt = file.read()
            return prompt
        except Exception as e:
            print(f"Error loading meta prompt from {filepath}: {e}")
            # Fallback meta prompt in case of error
            return "You are an expert article writer."

    def generate_article(self, scraped_data, user_comments="", image_path=None):
        # Start with the meta prompt loaded from the file
        prompt = self.meta_prompt

        if scraped_data and len(scraped_data) > 0:
            prompt += f"\nBased on the following scraped web page: {scraped_data}\n"
        if user_comments:
            prompt += f"And the following user comments: {user_comments}\n"
        if image_path:
            prompt += f"Also, use the information from this image: {image_path}\n"
        prompt += "Generate an article."

        article = self.agent_wrapper.run(prompt, image_path)
        return article

    def save_article(self, article, post_date=None, post_time=None):
        try:
            post = {
                "article": article,
                "post_date": post_date,
                "post_time": post_time
            }
            from post_history import save_post
            save_post(post)
            return True
        except Exception as e:
            print(f"Error saving article: {e}")
            return False
