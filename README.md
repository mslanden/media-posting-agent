# Social Media Content Generator

This application allows users to generate content for various social media platforms using LLMs. It supports generating tweets, LinkedIn posts, articles, and newsletters. Users can provide a URL to scrape content from, a message to guide the generation, and an optional image. The application also supports scheduling posts for later publication.

## Features

-   **Content Generation:** Generate content for tweets, LinkedIn posts, articles, and newsletters using LLMs.
-   **Web Scraping:** Scrape content from URLs to use as a basis for content generation.
-   **Image Support:** Include images with generated posts.
-   **Post Scheduling:** Schedule posts for later publication.
-   **Settings:** Configure API keys and LLM model.
-   **Dark Mode:** Toggle between light and dark mode.

## Setup

1.  Clone the repository.
2.  Install the required packages using `pip install -r requirements.txt`.
3.  Create a `.env` file and add your API keys.
4.  Run the application using `python3 frontend/app.py`.

## Usage

1.  Open the application in your browser.
2.  Enter a URL to scrape content from (optional).
3.  Enter a message to guide the content generation (optional).
4.  Select the media type (tweet, linkedin, article, newsletter).
5.  Upload an image (optional).
6.  Set a post date and time (optional).
7.  Click the "Submit" button.
8.  View scheduled posts in the "Scheduled Posts" tab.
9.  Configure settings in the "Settings" tab.

## Dependencies

-   Flask
-   Requests
-   Beautiful Soup 4
-   Markdownify
-   Python-dotenv
-   Tweepy
-   Python-linkedin
-   APScheduler

