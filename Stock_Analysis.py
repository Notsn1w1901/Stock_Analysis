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

# Function to fetch stock data using yfinance
def fetch_stock_data(symbol, start_date='2020-01-01', session=None):
    stock = yf.Ticker(symbol, session=session)
    df = stock.history(start=start_date)
    return df

# Safe method to handle missing data
def safe_get(data, key):
    return data.get(key, None) if key in data else None

# Function to calculate key financial ratios
def calculate_ratios(stock):
    info = stock.info
    financials = stock.financials
    balance_sheet = stock.balance_sheet
    cashflow = stock.cashflow
    
    # Profitability Ratios
    pe_ratio = safe_get(info, 'trailingPE')
    roe = safe_get(info, 'returnOnEquity')
    gross_profit = financials.loc['Gross Profit'].iloc[0] if 'Gross Profit' in financials else None
    revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials else None
    net_income = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials else None
    total_assets = balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in balance_sheet else None
    
    gross_profit_margin = (gross_profit / revenue) * 100 if gross_profit and revenue else 'Data Missing'
    net_profit_margin = (net_income / revenue) * 100 if net_income and revenue else 'Data Missing'
    roa = (net_income / total_assets) * 100 if net_income and total_assets else 'Data Missing'
    
    # Liquidity Ratios
    current_assets = balance_sheet.loc['Total Current Assets'].iloc[0] if 'Total Current Assets' in balance_sheet else None
    current_liabilities = balance_sheet.loc['Total Current Liabilities'].iloc[0] if 'Total Current Liabilities' in balance_sheet else None
    current_ratio = current_assets / current_liabilities if current_assets and current_liabilities else 'Data Missing'
    inventory = balance_sheet.loc['Inventory'].iloc[0] if 'Inventory' in balance_sheet else None
    quick_ratio = (current_assets - inventory) / current_liabilities if current_assets and inventory and current_liabilities else 'Data Missing'
    
    # Solvency Ratios
    total_debt = balance_sheet.loc['Total Debt'].iloc[0] if 'Total Debt' in balance_sheet else None
    shareholders_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[0] if 'Total Stockholder Equity' in balance_sheet else None
    debt_to_equity = total_debt / shareholders_equity if total_debt and shareholders_equity else 'Data Missing'
    interest_expense = cashflow.loc['Interest Expense'].iloc[0] if 'Interest Expense' in cashflow else None
    ebit = financials.loc['EBIT'].iloc[0] if 'EBIT' in financials else None
    interest_coverage = ebit / interest_expense if ebit and interest_expense else 'Data Missing'
    
    # Valuation Ratios
    market_price = safe_get(info, 'regularMarketPrice')
    book_value = safe_get(info, 'bookValue')
    pb_ratio = market_price / book_value if market_price and book_value else 'Data Missing'
    dividend_yield = safe_get(info, 'dividendYield') * 100 if safe_get(info, 'dividendYield') else 'Data Missing'
    earnings_yield = (1 / pe_ratio) * 100 if pe_ratio else 'Data Missing'
    
    # Efficiency Ratios
    cogs = financials.loc['Cost Of Revenue'].iloc[0] if 'Cost Of Revenue' in financials else None
    inventory_turnover = cogs / inventory if cogs and inventory else 'Data Missing'
    asset_turnover = revenue / total_assets if revenue and total_assets else 'Data Missing'
    
    return {
        'PE Ratio': pe_ratio,
        'Debt to Equity': debt_to_equity,
        'ROE': roe,
        'Gross Profit Margin': gross_profit_margin,
        'Net Profit Margin': net_profit_margin,
        'ROA': roa,
        'Current Ratio': current_ratio,
        'Quick Ratio': quick_ratio,
        'Interest Coverage Ratio': interest_coverage,
        'P/B Ratio': pb_ratio,
        'Dividend Yield': dividend_yield,
        'Earnings Yield': earnings_yield,
        'Inventory Turnover': inventory_turnover,
        'Asset Turnover': asset_turnover
    }

# Main Streamlit App
def main():
    # User input for stock symbol
    symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, GOOGL, BBCA.JK):", value="BBCA.JK")
    start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
    
    # Set up a session with custom headers to avoid 401 Unauthorized errors
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'})
    
    # Fetch stock data
    stock_data = fetch_stock_data(symbol, start_date=start_date.strftime("%Y-%m-%d"), session=session)
    
    # Display stock data
    if not stock_data.empty:
        st.subheader("Stock Price Data")
        st.line_chart(stock_data['Close'])
    
        # Fetch stock info and calculate ratios
        stock = yf.Ticker(symbol, session=session)
        ratios = calculate_ratios(stock)
    
        # Display financial ratios in metric cards
        st.subheader("Financial Ratios")
        cols = st.columns(3)
        
        # Display ratios with custom CSS as metric cards
        ratios_dict = {
            "PE Ratio": ratios['PE Ratio'],
            "Debt to Equity": ratios['Debt to Equity'],
            "ROE": ratios['ROE'],
            "Gross Profit Margin": ratios['Gross Profit Margin'],
            "Net Profit Margin": ratios['Net Profit Margin'],
            "ROA": ratios['ROA'],
            "Current Ratio": ratios['Current Ratio'],
            "Quick Ratio": ratios['Quick Ratio'],
            "Interest Coverage Ratio": ratios['Interest Coverage Ratio'],
            "P/B Ratio": ratios['P/B Ratio'],
            "Dividend Yield": ratios['Dividend Yield'],
            "Earnings Yield": ratios['Earnings Yield'],
            "Inventory Turnover": ratios['Inventory Turnover'],
            "Asset Turnover": ratios['Asset Turnover']
        }
        
        for idx, (key, value) in enumerate(ratios_dict.items()):
            col = cols[idx % 3]
            col.markdown(f"""
            <div class="metric-card">
                <h3>{key}</h3>
                <div class="value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.error("No data found for the given symbol.")

if __name__ == "__main__":
    main()
