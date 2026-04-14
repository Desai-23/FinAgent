# api/routes.py
# Main chat and upload endpoints — protected by JWT authentication
# Keeps all existing features: streaming agentic, RAG, LLM, PDF upload

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent.core import run_agent
from agent.router import classify_query
from agent.graph import run_analysis
from rag.retriever import rag_answer
from rag.loader import load_pdf_into_chroma, UPLOADS_DIR, collection
from auth.dependencies import get_current_user
from auth.models import User
from config import FINNHUB_API_KEY
import finnhub
import json
import asyncio
import re
import os
import shutil

router = APIRouter()

# Per-user conversation history — key is user_id (int)
# Replaces the old single global conversation_history list
user_histories: dict = {}

finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)


class ChatRequest(BaseModel):
    message: str
    mode: str = "auto"


class ChatResponse(BaseModel):
    response: str
    history_length: int
    mode_used: str


COMMON_WORDS = {
    "I", "A", "AN", "THE", "FOR", "ON", "AT", "IN", "OF", "OR", "AND",
    "IS", "IT", "ME", "MY", "US", "BE", "DO", "GO", "IF", "AS", "UP",
    "BY", "TO", "BUY", "SELL", "GET", "CAN", "HOW", "WHY", "WHAT",
    "WHO", "ARE", "WAS", "HAS", "HAD", "ITS", "NOW", "NEW", "ALL",
    "TOP", "ANY", "USE", "NOT", "YES", "NO", "LOW", "HIGH", "GOOD",
    "BAD", "BIG", "OLD", "WAY", "DAY", "MAN", "MAY", "SAY", "SEE",
    "PUT", "TOO", "HIM", "HIS", "HER", "OUR", "OUT", "OFF", "SET",
    "OWN", "RUN", "TRY", "FEW", "FAR", "LET", "LOT", "CUT", "EAT",
    "SHOULD", "WOULD", "COULD", "WILL", "INTO", "FROM", "ABOUT",
    "OVER", "BACK", "JUST", "LIKE", "GIVE", "KNOW", "TAKE", "MAKE",
    "COME", "WANT", "LOOK", "ALSO", "THEY", "THEM", "THEN", "THAN",
    "THAT", "THIS", "WITH", "HAVE", "BEEN", "DOES", "MORE", "SOME",
    "TELL", "SHOW", "FIND", "HELP", "NEED", "HOLD", "LONG", "SHORT",
    "MARKET", "STOCK", "PRICE", "SHARE", "VALUE", "INVEST",
}


def finnhub_symbol_lookup(query: str) -> str:
    """
    Use Finnhub's symbol search to resolve a company name or
    partial ticker to a real ticker symbol.
    Returns the best match ticker or empty string if not found.
    """
    try:
        results = finnhub_client.symbol_lookup(query)
        if not results or not results.get("result"):
            return ""

        us_stocks = [
            r for r in results["result"]
            if r.get("type") == "Common Stock"
            and "." not in r.get("symbol", "")
        ]

        if us_stocks:
            return us_stocks[0]["symbol"]

        return results["result"][0].get("symbol", "")

    except Exception as e:
        print(f"[Ticker Lookup] Finnhub search failed for '{query}': {e}")
        return ""


def extract_ticker(message: str) -> str:
    """
    Extract and resolve a stock ticker from a natural language message.
    Steps:
    1. Pull candidate words/phrases from the message
    2. If it looks like a real ticker already (2-5 uppercase letters), verify it
    3. Otherwise do a Finnhub symbol lookup to resolve company names
    """
    message_upper = message.upper()

    # Step 1 — look for explicit patterns first
    explicit_patterns = [
        r'(?:ANALYSE|ANALYZE|ANALYSIS OF|REPORT ON|RESEARCH|CHECK)\s+([A-Z]{1,5})\b',
    ]
    for pattern in explicit_patterns:
        match = re.search(pattern, message_upper)
        if match:
            candidate = match.group(1)
            if candidate not in COMMON_WORDS:
                verified = finnhub_symbol_lookup(candidate)
                return verified if verified else candidate

    # Step 2 — scan for short uppercase words that look like tickers
    words = re.findall(r'\b([A-Z]{2,5})\b', message_upper)
    for word in words:
        if word not in COMMON_WORDS:
            verified = finnhub_symbol_lookup(word)
            if verified:
                return verified

    # Step 3 — try to find company names from natural language
    all_words = re.findall(r'\b([A-Za-z]{3,})\b', message)
    skip = {
        "should", "stock", "market", "company", "invest", "about",
        "price", "tell", "give", "what", "does", "this", "that",
        "with", "have", "been", "their", "they", "from", "into",
        "analysis", "analyse", "analyze", "report", "sector", "today",
        "currently", "trading", "industry", "shares", "financial",
    }
    for word in all_words:
        if word.lower() not in skip and len(word) >= 3:
            result = finnhub_symbol_lookup(word)
            if result:
                return result

    return ""


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Main chat endpoint — supports Auto/LLM/RAG/Agentic modes.
    Each user has their own conversation history.
    """
    message = request.message
    mode = request.mode.lower()
    user_id = current_user.id

    # Get or create this user's history
    if user_id not in user_histories:
        user_histories[user_id] = []
    conversation_history = user_histories[user_id]

    # Determine which mode to use
    if mode == "auto":
        mode_used = classify_query(message)
    elif mode == "agentic":
        mode_used = "AGENTIC"
    elif mode == "rag":
        mode_used = "RAG"
    else:
        mode_used = "LLM"

    # ── AGENTIC mode ──────────────────────────────────────────
    if mode_used == "AGENTIC":
        ticker = extract_ticker(message)
        if not ticker:
            mode_used = "LLM"
        else:
            async def stream_agentic():
                yield json.dumps({
                    "type": "mode", "mode_used": "AGENTIC", "ticker": ticker,
                }) + "\n"
                yield json.dumps({
                    "type": "step", "step": "research",
                    "message": f"Research Agent is analyzing {ticker}...",
                    "ticker": ticker,
                }) + "\n"
                await asyncio.sleep(0.1)
                try:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, run_analysis, ticker)

                    yield json.dumps({
                        "type": "step", "step": "sentiment",
                        "message": f"Sentiment Agent reading news for {ticker}...",
                        "ticker": ticker,
                    }) + "\n"
                    await asyncio.sleep(0.2)

                    yield json.dumps({
                        "type": "step", "step": "report",
                        "message": "Report Agent writing final analysis...",
                        "ticker": ticker,
                    }) + "\n"
                    await asyncio.sleep(0.2)

                    if result.get("error"):
                        yield json.dumps({
                            "type": "error",
                            "message": result["error"]
                        }) + "\n"
                        return

                    yield json.dumps({
                        "type": "done",
                        "mode_used": "AGENTIC",
                        "data": {
                            "ticker": ticker,
                            "sentiment": result["sentiment"].get("sentiment", "Neutral"),
                            "sentiment_score": result["sentiment"].get("sentiment_score", 0),
                            "headlines": result["sentiment"].get("headlines", []),
                            "final_report": result["final_report"],
                        },
                    }) + "\n"

                except Exception as e:
                    yield json.dumps({
                        "type": "error",
                        "message": str(e)
                    }) + "\n"

            return StreamingResponse(stream_agentic(), media_type="text/plain")

    # ── RAG mode ──────────────────────────────────────────────
    if mode_used == "RAG":
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, rag_answer, message)
            return ChatResponse(
                response=result["answer"],
                history_length=len(conversation_history),
                mode_used="RAG",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ── LLM mode ──────────────────────────────────────────────
    try:
        response = run_agent(message, conversation_history)

        # Save to this user's history
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": response})

        # Keep last 20 messages per user
        if len(conversation_history) > 20:
            user_histories[user_id] = conversation_history[-20:]

        return ChatResponse(
            response=response,
            history_length=len(user_histories[user_id]),
            mode_used="LLM",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/history")
async def clear_history(current_user: User = Depends(get_current_user)):
    """Clear only the current user's conversation history."""
    user_histories[current_user.id] = []
    return {"message": "Conversation history cleared.", "history_length": 0}


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF — prefixed with user ID to keep files separate per user."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    os.makedirs(UPLOADS_DIR, exist_ok=True)

    # Prefix with user ID so each user's files stay separate
    safe_filename = f"user{current_user.id}_{file.filename}"
    save_path = os.path.join(UPLOADS_DIR, safe_filename)

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunks_loaded = load_pdf_into_chroma(save_path, safe_filename)

    if chunks_loaded == 0:
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from PDF. Make sure it is not scanned/image-only."
        )

    return {
        "message": f"Successfully loaded '{file.filename}' into knowledge base.",
        "filename": safe_filename,
        "chunks_loaded": chunks_loaded,
    }


@router.get("/documents")
async def list_documents(current_user: User = Depends(get_current_user)):
    """List only the current user's uploaded PDFs."""
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    prefix = f"user{current_user.id}_"
    files = [f for f in os.listdir(UPLOADS_DIR) if f.startswith(prefix) and f.endswith(".pdf")]
    return {
        "documents": files,
        "total": len(files),
        "total_chunks": collection.count(),
    }


@router.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """Delete one of the current user's PDFs and remove its chunks from ChromaDB."""
    # Security check — users can only delete their own files
    if not filename.startswith(f"user{current_user.id}_"):
        raise HTTPException(status_code=403, detail="You can only delete your own files.")

    file_path = os.path.join(UPLOADS_DIR, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    # Remove chunks from ChromaDB
    try:
        results = collection.get(where={"source": filename})
        if results["ids"]:
            collection.delete(ids=results["ids"])
            return {
                "message": f"Deleted '{filename}' and removed {len(results['ids'])} chunks from knowledge base.",
                "chunks_removed": len(results["ids"]),
            }
    except Exception as e:
        print(f"[Delete] Error removing chunks: {e}")

    return {"message": f"Deleted '{filename}'.", "chunks_removed": 0}


@router.get("/health")
async def health_check():
    """Public health check — no auth required."""
    return {"status": "ok", "agent": "FinAgent", "version": "3.0.0"}







