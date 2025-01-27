from bs4 import BeautifulSoup
import requests
import markdownify
import os

def scrape_and_format_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Attempt to find the main article content
        article = soup.find('div', class_='article-content')
        if not article:
            article = soup.find('main')
        if not article:
            article = soup.find('div', id='content')
        if not article:
            return "Error: Could not find main article content"
        
        text_content = markdownify.markdownify(str(article))

        # Remove extra empty lines
        lines = text_content.splitlines()
        cleaned_lines = []
        empty_line_count = 0
        for line in lines:
            if not line.strip():
                empty_line_count += 1
                if empty_line_count <= 2:
                    cleaned_lines.append(line)
            else:
                empty_line_count = 0
                cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)
    except requests.exceptions.RequestException as e:
        return f"Error: Could not retrieve URL: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"

def save_markdown_file(content, filename="webdata.md"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.truncate(0) # Clear the file content
            f.write(content)
        return True
    except Exception as e:
        print(f"Error saving markdown file: {e}")
        return False
