import requests
from bs4 import BeautifulSoup
import markdownify
import os

def scrape_and_format_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text = markdownify.markdownify(str(soup))
        return text
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}"
    except Exception as e:
        return f"Error processing URL: {e}"

def save_markdown_file(content, filename="webdata.md"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        return f"Error saving file: {e}"
