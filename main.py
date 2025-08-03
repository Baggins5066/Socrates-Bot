import tweepy
import schedule
import time
import random
import requests

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

# Load quotes from Quotable API
def load_quotes():
    url = "https://api.quotable.io/random"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return [response.json()]  # Wrap single quote in a list for compatibility
    except Exception as e:
        print(f"Error loading quotes: {e}")
        return None

def post_philosophy_quote():
    quotes = load_quotes()
    if not quotes:
        print("No quotes loaded, skipping post.")
        return
    quote = random.choice(quotes)
    post_text = f"{quote['content']} - {quote['author']}"
    try:
        client.create_tweet(text=post_text[:280])  # Ensure within X's 280-char limit
        print(f"Posted: {post_text}")
    except Exception as e:
        print(f"Error posting to X: {e}")

# Schedule daily post at 9:00 AM
schedule.every().day.at("09:00").do(post_philosophy_quote)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)