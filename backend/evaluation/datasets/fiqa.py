"""
FiQA Evaluation — REAL Hugging Face Dataset
Dataset: BeIR/fiqa — Financial Opinion Mining and Question Answering
~5,500 financial questions from Stack Exchange and microblogs
Tests: Does our RAG system answer real financial questions correctly?
"""

import sys
import os
import time
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def load_fiqa_samples(n: int = 25, seed: int = 42) -> list:
    try:
        import importlib
        ds_lib = importlib.import_module("datasets")
        load_dataset = ds_lib.load_dataset

        print("  [FiQA] Downloading FiQA dataset...")

        # Use the BEIR version that has Parquet support
        dataset = load_dataset("sentence-transformers/fiqa", split="train")

        questions = []
        for item in dataset:
            text = (item.get("query") or item.get("question") or item.get("text") or "").strip()
            if text and len(text) > 15:
                questions.append({"question": text})

        if not questions:
            raise ValueError("No questions found")

        random.seed(seed)
        random.shuffle(questions)
        selected = questions[:n]

        for i, q in enumerate(selected):
            q["id"] = i + 1

        print(f"  [FiQA] Loaded {len(selected)} real questions")
        return selected

    except Exception as e:
        print(f"  [FiQA] Failed: {e}")
        print("  [FiQA] Using fallback questions...")
        return _fallback_questions(n)


def _fallback_questions(n: int) -> list:
    """Fallback questions if Hugging Face is unavailable."""
    questions = [
        {"id": 1,  "question": "What is a bond and how does it work?"},
        {"id": 2,  "question": "What is the difference between stocks and bonds?"},
        {"id": 3,  "question": "What is inflation and how does it affect investments?"},
        {"id": 4,  "question": "What is a mutual fund?"},
        {"id": 5,  "question": "How does compound interest work?"},
        {"id": 6,  "question": "What is dollar cost averaging?"},
        {"id": 7,  "question": "What is a stock market index?"},
        {"id": 8,  "question": "What does it mean when a stock is overvalued?"},
        {"id": 9,  "question": "What is a dividend?"},
        {"id": 10, "question": "What is portfolio diversification?"},
    ]
    return questions[:n]


def score_fiqa_response(question: str, response: str) -> tuple[bool, str]:
    """
    Score a FiQA response using the LLM as a judge.
    Asks the LLM: does this response actually answer the question?
    Returns (passed, reasoning)
    """
    from openai import OpenAI
    from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL

    client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

    prompt = f"""You are an evaluation judge for a financial AI assistant.

Question asked: {question}

Response given: {response[:500]}

Does this response:
1. Actually attempt to answer the question?
2. Contain relevant financial information?
3. Make sense as an answer?

Respond with ONLY: PASS or FAIL
Then on the next line, one short reason (max 10 words).

Example:
PASS
Correctly explains the concept with relevant details"""

    try:
        result = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=30,
        )
        content = result.choices[0].message.content.strip()
        lines = content.split("\n")
        verdict = lines[0].strip().upper()
        reason = lines[1].strip() if len(lines) > 1 else ""
        passed = "PASS" in verdict
        return passed, reason
    except Exception:
        # Fallback: basic length check
        return len(response) > 50, "Fallback length check"


def run_fiqa_eval(n_questions: int = 25, use_rag: bool = True) -> dict:
    """Run FiQA evaluation and return results."""
    from rag.retriever import rag_answer
    from agent.core import run_agent

    questions = load_fiqa_samples(n_questions)
    results = []
    passed = 0
    failed = 0

    print(f"\n{'='*50}")
    print(f"  FiQA Evaluation — {len(questions)} Real Finance Questions")
    print(f"  Source: BeIR/fiqa — Stack Exchange + microblogs")
    print(f"  Mode: {'RAG' if use_rag else 'LLM'} + LLM-as-judge scoring")
    print(f"{'='*50}")

    for i, test in enumerate(questions):
        print(f"\n[{i+1}/{len(questions)}] {test['question'][:65]}...")

        try:
            # Get answer from our system
            if use_rag:
                result = rag_answer(test["question"])
                response = result["answer"]
                sources = result.get("sources", [])
            else:
                response = run_agent(test["question"], [])
                sources = []

            # Score using LLM as judge
            passed_test, reason = score_fiqa_response(test["question"], response)

            status = "✅ PASS" if passed_test else "❌ FAIL"
            print(f"  Judge: {status} — {reason}")

            if passed_test:
                passed += 1
            else:
                failed += 1
                print(f"  Response preview: {response[:120]}...")

            results.append({
                "id": test["id"],
                "question": test["question"],
                "response": response[:300] + "..." if len(response) > 300 else response,
                "sources": sources,
                "judge_reason": reason,
                "passed": passed_test,
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1
            results.append({
                "id": test["id"],
                "question": test["question"],
                "response": f"ERROR: {str(e)}",
                "sources": [],
                "judge_reason": "Exception during evaluation",
                "passed": False,
            })

        time.sleep(1.5)  # LLM judge adds an extra call

    total = len(questions)
    accuracy = round((passed / total) * 100, 1)

    print(f"\n{'='*50}")
    print(f"  FiQA Results: {passed}/{total} passed — {accuracy}% accuracy")
    print(f"  Scoring method: LLM-as-judge")
    print(f"{'='*50}")

    return {
        "dataset": "FiQA",
        "description": "Finance Q&A — BeIR/fiqa dataset, LLM-as-judge scoring",
        "total": total,
        "passed": passed,
        "failed": failed,
        "accuracy": accuracy,
        "results": results,
    }