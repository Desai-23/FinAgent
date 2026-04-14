"""
Phase 1 Evaluation: Tests the agent against sample questions.
Run this to verify the agent is working correctly before Phase 2.
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.core import run_agent

TEST_QUESTIONS = [
      {
        "id": 1,
        "question": "What is the current price of Apple stock?",
        "check": lambda r: (
            "unable" not in r.lower() and
            "error" not in r.lower() and
            any(c.isdigit() for c in r) and
            any(x in r.upper() for x in ["USD", "AAPL", "PRICE", "$", "CLOSE"])
        ),
        "note": "Must return a real price or last close — not an error message"
    },
    {
        "id": 2,
        "question": "Tell me about Microsoft as a company.",
        "check": lambda r: any(x in r.lower() for x in ["microsoft", "software", "sector", "industry", "unable"]),
        "note": "Should return real company data or honest error"
    },
    {
        "id": 3,
        "question": "What is a stock market index?",
        "check": lambda r: any(x in r.lower() for x in ["index", "market", "stocks", "benchmark"]),
        "note": "General finance knowledge — no tool needed"
    },
    {
        "id": 4,
        "question": "What is Tesla's market cap?",
        "check": lambda r: any(x in r.lower() for x in ["$", "billion", "market cap", "unable", "error", "tsla"]),
        "note": "Should return real market cap or honest error"
    },
    {
        "id": 5,
        "question": "What day is it today?",
        "check": lambda r: any(x in r.lower() for x in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "2026", "march"]),
        "note": "Should return the actual current date"
    },
]


def run_evaluation():
    print("=" * 60)
    print("  FinAgent - Phase 1 Evaluation")
    print("=" * 60)

    passed = 0
    failed = 0

    for test in TEST_QUESTIONS:
        print(f"\n[Test {test['id']}] {test['question']}")
        print(f"Checking: {test['note']}")
        print("-" * 40)

        try:
            response = run_agent(test["question"], [])
            
            # Show full response
            print(f"Response:\n{response}\n")
            
            # Check if response looks correct
            is_valid = test["check"](response)
            
            # Flag if model leaked raw function call syntax (bad sign)
            has_leak = "<function=" in response or "function_call" in response
            
            if is_valid and not has_leak:
                print("Status: ✅ PASSED")
                passed += 1
            else:
                if has_leak:
                    print("Status: ⚠️  FAILED — model leaked raw function call syntax")
                else:
                    print("Status: ⚠️  FAILED — response doesn't look correct")
                failed += 1

        except Exception as e:
            print(f"ERROR: {str(e)}")
            print("Status: ❌ FAILED")
            failed += 1

        # Wait between tests to avoid Yahoo Finance rate limiting
        print("Waiting 4 seconds before next test...")
        time.sleep(4)

    print("\n" + "=" * 60)
    print(f"  Results: {passed} passed, {failed} failed out of {len(TEST_QUESTIONS)} tests")
    
    if passed == len(TEST_QUESTIONS):
        print("  🎉 All tests passed! Ready for Phase 2.")
    else:
        print("  ⚠️  Some tests failed. Review responses above.")
    print("=" * 60)


if __name__ == "__main__":
    run_evaluation()





