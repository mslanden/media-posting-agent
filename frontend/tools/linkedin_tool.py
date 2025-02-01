import os
import requests
from typing import Optional, Union
import logging
from settings import load_settings

settings = load_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_linkedin_member_id(access_token: str) -> str:
    """
    Retrieve numeric LinkedIn member ID

    Args:
        access_token: LinkedIn OAuth access token

    Returns:
        Numeric member ID
    """
    try:
        response = requests.get(
            'https://api.linkedin.com/v2/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        response.raise_for_status()
        return response.json()['id']
    except Exception as e:
        logger.error(f"Failed to retrieve member ID: {e}")
        raise

def post_to_linkedin(
    post_text: str,
    access_token: str,
    image_path: Optional[str] = None,
    visibility: str = "PUBLIC"
) -> Union[dict, str]:
    """
    Post content to LinkedIn using UGC API.

    Args:
        post_text: Text content of the post
        access_token: LinkedIn OAuth access token
        image_path: Optional path to image file
        visibility: Visibility setting (default: PUBLIC)

    Returns:
        Dictionary with post details or error message
    """
    # Validate input
    if not post_text or len(post_text) > 3000:
        return {"error": "Invalid post text length"}

    try:
        # Dynamically get member ID
        linkedin_person_id = get_linkedin_member_id(access_token)
    except Exception as e:
        return {"error": f"Failed to get member ID: {e}"}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    try:
        # Image upload process (if applicable)
        image_urn = None
        if image_path and os.path.exists(image_path):
            # Register upload
            register_payload = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:member:{linkedin_person_id}",
                    "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}],
                }
            }
            register_response = requests.post(
                "https://api.linkedin.com/v2/assets?action=registerUpload",
                headers=headers,
                json=register_payload,
            )
            register_response.raise_for_status()

            upload_data = register_response.json()
            upload_url = upload_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            image_urn = upload_data["value"]["asset"]

            # Upload image
            with open(image_path, "rb") as image_file:
                upload_response = requests.put(upload_url, data=image_file)
                upload_response.raise_for_status()

        # Prepare post payload
        post_payload = {
            "author": f"urn:li:member:{linkedin_person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text},
                    "shareMediaCategory": "IMAGE" if image_urn else "NONE",
                    "media": [{"status": "READY", "media": image_urn}] if image_urn else [],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
        }

        # Post to LinkedIn
        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=headers,
            json=post_payload,
        )
        response.raise_for_status()

        logger.info("LinkedIn post submitted successfully")
        return {"success": True, "post_id": response.json().get("id")}

    except requests.exceptions.RequestException as e:
        error_message = e.response.text if hasattr(e, 'response') else str(e)
        logger.error(f"LinkedIn post failed: {error_message}")
        return {"error": error_message}

# Example usage
if __name__ == "__main__":
    # Replace with your actual access token
    access_token = settings.get("linkedin_access_token")

    result = post_to_linkedin(
        "Test post with LinkedIn API",
        access_token,
        image_path=None  # Optional image path
    )
    print(result)
