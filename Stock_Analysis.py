import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import requests

# Function to fetch stock data using yfinance
def fetch_stock_data(symbol, start_date='2020-01-01', session=None):
    stock = yf.Ticker(symbol, session=session)
    df = stock.history(start=start_date)
    return df

# Function to calculate key financial ratios
def calculate_ratios(stock):
    info = stock.info
    financials = stock.financials
    balance_sheet = stock.balance_sheet
    cashflow = stock.cashflow
    
    # Profitability Ratios
    pe_ratio = info.get('trailingPE', None)
    roe = info.get('returnOnEquity', None)
    gross_profit = financials.loc['Gross Profit'].iloc[0] if 'Gross Profit' in financials else None
    revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials else None
    net_income = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials else None
    total_assets = balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in balance_sheet else None
    gross_profit_margin = (gross_profit / revenue) * 100 if gross_profit and revenue else None
    net_profit_margin = (net_income / revenue) * 100 if net_income and revenue else None
    roa = (net_income / total_assets) * 100 if net_income and total_assets else None
    
    # Liquidity Ratios
    current_assets = balance_sheet.loc['Total Current Assets'].iloc[0] if 'Total Current Assets' in balance_sheet else None
    current_liabilities = balance_sheet.loc['Total Current Liabilities'].iloc[0] if 'Total Current Liabilities' in balance_sheet else None
    current_ratio = current_assets / current_liabilities if current_assets and current_liabilities else None
    inventory = balance_sheet.loc['Inventory'].iloc[0] if 'Inventory' in balance_sheet else None
    quick_ratio = (current_assets - inventory) / current_liabilities if current_assets and inventory and current_liabilities else None
    
    # Solvency Ratios
    total_debt = balance_sheet.loc['Total Debt'].iloc[0] if 'Total Debt' in balance_sheet else None
    shareholders_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[0] if 'Total Stockholder Equity' in balance_sheet else None
    debt_to_equity = total_debt / shareholders_equity if total_debt and shareholders_equity else None
    interest_expense = cashflow.loc['Interest Expense'].iloc[0] if 'Interest Expense' in cashflow else None
    ebit = financials.loc['EBIT'].iloc[0] if 'EBIT' in financials else None
    interest_coverage = ebit / interest_expense if ebit and interest_expense else None
    
    # Valuation Ratios
    market_price = info.get('regularMarketPrice', None)
    book_value = info.get('bookValue', None)
    pb_ratio = market_price / book_value if market_price and book_value else None
    dividend_yield = info.get('dividendYield', None) * 100 if info.get('dividendYield') else None
    earnings_yield = (1 / pe_ratio) * 100 if pe_ratio else None
    
    # Efficiency Ratios
    cogs = financials.loc['Cost Of Revenue'].iloc[0] if 'Cost Of Revenue' in financials else None
    inventory_turnover = cogs / inventory if cogs and inventory else None
    asset_turnover = revenue / total_assets if revenue and total_assets else None
    
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
    st.title("Stock Fundamental Analysis Dashboard")
    
    # User input for stock symbol
    symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, GOOGL, NISP.JK):", value="NISP.JK")
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
    
        # Display financial ratios with a box design
        st.subheader("Financial Ratios")
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                for ratio, value in list(ratios.items())[:8]:
                    st.markdown(f"**{ratio}**: {value if value else 'N/A'}")
            
            with col2:
                for ratio, value in list(ratios.items())[8:]:
                    st.markdown(f"**{ratio}**: {value if value else 'N/A'}")
                
    else:
        st.error("No data found for the given symbol.")

if __name__ == "__main__":
    main()
