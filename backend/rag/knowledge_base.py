"""
Built-in finance concepts knowledge base.
These are pre-loaded into ChromaDB so RAG works
even without any uploaded PDFs.
"""

FINANCE_KNOWLEDGE = [
    {
        "id": "kb1",
        "text": """Price-to-Earnings Ratio (P/E Ratio): The P/E ratio measures how much investors
are willing to pay per dollar of earnings. It is calculated by dividing the stock price
by earnings per share (EPS). A high P/E suggests investors expect high future growth.
A low P/E may indicate undervaluation or poor growth prospects. The average S&P 500
P/E ratio historically ranges between 15 and 25.""",
        "metadata": {"source": "knowledge_base", "topic": "valuation_metrics"}
    },
    {
        "id": "kb2",
        "text": """Market Capitalization: Market cap is the total market value of a company's
outstanding shares. It is calculated as share price multiplied by total shares outstanding.
Companies are classified as: Mega-cap (over $200B), Large-cap ($10B-$200B),
Mid-cap ($2B-$10B), Small-cap ($300M-$2B), and Micro-cap (under $300M).
Market cap helps investors understand a company's size and risk profile.""",
        "metadata": {"source": "knowledge_base", "topic": "company_metrics"}
    },
    {
        "id": "kb3",
        "text": """Earnings Per Share (EPS): EPS represents the portion of a company's profit
allocated to each outstanding share of common stock. It is calculated as net income
divided by the number of outstanding shares. Higher EPS generally indicates greater
profitability. EPS is one of the most important metrics used by investors to assess
company performance and stock valuation.""",
        "metadata": {"source": "knowledge_base", "topic": "valuation_metrics"}
    },
    {
        "id": "kb4",
        "text": """Dividend Yield: Dividend yield shows how much a company pays in dividends
relative to its stock price. It is calculated as annual dividend per share divided by
stock price. Income investors prefer high dividend yields. A yield above 4-5% may
indicate either a generous payout or a falling stock price. Tech companies typically
pay low or no dividends, while utilities and REITs pay higher yields.""",
        "metadata": {"source": "knowledge_base", "topic": "income_investing"}
    },
    {
        "id": "kb5",
        "text": """Stock Market Index: A stock market index measures the performance of a
group of stocks representing a portion of the market. The S&P 500 tracks 500 large
US companies. The Dow Jones Industrial Average tracks 30 major companies.
The NASDAQ Composite focuses on technology stocks. Indexes are used as benchmarks
to compare investment performance and gauge overall market health.""",
        "metadata": {"source": "knowledge_base", "topic": "market_basics"}
    },
    {
        "id": "kb6",
        "text": """Bull Market vs Bear Market: A bull market is a period of rising stock prices,
typically defined as a 20% or more increase from recent lows. A bear market is a period
of falling stock prices, defined as a 20% or more decline from recent highs. Bull markets
are associated with economic growth and investor confidence. Bear markets are associated
with economic recession, rising unemployment, and falling corporate profits.""",
        "metadata": {"source": "knowledge_base", "topic": "market_basics"}
    },
    {
        "id": "kb7",
        "text": """Return on Equity (ROE): ROE measures how effectively a company uses
shareholder equity to generate profit. It is calculated as net income divided by
shareholder equity. A higher ROE indicates more efficient use of equity capital.
Warren Buffett considers ROE above 15% as a sign of a strong business. ROE should
be compared within the same industry for meaningful analysis.""",
        "metadata": {"source": "knowledge_base", "topic": "valuation_metrics"}
    },
    {
        "id": "kb8",
        "text": """Debt-to-Equity Ratio (D/E): The D/E ratio compares a company's total debt
to its shareholder equity. It indicates how much leverage a company is using.
A high D/E ratio suggests higher financial risk but can also mean the company is
aggressively growing. A low D/E ratio indicates conservative financing.
Capital-intensive industries like utilities typically have higher D/E ratios.""",
        "metadata": {"source": "knowledge_base", "topic": "risk_metrics"}
    },
    {
        "id": "kb9",
        "text": """Diversification: Diversification is an investment strategy that spreads
investments across different assets, sectors, or geographies to reduce risk.
The principle is that different assets don't move in the same direction at the same time.
A diversified portfolio typically includes stocks, bonds, real estate, and commodities.
Modern Portfolio Theory by Harry Markowitz proved mathematically that diversification
can improve risk-adjusted returns.""",
        "metadata": {"source": "knowledge_base", "topic": "investment_strategy"}
    },
    {
        "id": "kb10",
        "text": """Compound Interest: Compound interest is the process where interest is
earned on both the initial principal and the accumulated interest from previous periods.
Albert Einstein reportedly called it the eighth wonder of the world. The formula is
A = P(1 + r/n)^(nt). Long-term investors benefit enormously from compounding.
For example, $10,000 invested at 10% annual return becomes $174,494 after 30 years.""",
        "metadata": {"source": "knowledge_base", "topic": "investment_basics"}
    },
    {
        "id": "kb11",
        "text": """ETF (Exchange-Traded Fund): An ETF is a type of investment fund that
trades on stock exchanges like individual stocks. ETFs typically track an index,
commodity, or sector. They offer diversification, low costs, and tax efficiency.
Popular ETFs include SPY (tracks S&P 500), QQQ (tracks NASDAQ 100), and VTI
(tracks total US stock market). ETFs have largely replaced mutual funds for
retail investors due to lower expense ratios.""",
        "metadata": {"source": "knowledge_base", "topic": "investment_vehicles"}
    },
    {
        "id": "kb12",
        "text": """Federal Reserve and Interest Rates: The Federal Reserve (Fed) is the
central bank of the United States. It controls monetary policy by setting the
federal funds rate — the interest rate at which banks lend to each other overnight.
When the Fed raises rates, borrowing becomes more expensive, slowing the economy
and reducing inflation. When it cuts rates, borrowing becomes cheaper, stimulating
growth. Stock markets are highly sensitive to Fed rate decisions.""",
        "metadata": {"source": "knowledge_base", "topic": "macroeconomics"}
    },
    {
        "id": "kb13",
        "text": """Volatility and VIX: Volatility measures how much a stock or market fluctuates.
The VIX (CBOE Volatility Index) is known as the fear index — it measures expected
volatility of the S&P 500 over the next 30 days. A VIX above 30 signals high fear
and uncertainty. A VIX below 20 signals calm markets. High volatility means higher
risk but also potentially higher returns. Beta measures a stock's volatility
relative to the broader market.""",
        "metadata": {"source": "knowledge_base", "topic": "risk_metrics"}
    },
    {
        "id": "kb14",
        "text": """Revenue vs Profit: Revenue (also called sales or turnover) is the total
income a company generates from its business activities before any expenses are deducted.
Profit is what remains after all expenses, taxes, and costs are subtracted from revenue.
Gross profit subtracts only cost of goods sold. Operating profit also subtracts
operating expenses. Net profit (bottom line) subtracts everything including taxes
and interest. A company can have high revenue but low or negative profit.""",
        "metadata": {"source": "knowledge_base", "topic": "financial_statements"}
    },
    {
        "id": "kb15",
        "text": """IPO (Initial Public Offering): An IPO is when a private company offers
shares to the public for the first time on a stock exchange. Companies use IPOs to
raise capital for growth, pay off debt, or allow early investors to exit.
The IPO process involves investment banks as underwriters who help price and sell shares.
IPO stocks can be highly volatile in early trading. Famous IPOs include Google (2004),
Facebook (2012), and Airbnb (2020).""",
        "metadata": {"source": "knowledge_base", "topic": "market_basics"}
    }
]