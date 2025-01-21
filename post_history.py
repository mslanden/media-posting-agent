import json
import os

POST_HISTORY_FILE = "post_history.json"

def save_post(post):
    """
    Save a post to the post history JSON file.

    Args:
        post (dict): The post to save.
    """
    posts = load_posts()
    posts.append(post)
    try:
        with open(POST_HISTORY_FILE, "w") as f:
            json.dump(posts, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving post: {e}")
        return False

def load_posts():
    """
    Load the post history from the JSON file. If the file does not exist or is corrupted,
    return an empty list.

    Returns:
        list: The loaded posts.
    """
    if os.path.exists(POST_HISTORY_FILE):
        try:
            with open(POST_HISTORY_FILE, "r") as f:
                posts = json.load(f)
            return posts
        except Exception as e:
            print(f"Error loading posts: {e}")
            return []
    else:
        return []
