import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.loader import collection
from openai import OpenAI
from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_BASE_URL,
)


def retrieve(query: str, n_results: int = 4) -> list[dict]:
    """
    Search ChromaDB for the most relevant documents for a query.
    Returns a list of matching documents with their metadata.
    """
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )

        docs = []
        for i, doc in enumerate(results["documents"][0]):
            docs.append({
                "text": doc,
                "source": results["metadatas"][0][i].get("source", "knowledge_base"),
                "topic": results["metadatas"][0][i].get("topic", ""),
                "distance": results["distances"][0][i] if results.get("distances") else 0,
            })
        return docs

    except Exception as e:
        print(f"[RAG] Retrieval error: {e}")
        return []


def rag_answer(query: str) -> dict:
    """
    Retrieve relevant documents and generate an answer using the LLM.
    Returns the answer and the sources used.
    """
    docs = retrieve(query)

    if not docs:
        return {
            "answer": "I couldn't find relevant information in the knowledge base for your query.",
            "sources": [],
        }

    # Build context from retrieved docs
    context_parts = []
    for i, doc in enumerate(docs):
        context_parts.append(f"[Source {i+1}: {doc['source']}]\n{doc['text']}")
    context = "\n\n".join(context_parts)

    prompt = f"""You are a financial knowledge assistant.
Use ONLY the context below to answer the user's question.
If the context does not contain enough information, say so honestly.

CONTEXT:
{context}

USER QUESTION:
{query}

Provide a clear, accurate answer based on the context above.
At the end, mention which sources you used."""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        answer = response.choices[0].message.content

        sources = list(set([doc["source"] for doc in docs]))

        return {
            "answer": answer,
            "sources": sources,
            "docs_used": len(docs),
        }

    except Exception as e:
        return {
            "answer": f"Error generating answer: {str(e)}",
            "sources": [],
        }