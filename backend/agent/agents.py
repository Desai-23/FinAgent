import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, FINNHUB_API_KEY
from agent.tools import get_stock_price, get_stock_info
import finnhub
from datetime import datetime, timedelta

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_BASE_URL,
)
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)


def research_agent(ticker: str) -> dict:
    """Agent 1 — fetches stock price and company info."""
    price_data = get_stock_price(ticker)
    company_data = get_stock_info(ticker)

    prompt = f"""You are a financial research agent.
Raw data for {ticker}:

PRICE DATA:
{price_data}

COMPANY DATA:
{company_data}

Summarize into a clean research brief in 3-4 sentences.
Only use the data provided. Do not make anything up."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return {
        "ticker": ticker,
        "price_raw": price_data,
        "company_raw": company_data,
        "research_summary": response.choices[0].message.content,
    }


def sentiment_agent(ticker: str) -> dict:
    """Agent 2 — fetches news and scores sentiment."""
    try:
        today = datetime.now()
        from_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")
        news_items = finnhub_client.company_news(ticker, _from=from_date, to=to_date)
        recent_news = news_items[:5] if news_items else []

        if not recent_news:
            return {
                "ticker": ticker,
                "sentiment": "Neutral",
                "sentiment_score": 0,
                "news_summary": "No recent news found for this ticker.",
                "headlines": [],
            }

        headlines = [item.get("headline", "") for item in recent_news]
        headlines_text = "\n".join([f"- {h}" for h in headlines])

    except Exception as e:
        return {
            "ticker": ticker,
            "sentiment": "Neutral",
            "sentiment_score": 0,
            "news_summary": f"Could not fetch news: {str(e)}",
            "headlines": [],
        }

    prompt = f"""You are a financial sentiment analysis agent.
Analyze these headlines for {ticker}:

{headlines_text}

Respond in this exact format:
SENTIMENT: [Positive/Negative/Neutral]
SCORE: [number from -10 to +10]
SUMMARY: [2-3 sentences explaining the sentiment]"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    raw = response.choices[0].message.content
    sentiment, score, summary = "Neutral", 0, raw

    for line in raw.split("\n"):
        if line.startswith("SENTIMENT:"):
            sentiment = line.replace("SENTIMENT:", "").strip()
        elif line.startswith("SCORE:"):
            try:
                score = int(line.replace("SCORE:", "").strip())
            except:
                score = 0
        elif line.startswith("SUMMARY:"):
            summary = line.replace("SUMMARY:", "").strip()

    return {
        "ticker": ticker,
        "sentiment": sentiment,
        "sentiment_score": score,
        "news_summary": summary,
        "headlines": headlines,
    }


def report_agent(ticker: str, research: dict, sentiment: dict) -> str:
    """Agent 3 — writes the final professional report."""
    prompt = f"""You are a professional financial report writing agent.
Findings for {ticker}:

RESEARCH:
{research['research_summary']}

SENTIMENT:
Overall: {sentiment['sentiment']} (Score: {sentiment['sentiment_score']}/10)
{sentiment['news_summary']}

Headlines:
{chr(10).join([f'- {h}' for h in sentiment['headlines'][:3]])}

Write a professional financial analysis report with these sections:
1. **Overview** — company and current price
2. **Market Sentiment** — what the news says
3. **Key Takeaway** — one clear insight for an investor

Keep it under 200 words. Be professional and factual."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content
