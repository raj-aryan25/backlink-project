# config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file if it exists

# Your Google AI API Key. It's recommended to load this from an environment variable for security.
# To set it, run `export GOOGLE_API_KEY='Your_API_Key_Here'` in your terminal.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Default delay in milliseconds to wait between actions to ensure pages load
# and to avoid being flagged as a bot.
ACTION_DELAY = 2000  # 2 seconds
