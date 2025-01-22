import os
from agent_wrapper.base_agent import AgentWrapper

class TweetAgent:
    def __init__(self, framework="openai", api_key=None):
        self.agent_wrapper = AgentWrapper(framework, api_key)

    def generate_tweet(self, scraped_data, user_comments, image_path=None):
        prompt = f"""
        You are an expert tweet writer.
        """
        if scraped_data and len(scraped_data) > 0:
            prompt += f"Based on the following scraped web page: {scraped_data}\n"
        prompt += f"And the following user comments: {user_comments}\n"
        if image_path:
            prompt += f"Also, use the information from this image: {image_path}\n"
        prompt += "Generate a tweet."
        tweet = self.agent_wrapper.run(prompt, image_path)
        return tweet

    def save_tweet(self, tweet, post_date=None, post_time=None):
        try:
            post = {
                "tweet": tweet,
                "post_date": post_date,
                "post_time": post_time
            }
            from post_history import save_post
            save_post(post)
            return True
        except Exception as e:
            print(f"Error saving tweet: {e}")
            return False
