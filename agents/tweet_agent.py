from agent_wrapper.base_agent import AgentWrapper

class TweetAgent:
    def __init__(self, framework="openai", api_key=None):
        self.agent_wrapper = AgentWrapper(framework, api_key)
        self.main_prompt = self.load_prompt("meta_prompts/tweet_prompt.xml")

    def load_prompt(self, filepath):
        """Load the main prompt from the given XML file."""
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                prompt = file.read()
            return prompt
        except Exception as e:
            print(f"Error loading main prompt from {filepath}: {e}")
            return ""

    def generate_tweet(self, scraped_data, user_comments="", image_path=None):
        # Start with the main prompt loaded from the file
        prompt = self.main_prompt

        # Append additional context if available
        if scraped_data and len(scraped_data) > 0:
            prompt += f"\n<Notes>Scraped web page notes: {scraped_data}<Notes>\n"
        if user_comments:
            prompt += f"<user comments> user comments: {user_comments}<user comments>\n"
        if image_path:
            prompt += f"<user defined> image: {image_path}<user defined>\n"

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
