"""
FinAgent — Phase 5 Master Evaluation Runner
Runs all three dataset evaluations and produces:
  1. Terminal output with live results
  2. HTML report saved to backend/evaluation/reports/
"""

import sys
import os
import json
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.datasets.fiqa import run_fiqa_eval
from evaluation.datasets.phrasebank import run_phrasebank_eval
from evaluation.datasets.financebench import run_financebench_eval

N_QUESTIONS = 25
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")


def generate_html_report(all_results: list, total_passed: int, total_questions: int, duration: float) -> str:
    """Generate a clean HTML evaluation report."""
    overall_accuracy = round((total_passed / total_questions) * 100, 1)
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    def accuracy_color(acc):
        if acc >= 80: return "#16a34a"
        if acc >= 60: return "#d97706"
        return "#dc2626"

    def accuracy_bg(acc):
        if acc >= 80: return "#dcfce7"
        if acc >= 60: return "#fef3c7"
        return "#fef2f2"

    # Build dataset sections
    dataset_sections = ""
    for dataset in all_results:
        acc = dataset["accuracy"]
        color = accuracy_color(acc)
        bg = accuracy_bg(acc)

        # Build results table rows
        rows = ""
        for r in dataset["results"]:
            status_color = "#16a34a" if r["passed"] else "#dc2626"
            status_text = "✓ Pass" if r["passed"] else "✗ Fail"
            question_text = r.get("question") or r.get("text", "")[:80]

            if dataset["dataset"] == "Financial PhraseBank":
                detail = f'Expected: <strong>{r.get("expected", "")}</strong> → Got: <strong style="color:{status_color}">{r.get("predicted", "")}</strong>'
            else:
                detail = f'Keywords found: {r.get("keywords_found", 0)}/{r.get("keywords_total", 0)}'

            rows += f"""
            <tr>
                <td style="padding:10px;border-bottom:1px solid #f0f0f0;font-size:13px;color:#374151">{question_text}</td>
                <td style="padding:10px;border-bottom:1px solid #f0f0f0;font-size:12px;color:#6b7280">{detail}</td>
                <td style="padding:10px;border-bottom:1px solid #f0f0f0;font-size:12px;font-weight:600;color:{status_color};text-align:center">{status_text}</td>
            </tr>"""

        dataset_sections += f"""
        <div style="margin-bottom:40px;background:white;border-radius:12px;border:1px solid #e5e7eb;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
            <div style="padding:20px 24px;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;justify-content:space-between">
                <div>
                    <div style="font-size:17px;font-weight:700;color:#111827">{dataset['dataset']}</div>
                    <div style="font-size:13px;color:#6b7280;margin-top:2px">{dataset['description']}</div>
                </div>
                <div style="text-align:right">
                    <div style="font-size:28px;font-weight:800;color:{color}">{acc}%</div>
                    <div style="font-size:12px;color:#6b7280">{dataset['passed']}/{dataset['total']} correct</div>
                </div>
            </div>
            <div style="padding:0">
                <table style="width:100%;border-collapse:collapse">
                    <thead>
                        <tr style="background:#f9fafb">
                            <th style="padding:10px 10px;text-align:left;font-size:11px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px">Question / Sentence</th>
                            <th style="padding:10px 10px;text-align:left;font-size:11px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px">Detail</th>
                            <th style="padding:10px 10px;text-align:center;font-size:11px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px">Result</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FinAgent Evaluation Report</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f3f4f6; color: #111827; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
    </style>
</head>
<body>
<div class="container">

    <!-- Header -->
    <div style="text-align:center;margin-bottom:40px">
        <div style="font-size:36px;margin-bottom:8px">📊</div>
        <h1 style="font-size:28px;font-weight:800;color:#111827;letter-spacing:-0.5px">FinAgent Evaluation Report</h1>
        <p style="font-size:14px;color:#6b7280;margin-top:6px">Generated on {timestamp} · Duration: {round(duration/60, 1)} minutes</p>
    </div>

    <!-- Overall score card -->
    <div style="background:white;border-radius:12px;border:1px solid #e5e7eb;padding:28px;margin-bottom:32px;box-shadow:0 1px 3px rgba(0,0,0,0.06);text-align:center">
        <div style="font-size:13px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.7px;margin-bottom:12px">Overall Accuracy</div>
        <div style="font-size:56px;font-weight:900;color:{accuracy_color(overall_accuracy)};line-height:1">{overall_accuracy}%</div>
        <div style="font-size:15px;color:#6b7280;margin-top:8px">{total_passed} of {total_questions} questions answered correctly across 3 datasets</div>

        <!-- Dataset summary pills -->
        <div style="display:flex;justify-content:center;gap:12px;margin-top:20px;flex-wrap:wrap">
            {" ".join([f'<div style="padding:8px 16px;border-radius:20px;background:{accuracy_bg(d["accuracy"])};color:{accuracy_color(d["accuracy"])};font-size:13px;font-weight:600">{d["dataset"]}: {d["accuracy"]}%</div>' for d in all_results])}
        </div>
    </div>

    <!-- Dataset detail sections -->
    {dataset_sections}

    <!-- Footer -->
    <div style="text-align:center;font-size:12px;color:#9ca3af;padding-top:16px">
        FinAgent v3.0.0 · Evaluated against FiQA, Financial PhraseBank, and FinanceBench datasets
    </div>

</div>
</body>
</html>"""

    return html


def run_all_evaluations():
    """Master evaluation runner."""
    start_time = time.time()

    print("\n" + "="*60)
    print("  FinAgent — Phase 5 Full Evaluation Suite")
    print(f"  Running {N_QUESTIONS} questions per dataset")
    print(f"  Started at: {datetime.now().strftime('%I:%M %p')}")
    print("="*60)

    all_results = []
    total_passed = 0
    total_questions = 0

    # ── Run FiQA ──────────────────────────────────────────────
    print("\n🔵 Dataset 1/3 — FiQA (Finance Q&A)")
    fiqa_results = run_fiqa_eval(n_questions=N_QUESTIONS, use_rag=True)
    all_results.append(fiqa_results)
    total_passed += fiqa_results["passed"]
    total_questions += fiqa_results["total"]

    # ── Run Financial PhraseBank ───────────────────────────────
    print("\n🟡 Dataset 2/3 — Financial PhraseBank (Sentiment)")
    phrasebank_results = run_phrasebank_eval(n_questions=N_QUESTIONS)
    all_results.append(phrasebank_results)
    total_passed += phrasebank_results["passed"]
    total_questions += phrasebank_results["total"]

    # ── Run FinanceBench ───────────────────────────────────────
    print("\n🟢 Dataset 3/3 — FinanceBench (Company Facts)")
    financebench_results = run_financebench_eval(n_questions=N_QUESTIONS)
    all_results.append(financebench_results)
    total_passed += financebench_results["passed"]
    total_questions += financebench_results["total"]

    # ── Final summary ─────────────────────────────────────────
    duration = time.time() - start_time
    overall_accuracy = round((total_passed / total_questions) * 100, 1)

    print("\n" + "="*60)
    print("  FINAL RESULTS")
    print("="*60)
    for d in all_results:
        bar = "█" * int(d["accuracy"] / 5) + "░" * (20 - int(d["accuracy"] / 5))
        print(f"  {d['dataset']:<25} {bar} {d['accuracy']}%")
    print("-"*60)
    print(f"  {'OVERALL':<25} {overall_accuracy}% ({total_passed}/{total_questions})")
    print(f"  Duration: {round(duration/60, 1)} minutes")
    print("="*60)

    # ── Generate HTML report ───────────────────────────────────
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_filename = f"eval_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_path = os.path.join(REPORTS_DIR, report_filename)

    html = generate_html_report(all_results, total_passed, total_questions, duration)
    with open(report_path, "w") as f:
        f.write(html)

    # Also save raw JSON results
    json_path = report_path.replace(".html", ".json")
    with open(json_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "overall_accuracy": overall_accuracy,
            "total_passed": total_passed,
            "total_questions": total_questions,
            "duration_seconds": round(duration),
            "datasets": all_results,
        }, f, indent=2)

    print(f"\n📄 HTML Report saved to:")
    print(f"   {report_path}")
    print(f"\n📦 JSON Results saved to:")
    print(f"   {json_path}")
    print("\nOpen the HTML file in your browser to see the full report!")

    return all_results


if __name__ == "__main__":
    run_all_evaluations()