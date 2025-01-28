import argparse
from frontend.app import generate_content
from utils import scrape_and_format_url
from settings import load_settings
from post_history import save_post
import os
import uuid

def main():
    parser = argparse.ArgumentParser(description="Marketing Agent CLI")
    subparsers = parser.add_subparsers(title="commands", dest="command")

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape a URL")
    scrape_parser.add_argument("url", help="URL to scrape")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate content")
    generate_parser.add_argument("--message", help="User comments")
    generate_parser.add_argument("--url", help="URL to scrape")
    generate_parser.add_argument("--media_type", required=True, choices=["tweet", "linkedin", "article", "newsletter"], help="Type of media to generate")
    generate_parser.add_argument("--image", help="Path to an image")

    args = parser.parse_args()

    if args.command == "scrape":
        markdown_content = scrape_and_format_url(args.url)
        if "Error" in markdown_content:
            print(f"Error: {markdown_content}")
        else:
            print(markdown_content)
    elif args.command == "generate":
        settings = load_settings()
        api_key = settings.get("api_key")
        llm_model = settings.get("llm_model")
        if not api_key:
            print("Error: No API key provided")
            return
        if not llm_model:
            print("Error: No LLM model provided")
            return

        scraped_data = ""
        if args.url:
            scraped_data = scrape_and_format_url(args.url)
            if "Error" in scraped_
                print(f"Error: {scraped_data}")
                return

        image_path = None
        if args.image:
            images_dir = os.path.join("frontend", "static", "images")
            os.makedirs(images_dir, exist_ok=True)
            image_filename = f"image_{uuid.uuid4()}.{os.path.splitext(args.image)[1][1:]}"
            image_path = os.path.join(images_dir, image_filename)
            try:
                with open(args.image, 'rb') as f:
                    with open(image_path, 'wb') as img_file:
                        img_file.write(f.read())
                image_path = os.path.relpath(image_path, ".")
            except Exception as e:
                print(f"Error saving image: {e}")
                return

        # Simulate the request.form data
        class MockRequestForm:
            def get(self, key):
                if key == "message":
                    return args.message
                elif key == "url":
                    return args.url
                elif key == "mediaType":
                    return args.media_type
                elif key == "api_key":
                    return api_key
                elif key == "llm_model":
                    return llm_model
                return None
        
        class MockRequestFiles:
            def get(self, key):
                if key == "image" and args.image:
                    class MockFile:
                        def save(self, path):
                            pass
                        @property
                        def filename(self):
                            return os.path.basename(args.image)
                    return MockFile()
                return None

        class MockRequest:
            @property
            def form(self):
                return MockRequestForm()
            @property
            def files(self):
                return MockRequestFiles()

        mock_request = MockRequest()
        
        response = generate_content(request=mock_request)
        if response[1] == 200:
            print(f"Success: {response[0].get_json().get('message')}")
        else:
            print(f"Error: {response[0].get_json().get('error')}")

if __name__ == "__main__":
    main()
