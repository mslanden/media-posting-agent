import os
from agent_wrapper.base_agent import AgentWrapper

class TweetAgent:
    def __init__(self, framework="openai", api_key=None):
        self.agent_wrapper = AgentWrapper(framework, api_key)

    def generate_tweet(self, scraped_data, user_comments):
        prompt = f"""
        You are an expert tweet writer.
        Based on the following scraped web page 
        {scraped_data}
        And the following user comments:
        {user_comments}
        Generate a tweet.
        """
        tweet = self.agent_wrapper.run(prompt)
        return tweet

    def save_tweet(self, tweet):
        try:
            with open("tweets.txt", "a", encoding="utf-8") as f:
                f.write(tweet + "\n")
            return True
        except Exception as e:
            print(f"Error saving tweet: {e}")
            return False
