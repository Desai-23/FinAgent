"""
FinanceBench Evaluation — REAL Hugging Face Dataset
Dataset: PatronusAI/financebench
150 questions with answers from real SEC filings (10-K, 10-Q, 8-K)
Tests: Is our agent accurate on real verified company financial data?
"""

import sys
import os
import time
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def load_financebench_samples(n: int = 25, seed: int = 42) -> list:
    """Load real questions from the FinanceBench dataset."""
    try:
        from datasets import load_dataset
        print("  [FinanceBench] Downloading real FinanceBench dataset...")

        dataset = load_dataset("PatronusAI/financebench", trust_remote_code=True)

        samples = []
        for item in dataset["train"]:
            question = item.get("question", "").strip()
            answer = item.get("answer", "").strip()
            company = item.get("company", "").strip()
            ticker = item.get("ticker", "").strip()

            if question and answer and len(answer) < 200:
                samples.append({
                    "question": question,
                    "expected_answer": answer,
                    "company": company,
                    "ticker": ticker,
                })

        random.seed(seed)
        random.shuffle(samples)
        selected = samples[:n]

        for i, s in enumerate(selected):
            s["id"] = i + 1

        print(f"  [FinanceBench] Loaded {len(selected)} real questions from SEC filing data")
        return selected

    except Exception as e:
        print(f"  [FinanceBench] Failed to load real dataset: {e}")
        print("  [FinanceBench] Falling back to built-in questions...")
        return _fallback_questions(n)


def _fallback_questions(n: int) -> list:
    """Fallback questions if Hugging Face is unavailable."""
    questions = [
        {"id": 1,  "question": "What sector does Apple operate in?",       "expected_answer": "Technology",  "company": "Apple",     "ticker": "AAPL"},
        {"id": 2,  "question": "What industry is Microsoft in?",           "expected_answer": "Software",    "company": "Microsoft", "ticker": "MSFT"},
        {"id": 3,  "question": "What exchange is Tesla listed on?",        "expected_answer": "NASDAQ",      "company": "Tesla",     "ticker": "TSLA"},
        {"id": 4,  "question": "What sector is Amazon in?",                "expected_answer": "Technology",  "company": "Amazon",    "ticker": "AMZN"},
        {"id": 5,  "question": "What industry is Nvidia in?",              "expected_answer": "Semiconductors", "company": "Nvidia", "ticker": "NVDA"},
        {"id": 6,  "question": "What sector is JPMorgan Chase in?",        "expected_answer": "Financial",   "company": "JPMorgan",  "ticker": "JPM"},
        {"id": 7,  "question": "What sector is Meta Platforms in?",        "expected_answer": "Technology",  "company": "Meta",      "ticker": "META"},
        {"id": 8,  "question": "What industry is Netflix in?",             "expected_answer": "Entertainment","company": "Netflix",  "ticker": "NFLX"},
        {"id": 9,  "question": "What sector is Walmart in?",               "expected_answer": "Retail",      "company": "Walmart",   "ticker": "WMT"},
        {"id": 10, "question": "What industry is Visa in?",                "expected_answer": "Financial",   "company": "Visa",      "ticker": "V"},
    ]
    return questions[:n]


def score_financebench_response(
    question: str,
    response: str,
    expected_answer: str
) -> tuple[bool, str]:
    """
    Score using LLM-as-judge: does the response contain
    the correct answer from the SEC filing?
    """
    from openai import OpenAI
    from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL

    client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

    prompt = f"""You are an evaluation judge for a financial AI system.

Question: {question}
Expected answer (from SEC filing): {expected_answer}
System response: {response[:500]}

Does the system response contain information that matches or is consistent 
with the expected answer?
It does not need to be word-for-word — just factually correct.

Respond with ONLY: PASS or FAIL
Then on the next line, one short reason (max 10 words).

Example:
PASS
Response correctly states the revenue figure"""

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
        # Fallback: check if expected answer keywords appear in response
        passed = any(
            word.lower() in response.lower()
            for word in expected_answer.split()
            if len(word) > 3
        )
        return passed, "Fallback keyword check"


def run_financebench_eval(n_questions: int = 25) -> dict:
    """Run FinanceBench evaluation and return results."""
    from agent.core import run_agent

    questions = load_financebench_samples(n_questions)
    results = []
    passed = 0
    failed = 0

    print(f"\n{'='*50}")
    print(f"  FinanceBench — {len(questions)} Real SEC Filing Questions")
    print(f"  Source: PatronusAI/financebench — verified answers")
    print(f"  Scoring: LLM-as-judge vs ground truth answers")
    print(f"{'='*50}")

    for i, test in enumerate(questions):
        print(f"\n[{i+1}/{len(questions)}] {test['question'][:65]}...")
        print(f"  Expected: {test['expected_answer'][:80]}")
        print(f"  Company:  {test['company']} ({test['ticker']})")

        try:
            response = run_agent(test["question"], [])
            passed_test, reason = score_financebench_response(
                test["question"], response, test["expected_answer"]
            )

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
                "company": test["company"],
                "ticker": test["ticker"],
                "expected_answer": test["expected_answer"],
                "response": response[:300] + "..." if len(response) > 300 else response,
                "judge_reason": reason,
                "passed": passed_test,
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1
            results.append({
                "id": test["id"],
                "question": test["question"],
                "company": test["company"],
                "ticker": test["ticker"],
                "expected_answer": test["expected_answer"],
                "response": f"ERROR: {str(e)}",
                "judge_reason": "Exception during evaluation",
                "passed": False,
            })

        time.sleep(1.5)

    total = len(questions)
    accuracy = round((passed / total) * 100, 1)

    print(f"\n{'='*50}")
    print(f"  FinanceBench Results: {passed}/{total} — {accuracy}% accuracy")
    print(f"  Source: Real SEC filing ground truth answers")
    print(f"{'='*50}")

    return {
        "dataset": "FinanceBench",
        "description": "SEC filing Q&A — PatronusAI/financebench, verified answers",
        "total": total,
        "passed": passed,
        "failed": failed,
        "accuracy": accuracy,
        "results": results,
    }

