import schedule
import time
import random
import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from threads_api.src.threads_api import ThreadsAPI
import asyncio
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    filename='quote_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables for Threads API credentials
load_dotenv()
INSTAGRAM_USERNAME = os.environ.get('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.environ.get('INSTAGRAM_PASSWORD')

# Set up requests session with retries for Quotable API
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# Load quotes from Quotable API
def load_quotes():
    url = "https://api.quotable.io/random"
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        logging.info("Successfully fetched quote from Quotable API")
        return [response.json()]  # Wrap single quote in a list for compatibility
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to load quotes: {e}")
        return None

# Async function to post to Threads
async def post_philosophy_quote():
    quotes = load_quotes()
    if not quotes:
        logging.warning("No quotes loaded, skipping post.")
        return
    quote = random.choice(quotes)
    post_text = f"{quote['content']} - {quote['author']}"
    
    try:
        api = ThreadsAPI()
        await api.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, cached_token_path=".token")
        result = await api.post(caption=post_text[:500])  # Threads allows up to 500 characters
        if result:
            logging.info(f"Posted: {post_text}")
        else:
            logging.error("Failed to post to Threads")
        await api.close_gracefully()
    except Exception as e:
        logging.error(f"Error posting to Threads: {e}")

# Wrapper to run async function in scheduler
def run_post_philosophy_quote():
    asyncio.run(post_philosophy_quote())

# Schedule daily post at 9:00 AM
schedule.every().day.at("09:00").do(run_post_philosophy_quote)

# Run scheduler
while True:
    try:
        schedule.run_pending()
        time.sleep(60)
    except Exception as e:
        logging.error(f"Scheduler error: {e}")
        time.sleep(60)