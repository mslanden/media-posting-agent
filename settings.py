import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "api_key": "",
    "llm_model": "openai",
    "dark_mode": False,
    "twitter_api_key": "",
    "twitter_api_secret": "",
    "twitter_access_token": "",
    "twitter_access_token_secret": "",
    "linkedin_client_id": "",
    "linkedin_client_secret": "",
    "linkedin_access_token": "",
    "twitter_bearer_token": ""
}

def save_settings(settings):
    """
    Save the settings dictionary to a JSON file.

    Args:
        settings (dict): The settings to save.

    Returns:
        bool: True if the settings were saved successfully, False otherwise.
    """
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def load_settings():
    """
    Load the settings from the JSON file. If the file does not exist or is corrupted,
    return default settings.

    Returns:
        dict: The loaded or default settings.
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
            # Ensure all default keys exist
            return {**DEFAULT_SETTINGS, **settings}
        except Exception as e:
            print(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS.copy()
    else:
        return DEFAULT_SETTINGS.copy()
