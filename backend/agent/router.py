import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_BASE_URL,
)

ROUTER_PROMPT = """You are a query routing agent for a financial AI system.
Classify the user's message into exactly one of these three categories:

1. LLM — Use for:
   - Simple stock price or market cap lookups
   - Quick factual questions that need live data
   - Casual conversation or greetings

2. RAG — Use for:
   - Questions about finance concepts, definitions, or theory
   - Questions that can be answered from documents or a knowledge base
   - Examples: "what is a P/E ratio", "explain diversification",
     "what is compound interest", "how do ETFs work"

3. AGENTIC — Use for:
   - Deep analysis of a specific company or stock
   - Requests using words like "analyse", "analyze", "full report",
     "should I invest", "research", "breakdown"
   - Queries needing news + sentiment + research combined

Respond with ONLY one word: LLM, RAG, or AGENTIC.
No explanation. No punctuation. Just the single word."""


def classify_query(user_message: str) -> str:
    """
    Classify the user query as LLM, RAG, or AGENTIC.
    """
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": ROUTER_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.0,
            max_tokens=5,
        )
        result = response.choices[0].message.content.strip().upper()
        if result not in ["LLM", "RAG", "AGENTIC"]:
            return "LLM"
        return result
    except Exception:
        return "LLM"