import datetime
import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Fetch S&P 500 tickers from Wikipedia
def fetch_sp500_tickers():
    print("🔍 Fetching S&P 500 tickers from Wikipedia...")
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0]
    tickers = df['Symbol'].tolist()
    print(f"✅ Found {len(tickers)} tickers.")
    return tickers

# Download stock data for given tickers and date range
def fetch_data(tickers, start, end):
    print(f"🔍 Getting stock prices from {start} to {end}...")
    data = yf.download(tickers, start=start, end=end, group_by='ticker', threads=True, auto_adjust=False)
    return data

# Analyze a single stock dataframe
def analyze_stock(ticker, df):
    df['Daily Return %'] = df['Adj Close'].pct_change() * 100
    df['SMA_5'] = df['Adj Close'].rolling(window=5).mean()

    latest = df.iloc[-1]
    last_return = latest['Daily Return %']
    last_close = latest['Adj Close']
    sma5 = latest['SMA_5']

    trend_score = (df['Daily Return %'].tail(5) > 0).sum()

    trade_signal = False
    reason = ""
    if last_close > sma5 and last_return > 0:
        trade_signal = True
        reason = "Price above 5-day SMA with positive momentum"
    else:
        reason = "No strong bullish signal"

    analysis = {
        'Ticker': ticker,
        'Last Close': last_close,
        'Last Return %': last_return,
        '5-Day SMA': sma5,
        'Trend Score': trend_score,
        'Trade Signal': trade_signal,
        'Reason': reason
    }
    return analysis

# Plot stock price and SMA
def plot_stock(ticker, df):
    plt.figure(figsize=(10, 5))
    plt.plot(df['Adj Close'], label='Adj Close Price', color='blue')
    plt.plot(df['SMA_5'], label='5-Day SMA', color='orange', linestyle='--')
    plt.title(f"{ticker} Price Chart")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    if not os.path.exists("charts"):
        os.makedirs("charts")
    plt.savefig(f"charts/{ticker}.png")
    plt.close()

# Save analysis results to CSV
def save_to_csv(analyses, filename="analysis.csv"):
    df = pd.DataFrame(analyses)
    df.to_csv(filename, index=False)

# Suggest best trade candidate
def suggest_best_trade(analyses):
    candidates = [a for a in analyses if a['Trade Signal']]
    if not candidates:
        print("❌ No strong trade candidates today.")
        return
    best = sorted(candidates, key=lambda x: (x['Trend Score'], x['Last Return %']), reverse=True)[0]
    print(f"\n🔥 Best Trade Candidate: {best['Ticker']}")
    print(f"   Last Close: ${best['Last Close']:.2f}")
    print(f"   Last Return: {best['Last Return %']:.2f}%")
    print(f"   Trend Score (last 5 days): {best['Trend Score']}/5")
    print(f"   Reason: {best['Reason']}")

# Main program
def main():
    DAYS_BACK = 15
    end_date = datetime.datetime.today().date()
    start_date = end_date - datetime.timedelta(days=DAYS_BACK)

    tickers = fetch_sp500_tickers()
    tickers = tickers[:20]  # Limit to first 20 for quick demo

    raw_data = fetch_data(tickers, start_date, end_date)

    all_analyses = []

    for ticker in tickers:
        if ticker in raw_data:
            df = raw_data[ticker].copy()
            analysis = analyze_stock(ticker, df)
            all_analyses.append(analysis)

            plot_stock(ticker, df)

            print(f"📊 {ticker} - Last Close: ${analysis['Last Close']:.2f} | "
                  f"Return: {analysis['Last Return %']:.2f}% | "
                  f"Trend Score: {analysis['Trend Score']}/5")

    save_to_csv(all_analyses)
    suggest_best_trade(all_analyses)

if __name__ == "__main__":
    main()
