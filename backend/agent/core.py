import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL
from agent.tools import get_stock_price, get_stock_info, get_current_date

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_BASE_URL,
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the current stock price and daily change percentage for a stock ticker symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol in uppercase. Example: AAPL, MSFT, TSLA, GOOGL"
                    }
                },
                "required": ["ticker"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_info",
            "description": "Get company details including sector, industry, market cap and business description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol in uppercase. Example: AAPL, MSFT, TSLA, GOOGL"
                    }
                },
                "required": ["ticker"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get the current date and time.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    }
]

TOOL_MAP = {
    "get_stock_price": get_stock_price,
    "get_stock_info": get_stock_info,
    "get_current_date": get_current_date,
}

SYSTEM_PROMPT = """You are FinAgent, a professional AI financial assistant.

You have access to these tools:
- get_stock_price: use when asked about a stock price or daily change
- get_stock_info: use when asked about a company, its sector, industry, or market cap
- get_current_date: use when asked about today's date or time

STRICT RULES:
1. Always call tools for ANY question about stock prices, market cap, or company data.
2. If a tool returns an error or "Unable to fetch", relay that message honestly. NEVER make up or guess stock prices or market caps.
3. Only answer from your own knowledge for general finance concepts (like "what is a stock index?").
4. Be concise and professional."""


def run_agent(user_message: str, conversation_history: list) -> str:
    """Run the FinAgent with tool use support."""
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.1,
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        messages.append(response_message)

        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name

            try:
                raw_args = tool_call.function.arguments
                function_args = json.loads(raw_args) if raw_args and raw_args.strip() else {}
            except json.JSONDecodeError:
                function_args = {}

            tool_fn = TOOL_MAP.get(function_name)
            if tool_fn:
                # Call with args only if there are any
                result = tool_fn(**function_args) if function_args else tool_fn()
            else:
                result = f"Tool '{function_name}' not found."

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

        final_response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.1,
        )
        return final_response.choices[0].message.content

    return response_message.content
