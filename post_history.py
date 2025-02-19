import json
import os

POST_HISTORY_FILE = "post_history.json"

load_scheduled = True # Load scheduled posts by default

def save_post(post):
    """
    Save a post to the post history JSON file.

    Args:
        post (dict): The post to save.

    Returns:
        bool: True if the post was saved successfully, False otherwise.
    """
    posts = load_posts()  # Load existing posts
    posts.append(post)  # Add the new post
    try:
        with open(POST_HISTORY_FILE, "w") as f:
            json.dump(posts, f, indent=4)  # Save the updated posts
        return True
    except Exception as e:
        print(f"Error saving post: {e}")
        return False


def update_post(post_id, updated_post):
    """
    Update a post in the post history JSON file.

    Args:
        post_id (str): The ID of the post to update.
        updated_post (dict): The updated post data.

    Returns:
        bool: True if the post was updated successfully, False otherwise.
    """
    posts = load_posts()
    for i, post in enumerate(posts):
        if str(post.get("id")) == str(post_id):  # Match by ID
            for key, value in updated_post.items():
                post[key] = value  # Update the post
            break
    else:
        print(f"Post with ID {post_id} not found.")
        return False

    try:
        with open(POST_HISTORY_FILE, "w") as f:
            json.dump(posts, f, indent=4)  # Save the updated posts
        return True
    except Exception as e:
        print(f"Error updating post: {e}")
        return False


def delete_post(post_id):
    """
    Delete a post from the post history JSON file.

    Args:
        post_id (str): The ID of the post to delete.

    Returns:
        bool: True if the post was deleted successfully, False otherwise.
    """
    posts = load_posts()
    post_to_delete = next((post for post in posts if str(post.get("id")) == str(post_id)), None)
    if post_to_delete and post_to_delete.get("image_path"):
        try:
            os.remove(os.path.join("frontend", post_to_delete["image_path"]))
        except Exception as e:
            print(f"Error deleting image: {e}")
    posts = [post for post in posts if str(post.get("id")) != str(post_id)]  # Exclude the post to delete
    try:
        with open(POST_HISTORY_FILE, "w") as f:
            json.dump(posts, f, indent=4)  # Save the updated posts
        return True
    except Exception as e:
        print(f"Error deleting post: {e}")
        return False


def load_posts():
    """
    Load the post history from the JSON file. If the file does not exist or is corrupted,
    return an empty list.

    Returns:
        list: The loaded posts, or an empty list if the file does not exist or is invalid.
    """
    posts = []
    if os.path.exists(POST_HISTORY_FILE):
        try:
            with open(POST_HISTORY_FILE, "r") as f:
                posts = json.load(f)
                if not load_scheduled:
                    posts = [post for post in posts if 'post_time' in post and post['post_time']] # Include scheduled posts if needed
            return posts
        except json.JSONDecodeError:
            pass # Handle empty or corrupted file

    return posts # Return empty list if posts is None
