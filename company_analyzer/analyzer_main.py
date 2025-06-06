import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time # For polite delay
import re # Though not heavily used in this version, good for potential future refinements

TARGET_TICKER = 'AAPL'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Using D/E and P/E, P/B as context. These would ideally be passed or calculated fresh.
# For this subtask, we'll use the approximate values provided in the prompt.
# In a real scenario, these would be fetched or calculated in preceding steps.
PRECALCULATED_DE_RATIO = 1.72
PRECALCULATED_PE_RATIO = 31.5
PRECALCULATED_PB_RATIO = 53.2


def search_and_extract_news(query: str, num_snippets: int = 2) -> list[str]:
    """
    Searches DuckDuckGo HTML version for a query and extracts news titles and snippets.
    """
    search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {'User-Agent': USER_AGENT}
    snippets = []

    print(f"Attempting to fetch: {search_url}")
    try:
        time.sleep(2) # Politeness delay
        response = requests.get(search_url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='result__body')

        if not results:
             results = soup.find_all('div', class_='web-result')

        count = 0
        for res in results:
            if count >= num_snippets:
                break

            title_tag = res.find('a', class_='result__a')
            snippet_tag = res.find('a', class_='result__snippet')
            title = title_tag.get_text(strip=True) if title_tag else 'N/A'
            snippet_text = snippet_tag.get_text(strip=True) if snippet_tag else 'N/A'

            # Filter for relevance
            if not snippet_text.lower().startswith(title.lower()) and len(snippet_text) > 20 and "what is" not in title.lower() and "define" not in title.lower():
                snippets.append(f"Title: {title} - Snippet: {snippet_text[:250]}...") # Truncate for brevity
                count += 1
            elif title != 'N/A' and snippet_text == 'N/A' and len(title) > 20:
                 query_keywords = [q_word for q_word in query.lower().split() if len(q_word) > 3 and q_word not in ["for", "and", "the", "sector", "industry", "or"]]
                 if any(q_key in title.lower() for q_key in query_keywords):
                     snippets.append(f"Title: {title} - Snippet: (No distinct snippet text found)")
                     count +=1

        if not snippets:
            return ["No specific snippets found from search after filtering."]
        return snippets

    except requests.RequestException as e:
        return [f"Error scraping news search for '{query}': {e}"]
    except Exception as e:
        return [f"An unexpected error occurred during news scraping for '{query}': {e}"]

def analyze_risks(ticker_symbol: str):
    print(f"--- Identifying Potential Risks for {ticker_symbol} ---")

    ticker = yf.Ticker(ticker_symbol)
    info = {}
    try:
        info = ticker.info
    except Exception as e:
        print(f"Could not fetch ticker.info for {ticker_symbol}: {e}. Some data will be missing.")

    # 1. Company-Specific Risks Scan
    print("\n--- Company-Specific Risks (AAPL) ---")

    # Scan yfinance news
    print("  Scanning yfinance.news for litigation/product issues...")
    company_news = []
    try:
        company_news = ticker.news
    except Exception as e:
        print(f"    Error fetching yfinance.news: {e}")

    risk_keywords = ['lawsuit', 'recall', 'investigation', 'controversy', 'fine', 'regulatory action', 'antitrust', 'probe', 'complaint']
    found_yf_risks = []
    if company_news:
      for news_item in company_news[:10]: # Scan top 10 recent news
        title = news_item.get('title', '').lower()
        if any(keyword in title for keyword in risk_keywords):
          found_yf_risks.append(news_item.get('title'))
      if found_yf_risks:
          print(f"    yfinance news mentions potentially related to risks: {'; '.join(found_yf_risks)}")
      else:
          print("    No direct mentions of specified risk keywords in recent yfinance news titles.")
    else:
      print("    No news fetched from yfinance for risk scan.")

    # DuckDuckGo Searches for company-specific risks
    print("\n  DuckDuckGo search for lawsuits/legal/antitrust issues:")
    litigation_snippets = search_and_extract_news(f"{ticker_symbol} OR Apple lawsuit OR legal issues OR antitrust OR regulatory probe", num_snippets=2)
    for snippet in litigation_snippets: print(f"    - {snippet}")

    print("\n  DuckDuckGo search for product issues/recalls:")
    product_issue_snippets = search_and_extract_news(f"{ticker_symbol} OR Apple product issues OR product recall OR defect", num_snippets=1)
    for snippet in product_issue_snippets: print(f"    - {snippet}")

    # Debt Burden
    print(f"\n  Debt Burden Assessment:")
    print(f"    Previously calculated Debt/Equity ratio for {ticker_symbol} approx {PRECALCULATED_DE_RATIO:.2f}.")
    if PRECALCULATED_DE_RATIO > 1.0: # Example threshold, can be industry specific
        print(f"    Note: D/E ratio of {PRECALCULATED_DE_RATIO:.2f} is > 1.0. While common for some tech companies leveraging growth, it indicates significant reliance on debt and should be monitored against industry peers and company's cash flow generation.")
    elif PRECALCULATED_DE_RATIO < 0.5 :
        print(f"    Note: D/E ratio of {PRECALCULATED_DE_RATIO:.2f} is < 0.5, suggesting a relatively low debt burden compared to equity.")
    else:
        print(f"    Note: D/E ratio of {PRECALCULATED_DE_RATIO:.2f} is moderate.")


    # 2. Industry Risks Scan
    print("\n--- Industry Risks (Consumer Electronics/Technology) ---")
    print("  DuckDuckGo search for overcapacity or supply chain risks:")
    overcapacity_snippets = search_and_extract_news("Consumer Electronics industry OR Technology sector overcapacity OR supply chain disruption OR chip shortage", num_snippets=1)
    for snippet in overcapacity_snippets: print(f"    - {snippet}")

    print("\n  DuckDuckGo search for demand slowdown:")
    demand_slowdown_snippets = search_and_extract_news("Consumer Electronics industry demand slowdown OR Technology sector demand outlook negative OR macroeconomic headwinds", num_snippets=2)
    for snippet in demand_slowdown_snippets: print(f"    - {snippet}")

    # 3. Valuation Risk Summary
    print("\n--- Valuation Risk (AAPL) ---")
    print(f"  Current P/E ratio for {ticker_symbol} approx {PRECALCULATED_PE_RATIO:.1f} (from previous yfinance data).")
    print(f"  Current P/B ratio for {ticker_symbol} approx {PRECALCULATED_PB_RATIO:.1f} (from previous yfinance data).")
    print("  These ratios are high in absolute terms, suggesting high market expectations. For full context, these should be compared against:")
    print("    - Historical averages for the company.")
    print("    - Current averages for direct competitors and the broader industry/sector.")
    print("  A high valuation without correspondingly strong growth prospects (PEG ratio was noted as N/A from yfinance.info) can indicate valuation risk. Continuous monitoring of growth and profitability is key.")

    # 4. Liquidity Risk Check
    print("\n--- Liquidity Risk (AAPL) ---")
    avg_vol = info.get('averageVolume')
    avg_vol_10d = info.get('averageVolume10days')
    market_cap = info.get('marketCap')

    if pd.notna(avg_vol): print(f"  Average Volume (3 months): {avg_vol:,.0f}")
    else: print("  Average Volume (3 months) not available.")
    if pd.notna(avg_vol_10d): print(f"  Average Volume (10 days): {avg_vol_10d:,.0f}")
    else: print("  Average Volume (10 days) not available.")

    # Liquidity assessment: For a mega-cap like Apple, any reasonable volume means low liquidity risk.
    # We can also consider float vs market cap if available.
    if pd.notna(avg_vol) and avg_vol > 1000000 and pd.notna(market_cap) and market_cap > 100e9: # Arbitrary thresholds for a mega-cap
        print("  Liquidity: Appears High (typical for a mega-cap stock like AAPL). Liquidity risk is generally considered low.")
    elif pd.notna(avg_vol):
        print("  Liquidity: Average volume is present, but assess against typical trading volumes for this stock to determine if it's unusually low.")
    else:
        print("  Liquidity: Average volume data not readily available from yfinance.info to make a quick assessment.")

    print(f"\n--- End of Risk Identification for {ticker_symbol} ---")

if __name__ == "__main__":
    analyze_risks(TARGET_TICKER)
