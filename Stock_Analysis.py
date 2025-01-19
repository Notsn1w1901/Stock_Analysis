import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import requests

# Streamlit app structure
st.set_page_config(page_title="Stock Fundamental Analysis", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for rounded squares for metrics
st.markdown("""
<style>
    /* Metric Card Styles */
    .metric-card {
        background: linear-gradient(145deg, #6a8dff, #4CAF50);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.2s ease-in-out;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
    }

    .metric-card h3 {
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        margin-bottom: 10px;
    }

    .metric-card .value {
        font-size: 2rem;
        font-weight: bold;
        color: #ffffff;
    }

    .metric-card .icon {
        font-size: 2rem;
        color: white;
        margin-bottom: 10px;
    }

    /* Green for return, Red for risk */
    .metric-return {
        background: linear-gradient(145deg, #81C784, #388E3C);
    }

    .metric-risk {
        background: linear-gradient(145deg, #FF7043, #D32F2F);
    }

    .metric-drawdown {
        background: linear-gradient(145deg, #FFB74D, #F57C00);
    }

    .metric-sharpe {
        background: linear-gradient(145deg, #64B5F6, #1976D2);
    }

    .metric-other {
        background: linear-gradient(145deg, #80DEEA, #26C6DA);
    }
</style>
""", unsafe_allow_html=True)

# Title of the app
st.title('📈 Stock Fundamental Analysis Dashboard')

# Sidebar Inputs for User Interactivity
st.sidebar.image("Designer.png", use_container_width=True)
st.sidebar.header("Portfolio Inputs")
tickers_input = st.sidebar.text_input("Enter asset tickers (e.g., BBCA.JK, TSLA)", "BBCA.JK")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
market_ticker_input = st.sidebar.text_input("Enter market index ticker (e.g., ^JKSE for Jakarta Composite Index IDX)", "^JKSE")

# Function to fetch stock data using yfinance
def fetch_stock_data(symbol, start_date='2020-01-01', session=None):
    stock = yf.Ticker(symbol, session=session)
    df = stock.history(start=start_date)
    return df

# Safe method to handle missing data
def safe_get(data, key, default_value='N/A'):
    return data.get(key, default_value)

# Function to fetch key statistics from Yahoo Finance
def fetch_yahoo_finance_statistics(stock):
    info = stock.info
    
    # Extracting key financial metrics from Yahoo Finance
    pe_ratio = safe_get(info, 'trailingPE')
    market_cap = safe_get(info, 'marketCap')
    dividend_yield = safe_get(info, 'dividendYield')
    price_to_book = safe_get(info, 'priceToBook')
    beta = safe_get(info, 'beta')
    diluted_eps = safe_get(info, 'trailingEps')
    profit_margin = safe_get(info, 'profitMargins') * 100 if 'profitMargins' in info else 'N/A'
    operating_margin = safe_get(info, 'operatingMargins') * 100 if 'operatingMargins' in info else 'N/A'
    return_on_assets = safe_get(info, 'returnOnAssets') * 100 if 'returnOnAssets' in info else 'N/A'
    return_on_equity = safe_get(info, 'returnOnEquity') * 100 if 'returnOnEquity' in info else 'N/A'
    earnings_yield = (1 / pe_ratio) * 100 if pe_ratio != 'N/A' else 'N/A'
    
    # Formatting values for percentages and multiples with 2 decimal places
    statistics = {
        'PE Ratio': f"{pe_ratio:.2f}" if pe_ratio != 'N/A' else 'N/A',
        'Market Cap': market_cap,
        'Dividend Yield': f"{dividend_yield * 100:.2f}%" if dividend_yield != 'N/A' else 'N/A',
        'Price to Book': f"{price_to_book:.2f}x" if price_to_book != 'N/A' else 'N/A',
        'Beta': f"{beta:.2f}" if beta != 'N/A' else 'N/A',
        'Diluted EPS': f"{diluted_eps:.2f}" if diluted_eps != 'N/A' else 'N/A',
        'Profit Margin': f"{profit_margin:.2f}%" if profit_margin != 'N/A' else 'N/A',
        'Operating Margin': f"{operating_margin:.2f}%" if operating_margin != 'N/A' else 'N/A',
        'Return on Asset': f"{return_on_assets:.2f}%" if return_on_assets != 'N/A' else 'N/A',
        'Return on Equity': f"{return_on_equity:.2f}%" if return_on_equity != 'N/A' else 'N/A',
        'Earnings Yield': f"{earnings_yield:.2f}%" if earnings_yield != 'N/A' else 'N/A'
    }
    
    return statistics

# Function to fetch company details (sector and industry)
def fetch_company_details(stock):
    info = stock.info
    sector = safe_get(info, 'sector')
    industry = safe_get(info, 'industry')
    return sector, industry

# Function to display financial statements in tables
def display_financial_statements(stock):
    # Display balance sheet
    st.subheader("Balance Sheet")
    st.dataframe(stock.balance_sheet.T)
    
    # Display income statement
    st.subheader("Income Statement")
    st.dataframe(stock.financials.T)
    
    # Display cash flow statement
    st.subheader("Cash Flow Statement")
    st.dataframe(stock.cashflow.T)

# Main Streamlit App
def main():
    # Parse tickers input from the sidebar
    tickers = tickers_input.split(",")
    
    # Set up a session with custom headers to avoid 401 Unauthorized errors
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'})
    
    for ticker in tickers:
        ticker = ticker.strip()  # Clean ticker input
        
        # Fetch stock data
        stock_data = fetch_stock_data(ticker, start_date=start_date.strftime("%Y-%m-%d"), session=session)
        
        # Fetch market index data
        market_data = fetch_stock_data(market_ticker_input, start_date=start_date.strftime("%Y-%m-%d"), session=session)
        
        # Display stock data
        if not stock_data.empty and not market_data.empty:
            st.subheader(f"Stock Price Data for {ticker} and Market Returns ({market_ticker_input})")
            
            # Normalize both stock and market data for comparison
            stock_data['Normalized'] = stock_data['Close'] / stock_data['Close'].iloc[0] * 100
            market_data['Normalized'] = market_data['Close'] / market_data['Close'].iloc[0] * 100
            
            # Plot both stock and market returns on the same chart
            plt.figure(figsize=(10, 6))
            plt.plot(stock_data.index, stock_data['Normalized'], label=f"{ticker} Returns", color='blue')
            plt.plot(market_data.index, market_data['Normalized'], label=f"{market_ticker_input} Returns", color='red')
            plt.title(f"Stock vs Market Returns: {ticker} vs {market_ticker_input}")
            plt.xlabel("Date")
            plt.ylabel("Normalized Price (%)")
            plt.legend()
            st.pyplot(plt)
        
            # Fetch stock info and statistics
            stock = yf.Ticker(ticker, session=session)
            statistics = fetch_yahoo_finance_statistics(stock)
            
            # Fetch company details
            sector, industry = fetch_company_details(stock)
        
            # Display company details
            st.subheader(f"Company Details for {ticker}")
            st.write(f"**Sector:** {sector}")
            st.write(f"**Industry:** {industry}")
        
            # Display key statistics in metric cards
            st.subheader(f"Key Financial Statistics for {ticker}")
            cols = st.columns(3)
            
            # Display metrics using custom CSS as metric cards
            for idx, (key, value) in enumerate(statistics.items()):
                col = cols[idx % 3]
                col.markdown(f"""
                <div class="metric-card">
                    <h3>{key}</h3>
                    <div class="value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

            # Display financial statements
            display_financial_statements(stock)

        else:
            st.error(f"No data found for {ticker} or {market_ticker_input}.")

if __name__ == "__main__":
    main()

