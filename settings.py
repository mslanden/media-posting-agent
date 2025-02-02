import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "llm_model": "openai",  # default model
    "dark_mode": False,
    # You might remove "api_key" from defaults since it will be loaded from the env
}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def load_settings():
    # Start with defaults
    settings = DEFAULT_SETTINGS.copy()

    # Load settings from file if available
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                file_settings = json.load(f)
            settings.update(file_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")

    # Based on the chosen model, load the corresponding API key from the environment
    model = settings.get("llm_model", "openai")
    if model == "openai":
        settings["api_key"] = os.getenv("OPENAI_API_KEY", "")
    elif model == "anthropic":
        settings["api_key"] = os.getenv("ANTHROPIC_API_KEY", "")
    elif model == "gemini":
        settings["api_key"] = os.getenv("GEMINI_API_KEY", "")
    elif model == "deepseek":
        settings["api_key"] = os.getenv("DEEPSEEK_API_KEY", "")
    else:
        # Fallback or error handling if needed
        settings["api_key"] = ""

    return settings
