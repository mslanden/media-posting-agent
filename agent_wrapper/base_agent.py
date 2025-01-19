class AgentWrapper:
    def __init__(self, framework):
        if framework == "openai":
            from .openai_agent import OpenAIAgent
            self.agent = OpenAIAgent()
        elif framework == "anthropic":
            from .anthropic_agent import AnthropicAgent
            self.agent = AnthropicAgent()
        elif framework == "gemini":
            from .gemini_agent import GeminiAgent
            self.agent = GeminiAgent()
        else:
            raise ValueError("Unsupported framework")

    def run(self, prompt):
        return self.agent.run(prompt)
