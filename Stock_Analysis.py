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

# Function to fetch stock data using yfinance
def fetch_stock_data(symbol, start_date='2020-01-01', session=None):
    stock = yf.Ticker(symbol, session=session)
    df = stock.history(start=start_date)
    return df

# Safe method to handle missing data
def safe_get(data, key, default_value='N/A'):
    return data.get(key, default_value)

# Function to calculate key financial ratios based on the financial statements
def calculate_ratios(stock):
    # Fetch the financial statements (balance sheet, income statement, cash flow statement)
    balance_sheet = stock.balance_sheet.T  # Transpose for better readability
    financials = stock.financials.T  # Income statement
    cashflow = stock.cashflow.T  # Cash flow statement
    
    # Check if financials have columns and rows
    if financials.empty:
        return "Financial data not available"
    
    # Get the most recent year available in the financials data
    recent_year = financials.columns[0] if len(financials.columns) > 0 else None
    if not recent_year:
        return "No data available"

    # Accessing data from financial statements (balance sheet and income statement)
    gross_profit = financials.loc['Gross Profit', recent_year] if 'Gross Profit' in financials else 'N/A'
    revenue = financials.loc['Total Revenue', recent_year] if 'Total Revenue' in financials else 'N/A'
    net_income = financials.loc['Net Income', recent_year] if 'Net Income' in financials else 'N/A'
    total_assets = balance_sheet.loc['Total Assets', recent_year] if 'Total Assets' in balance_sheet else 'N/A'
    
    # Calculate profitability ratios (Ensure there's no division by zero)
    gross_profit_margin = (gross_profit / revenue) * 100 if gross_profit != 'N/A' and revenue != 'N/A' else 'N/A'
    net_profit_margin = (net_income / revenue) * 100 if net_income != 'N/A' and revenue != 'N/A' else 'N/A'
    roa = (net_income / total_assets) * 100 if net_income != 'N/A' and total_assets != 'N/A' else 'N/A'
    
    # Liquidity Ratios
    current_assets = balance_sheet.loc['Total Current Assets', recent_year] if 'Total Current Assets' in balance_sheet else 'N/A'
    current_liabilities = balance_sheet.loc['Total Current Liabilities', recent_year] if 'Total Current Liabilities' in balance_sheet else 'N/A'
    inventory = balance_sheet.loc['Inventory', recent_year] if 'Inventory' in balance_sheet else 'N/A'
    
    # Current and Quick Ratios
    current_ratio = current_assets / current_liabilities if current_assets != 'N/A' and current_liabilities != 'N/A' else 'N/A'
    quick_ratio = (current_assets - inventory) / current_liabilities if current_assets != 'N/A' and inventory != 'N/A' and current_liabilities != 'N/A' else 'N/A'
    
    # Solvency Ratios
    total_debt = balance_sheet.loc['Total Debt', recent_year] if 'Total Debt' in balance_sheet else 'N/A'
    shareholders_equity = balance_sheet.loc['Total Stockholder Equity', recent_year] if 'Total Stockholder Equity' in balance_sheet else 'N/A'
    debt_to_equity = total_debt / shareholders_equity if total_debt != 'N/A' and shareholders_equity != 'N/A' else 'N/A'
    
    # Interest coverage ratio
    ebit = financials.loc['EBIT', recent_year] if 'EBIT' in financials else 'N/A'
    interest_expense = cashflow.loc['Interest Expense', recent_year] if 'Interest Expense' in cashflow else 'N/A'
    interest_coverage = ebit / interest_expense if ebit != 'N/A' and interest_expense != 'N/A' else 'N/A'
    
    # Valuation Ratios
    market_price = safe_get(stock.info, 'regularMarketPrice')
    book_value = safe_get(stock.info, 'bookValue')
    pb_ratio = market_price / book_value if market_price != 'N/A' and book_value != 'N/A' else 'N/A'
    dividend_yield = safe_get(stock.info, 'dividendYield') * 100 if safe_get(stock.info, 'dividendYield') != 'N/A' else 'N/A'
    earnings_yield = (1 / pe_ratio) * 100 if pe_ratio != 'N/A' else 'N/A'
    
    # Efficiency Ratios
    cogs = financials.loc['Cost Of Revenue', recent_year] if 'Cost Of Revenue' in financials else 'N/A'
    inventory_turnover = cogs / inventory if cogs != 'N/A' and inventory != 'N/A' else 'N/A'
    asset_turnover = revenue / total_assets if revenue != 'N/A' and total_assets != 'N/A' else 'N/A'
    
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
        
        # Display stock data
        if not stock_data.empty:
            st.subheader(f"Stock Price Data for {ticker}")
            st.line_chart(stock_data['Close'])
        
            # Fetch stock info and calculate ratios
            stock = yf.Ticker(ticker, session=session)
            ratios = calculate_ratios(stock)
            
            # Fetch company details
            sector, industry = fetch_company_details(stock)
        
            # Display company details
            st.subheader(f"Company Details for {ticker}")
            st.write(f"**Sector:** {sector}")
            st.write(f"**Industry:** {industry}")
        
            # Display financial ratios in metric cards
            st.subheader(f"Financial Ratios for {ticker}")
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

            # Display financial statements
            display_financial_statements(stock)

        else:
            st.error(f"No data found for {ticker}.")

if __name__ == "__main__":
    main()
