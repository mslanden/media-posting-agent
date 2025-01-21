class AgentWrapper:
    def __init__(self, framework, api_key=None):
        if framework == "openai":
            from .openai_agent import OpenAIAgent
            self.agent = OpenAIAgent(api_key)
        elif framework == "anthropic":
            from .anthropic_agent import AnthropicAgent
            self.agent = AnthropicAgent(api_key)
        elif framework == "gemini":
            from .gemini_agent import GeminiAgent
            self.agent = GeminiAgent(api_key)
        else:
            raise ValueError("Unsupported framework")

    def run(self, prompt, image_path=None):
        return self.agent.run(prompt, image_path)
