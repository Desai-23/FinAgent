import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Groq API settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Finnhub settings
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# App settings
APP_TITLE = "FinAgent"
APP_VERSION = "1.0.0"
