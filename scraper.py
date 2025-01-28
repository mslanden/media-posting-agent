
from bs4 import BeautifulSoup
import requests
import markdownify
import os
import time
import re
import logging
import random
from typing import Tuple, Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration constants
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
]

CONTENT_SELECTORS = [
    {'name': 'article'},
    {'class': 'article-content'},
    {'class': 'post-content'},
    {'class': 'entry-content'},
    {'id': 'main-content'},
    {'role': 'main'},
    {'class': 'content-wrapper'},
    {'data-component': 'article-body'},
    {'class': re.compile(r'content|body|main', re.I)},
    {'itemprop': 'articleBody'}
]

UNWANTED_ELEMENTS = [
    'script', 'style', 'nav', 'footer', 'iframe',
    'aside', 'header', 'svg', 'button', 'form',
    'div.ad', 'div.social-share', 'div.comments'
]

UNWANTED_PATTERNS = re.compile(
    r'(subscribe\s+(now|here)|members-only|advertisement|'
    r'privacy\s+policy|cookie\s+settings|^\s*\[\+?\d+\s*chars\]\s*$|'
    r'please\s+enable\s+cookies|we\s+use\s+cookies)',
    re.IGNORECASE
)

class Scraper:
    def __init__(self, max_retries: int = 3, request_timeout: int = 15):
        self.max_retries = max_retries
        self.request_timeout = request_timeout
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Configure requests session with retries and random headers."""
        session = requests.Session()

        retry = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
            backoff_factor=0.5
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1'
        })

        return session

    def _random_delay(self):
        """Add random delay between requests to avoid detection."""
        time.sleep(random.uniform(0.5, 2.5))

    def fetch_url(self, url: str) -> Tuple[Optional[BeautifulSoup], int]:
        """Fetch and parse webpage content with error handling."""
        self._random_delay()

        try:
            response = self.session.get(
                url,
                timeout=self.request_timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            if not response.content:
                logger.warning(f"No content received from {url}")
                return None, 204  # No content status

            soup = BeautifulSoup(response.content, 'html.parser')
            return soup, 200

        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response else 500
            logger.error(f"Request failed: {str(e)}")
            return None, status_code
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None, 500

    def extract_content(self, soup: BeautifulSoup, url: str) -> Optional[BeautifulSoup]:
        """Extract main content using multiple strategies."""
        # Domain-specific handling
        domain_handlers = {
            'investors.com': lambda: soup.find('div', class_='single-post-content'),
            'github.com': lambda: soup.find('article') or soup.find('div', class_='markdown-body')
        }

        for domain, handler in domain_handlers.items():
            if domain in url:
                if content := handler():
                    return content
                break # Use domain handler only once

        # Generic content extraction
        for selector in CONTENT_SELECTORS:
            if content := soup.find(**selector):
                return content

        # Fallback strategies
        return soup.find('main') or soup.find('body')

    def clean_content(self, element: BeautifulSoup) -> BeautifulSoup:
        """Clean HTML content before conversion."""
        # Remove unwanted elements
        for selector in UNWANTED_ELEMENTS:
            for tag in element.select(selector):
                tag.decompose()

        # Clean attributes and empty elements
        for tag in element.find_all():
            # Remove all attributes except these
            tag.attrs = {
                k: v for k, v in tag.attrs.items()
                if k in ['href', 'src', 'alt']
            }

            # Remove empty elements
            if not tag.get_text(strip=True) and not tag.find_all():
                tag.decompose()

        return element

    def convert_to_markdown(self, element: BeautifulSoup) -> str:
        """Convert cleaned HTML to formatted markdown."""
        converter = markdownify.MarkdownConverter(
            heading_style="ATX",
            bullets=['-', '*', '+'],
            wrap_width=120,
            autolinks=False,
            custom_elements=['pre']
        )

        # Handle pre tags manually
        for pre_tag in element.find_all('pre'):
            lang = next((c.split('-')[-1] for c in pre_tag.get('class', []) if 'language-' in c), '')
            code_content = converter.convert_soup(pre_tag)
            pre_tag.replace_with(f"\n```{lang}\n{code_content}\n```\n")

        return converter.convert_soup(element)

    def post_process(self, markdown: str) -> str:
        """Clean and format the final markdown content."""
        lines = []
        prev_empty = False

        for line in markdown.splitlines():
            stripped = line.strip()

            # Remove unwanted patterns
            if UNWANTED_PATTERNS.search(stripped):
                continue

            # Normalize headers
            if stripped.startswith('#'):
                stripped = re.sub(r'\s+#+$', '', stripped)

            # Manage empty lines
            if not stripped:
                if not prev_empty:
                    lines.append('')
                    prev_empty = True
                continue

            lines.append(stripped)
            prev_empty = False

        return '\n'.join(lines).strip()

    def scrape(self, url: str) -> Tuple[Optional[str], int]:
        """Complete scraping pipeline."""
        soup, status = self.fetch_url(url)
        if status != 200 or not soup:
            return None, status

        content = self.extract_content(soup, url)
        if not content:
            logger.warning("No main content found")
            return None, 404

        cleaned = self.clean_content(content)
        markdown = self.convert_to_markdown(cleaned)
        final = self.post_process(markdown)

        return final, 200

def save_markdown(content: str, filename: str) -> bool:
    """Save content to markdown file with proper error handling."""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved {len(content)} characters to {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    urls = [
        "https://www.investors.com/news/technology/deepseek-ai-stocks-nvidia-artificial-intelligence-capital-spending/",
        "https://github.com/blog/ai-development-trends",
        "https://example.com/invalid-url"
    ]

    scraper = Scraper()

    for url in urls:
        print(f"\nScraping: {url}")
        content, status = scraper.scrape(url)

        if status == 200 and content:
            filename = f"output/{url.split('//')[1].replace('/', '_')}.md"
            if save_markdown(content, filename):
                print(f"Successfully saved to {filename}")
        else:
            print(f"Failed with status {status}")
