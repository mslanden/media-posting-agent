import argparse
import os
import sys
import uuid
from typing import Optional, Dict, Any
from frontend.app import generate_content
from scraper import Scraper
from settings import load_settings
from post_history import save_post
from datetime import datetime

__version__ = "1.0.0"

def validate_url(url: str) -> str:
    """Validate URL format."""
    if not url.startswith(('http://', 'https://')):
        raise argparse.ArgumentTypeError("URL must start with http:// or https://")
    return url

def validate_date(date_str: str) -> str:
    """Validate date format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError("Date must be in YYYY-MM-DD format")

def validate_time(time_str: str) -> str:
    """Validate time format."""
    try:
        datetime.strptime(time_str, "%H:%M")
        return time_str
    except ValueError:
        raise argparse.ArgumentTypeError("Time must be in HH:MM format")


def create_mock_request(args: argparse.Namespace, api_key: str, llm_model: str) -> Dict[str, Any]:
    """Create mock request payload compatible with Flask request structure."""
    class MockFile:
        def __init__(self, file_path: str):
            self.file_path = file_path
            self.filename = os.path.basename(file_path)

        def save(self, save_path: str):
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(self.file_path, 'rb') as src, open(save_path, 'wb') as dest:
                dest.write(src.read())

    return {
        'form': {
            'message': args.message,
            'url': args.url,
            'mediaType': args.media_type,
            'api_key': api_key,
            'llm_model': llm_model,
            'postDate': args.post_date,
            'postTime': args.post_time
        },
        'files': {
            'image': MockFile(args.image) if args.image else None
        }
    }

def handle_image(image_path: str) -> Optional[str]:
    """Handle image file operations with proper error handling."""
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        sys.exit(1)

    try:
        images_dir = os.path.join("frontend", "static", "images")
        os.makedirs(images_dir, exist_ok=True)
        ext = os.path.splitext(image_path)[1][1:]
        image_filename = f"image_{uuid.uuid4()}.{ext}"
        dest_path = os.path.join(images_dir, image_filename)

        with open(image_path, 'rb') as src, open(dest_path, 'wb') as dest:
            dest.write(src.read())

        return os.path.relpath(dest_path, ".")
    except Exception as e:
        print(f"Error handling image: {str(e)}")
        sys.exit(1)

def main():
    """Main CLI entry point for Marketing Agent."""
    parser = argparse.ArgumentParser(
        description="Marketing Agent CLI - AI-powered content generation tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    subparsers = parser.add_subparsers(
        title="available commands",
        dest="command",
        metavar="COMMAND"
    )

    # Scrape command
    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Scrape content from a URL and return formatted markdown"
    )
    scrape_parser.add_argument(
        "url",
        type=validate_url,
        help="URL to scrape content from (must include http:// or https://)"
    )

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate marketing content using AI"
    )
    generate_parser.add_argument(
        "--message",
        type=str,
        help="User message/prompt to guide content generation"
    )
    generate_parser.add_argument(
        "--url",
        type=validate_url,
        help="URL to scrape and use as context for generation"
    )
    generate_parser.add_argument(
        "--media_type",
        required=True,
        choices=["tweet", "linkedin", "article", "newsletter"],
        help="Type of content to generate"
    )
    generate_parser.add_argument(
        "--image",
        type=str,
        help="Path to image file to include in generated content"
    )
    generate_parser.add_argument(
        "--post_date",
        type=validate_date,
        help="Date to schedule the post (YYYY-MM-DD)"
    )
    generate_parser.add_argument(
        "--post_time",
        type=validate_time,
        help="Time to schedule the post (HH:MM)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "scrape":
            markdown_content = Scraper(args.url)
            if "Error" in markdown_content:
                print(f"Scraping Error: {markdown_content}")
                sys.exit(1)
            print(markdown_content)
            sys.exit(0)

        elif args.command == "generate":
            settings = load_settings()
            if not (api_key := settings.get("api_key")):
                print("Error: No API key found in settings")
                sys.exit(1)
            if not (llm_model := settings.get("llm_model")):
                print("Error: No LLM model configured in settings")
                sys.exit(1)

            scraped_data = ""
            if args.url:
                scraper = Scraper()
                scraped_data, status = scraper.scrape(args.url)
                if status != 200:
                    print(f"Context Scraping Error: {scraped_data}")
                    sys.exit(1)

            image_path = handle_image(args.image) if args.image else None

            mock_request = create_mock_request(args, api_key, llm_model)
            response = generate_content(request=mock_request)

            if response[1] == 200:
                print(f"Success: {response[0].get_json().get('message')}")
                if post_id := save_post(response[0].get_json()):
                    print(f"Post saved with ID: {post_id}")
                sys.exit(0)
            else:
                print(f"Generation Error: {response[0].get_json().get('error')}")
                sys.exit(1)

    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        sys.exit(2)

if __name__ == "__main__":
    main()
