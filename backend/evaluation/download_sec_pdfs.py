"""
Downloads sample SEC filing PDFs for FinanceBench evaluation.
These give our RAG system the source documents it needs to answer
FinanceBench questions correctly.
"""

import os
import sys
import urllib.request

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Free SEC EDGAR direct links — real 10-K filings
SEC_PDFS = [
    {
        "company": "Apple",
        "ticker": "AAPL",
        "filing": "10-K FY2022",
        "url": "https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/aapl-20220924.htm",
        "filename": "AAPL_10K_2022.html",
    },
    {
        "company": "Microsoft",
        "ticker": "MSFT",
        "filing": "10-K FY2023",
        "url": "https://www.sec.gov/Archives/edgar/data/789019/000156459023034798/msft-10k_20230630.htm",
        "filename": "MSFT_10K_2023.html",
    },
    {
        "company": "Nike",
        "ticker": "NKE",
        "filing": "10-K FY2023",
        "url": "https://www.sec.gov/Archives/edgar/data/320187/000032018723000039/nke-20230531.htm",
        "filename": "NKE_10K_2023.html",
    },
]


def download_sec_filings():
    uploads_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "uploads"
    )
    os.makedirs(uploads_dir, exist_ok=True)

    print("Downloading SEC filings for FinanceBench evaluation...")
    headers = {"User-Agent": "FinAgent Research Project contact@finagent.com"}

    for filing in SEC_PDFS:
        filepath = os.path.join(uploads_dir, filing["filename"])
        if os.path.exists(filepath):
            print(f"  Already exists: {filing['filename']}")
            continue

        print(f"  Downloading {filing['company']} {filing['filing']}...")
        try:
            req = urllib.request.Request(filing["url"], headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(filepath, "wb") as f:
                    f.write(response.read())
            print(f"  Saved: {filing['filename']}")
        except Exception as e:
            print(f"  Failed: {e}")

    print("\nDone. Now restart the backend to load these into ChromaDB.")
    print("The RAG system will automatically index them on startup.")


if __name__ == "__main__":
    download_sec_filings()
    