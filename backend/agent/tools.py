import finnhub
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FINNHUB_API_KEY

# Single Finnhub client instance
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

# Simple cache to avoid repeat calls
_cache = {}
CACHE_SECONDS = 60


def _is_cached(key):
    if key in _cache:
        if time.time() - _cache[key]["time"] < CACHE_SECONDS:
            return True
    return False


def _get_cache(key):
    return _cache[key]["data"]


def _set_cache(key, data):
    _cache[key] = {"data": data, "time": time.time()}


def get_stock_price(ticker: str) -> str:
    """Get real-time stock price using Finnhub."""
    ticker = ticker.upper().strip()
    cache_key = f"{ticker}_price"

    if _is_cached(cache_key):
        return _get_cache(cache_key)

    try:
        quote = finnhub_client.quote(ticker)

        # Finnhub returns: c=current, pc=prev close, d=change, dp=change%
        current_price = quote.get("c", 0)
        prev_close = quote.get("pc", 0)
        change = quote.get("d", 0)
        change_pct = quote.get("dp", 0)

        

        if not current_price or current_price == 0:
            # Market may be closed — try previous close instead
            if prev_close and prev_close > 0:
                result = (
                    f"{ticker} — Market currently closed.\n"
                    f"Last Close Price: USD {prev_close:.2f}\n"
                    f"Last Change: {change:+.2f} ({change_pct:+.2f}%)"
                )
                _set_cache(cache_key, result)
                return result
            return f"Could not find price for {ticker}. Please check the ticker symbol is correct."

        direction = "up" if change >= 0 else "down"

        result = (
            f"{ticker} is {direction} today.\n"
            f"Current Price: USD {current_price:.2f}\n"
            f"Previous Close: USD {prev_close:.2f}\n"
            f"Change: {change:+.2f} ({change_pct:+.2f}%)"
        )
        _set_cache(cache_key, result)
        return result

    except Exception as e:
        return f"Error fetching price for {ticker}: {str(e)}"


def get_stock_info(ticker: str) -> str:
    """Get company profile and key metrics using Finnhub."""
    ticker = ticker.upper().strip()
    cache_key = f"{ticker}_info"

    if _is_cached(cache_key):
        return _get_cache(cache_key)

    try:
        # Get company profile
        profile = finnhub_client.company_profile2(symbol=ticker)

        if not profile or not profile.get("name"):
            return f"Could not find company info for {ticker}. Please check the ticker symbol."

        name = profile.get("name", ticker)
        exchange = profile.get("exchange", "N/A")
        industry = profile.get("finnhubIndustry", "N/A")
        market_cap = profile.get("marketCapitalization", 0)
        country = profile.get("country", "N/A")
        ipo = profile.get("ipo", "N/A")
        website = profile.get("weburl", "N/A")

        # Format market cap
        # Format market cap - Finnhub returns value in MILLIONS of USD
        if market_cap:
            market_cap_usd = market_cap * 1_000_000  # convert to actual USD
            if market_cap_usd >= 1_000_000_000_000:
                market_cap_str = f"${market_cap_usd/1_000_000_000_000:.2f}T"
            elif market_cap_usd >= 1_000_000_000:
                market_cap_str = f"${market_cap_usd/1_000_000_000:.2f}B"
            else:
                market_cap_str = f"${market_cap_usd/1_000_000:.2f}M"
        else:
            market_cap_str = "N/A"

        result = (
            f"Company: {name} ({ticker})\n"
            f"Exchange: {exchange}\n"
            f"Industry: {industry}\n"
            f"Country: {country}\n"
            f"Market Cap: {market_cap_str}\n"
            f"IPO Date: {ipo}\n"
            f"Website: {website}"
        )
        _set_cache(cache_key, result)
        return result

    except Exception as e:
        return f"Error fetching company info for {ticker}: {str(e)}"


def get_current_date() -> str:
    """Get the current date and time."""
    now = datetime.now()
    return f"Current date and time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}"




