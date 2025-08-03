import tweepy
import schedule
import time
import random
import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set up logging
logging.basicConfig(
    filename='quote_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Twitter API credentials
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"
ACCESS_TOKEN = "your_access_token"
ACCESS_TOKEN_SECRET = "your_access_token_secret"
BEARER_TOKEN = "your_bearer_token"

# Initialize Tweepy client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Set up requests session with retries
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

def post_philosophy_quote():
    quotes = load_quotes()
    if not quotes:
        logging.warning("No quotes loaded, skipping post.")
        return
    quote = random.choice(quotes)
    post_text = f"{quote['content']} - {quote['author']}"
    try:
        client.create_tweet(text=post_text[:280])  # Ensure within X's 280-char limit
        logging.info(f"Posted: {post_text}")
    except tweepy.TweepyException as e:
        logging.error(f"Error posting to X: {e}")

# Schedule daily post at 9:00 AM
schedule.every().day.at("09:00").do(post_philosophy_quote)

# Run scheduler
while True:
    try:
        schedule.run_pending()
        time.sleep(60)
    except Exception as e:
        logging.error(f"Scheduler error: {e}")
        time.sleep(60)  # Continue loop even if scheduler fails