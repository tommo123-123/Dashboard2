import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import numpy as np

# Page config
st.set_page_config(page_title="Financial Markets Dashboard", layout="wide")

# Header
st.title("Financial Markets Dashboard")
st.markdown(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Market Overview", "Stock Analysis", "Sector Performance", "Economic Indicators"])

# Function to get stock data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol, period="1d"):
    try:
        data = yf.Ticker(symbol)
        return data.info, data.history(period=period)
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return {}, pd.DataFrame()

# Function to get historical data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_historical_data(symbol, period="1y", interval="1d"):
    try:
        data = yf.download(symbol, period=period, interval=interval)
        return data
    except Exception as e:
        st.error(f"Error fetching historical data for {symbol}: {e}")
        return pd.DataFrame()

# Market Overview Tab
with tab1:
    st.header("Market Overview")
    
    # Major Indices
    indices_col1, indices_col2 = st.columns(2)
    
    with indices_col1:
        st.subheader("Major US Indices")
        indices = [
            {"symbol": "^GSPC", "name": "S&P 500"},
            {"symbol": "^DJI", "name": "Dow Jones Industrial Avg"},
            {"symbol": "^IXIC", "name": "Nasdaq Composite"},
            {"symbol": "^RUT", "name": "Russell 2000"}
        ]
        
        for index in indices:
            info, data = get_stock_data(index["symbol"])
            if not data.empty:
                price = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2] if len(data) > 1 else info.get('previousClose', price)
                change_percent = ((price - prev_close) / prev_close) * 100
                
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.text(index["name"])
                with col2:
                    st.text(f"${price:.2f}")
                with col3:
                    if change_percent >= 0:
                        st.markdown(f"<span style='color:green'>▲ {change_percent:.2f}%</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color:red'>▼ {abs(change_percent):.2f}%</span>", unsafe_allow_html=True)
                st.divider()
    
    with indices_col2:
        st.subheader("International & Volatility")
        international_indices = [
            {"symbol": "^FTSE", "name": "FTSE 100 (UK)"},
            {"symbol": "^N225", "name": "Nikkei 225 (Japan)"},
            {"symbol": "^VIX", "name": "Volatility Index"},
            {"symbol": "GC=F", "name": "Gold Futures"}
        ]
        
        for index in international_indices:
            info, data = get_stock_data(index["symbol"])
            if not data.empty:
                price = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2] if len(data) > 1 else info.get('previousClose', price)
                change_percent = ((price - prev_close) / prev_close) * 100
                
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.text(index["name"])
                with col2:
                    st.text(f"${price:.2f}")
                with col3:
                    # For VIX, rising is usually considered negative
                    if index["symbol"] == "^VIX":
                        if change_percent >= 0:
                            st.markdown(f"<span style='color:red'>▲ {change_percent:.2f}%</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span style='color:green'>▼ {abs(change_percent):.2f}%</span>", unsafe_allow_html=True)
                    else:
                        if change_percent >= 0:
                            st.markdown(f"<span style='color:green'>▲ {change_percent:.2f}%</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span style='color:red'>▼ {abs(change_percent):.2f}%</span>", unsafe_allow_html=True)
                st.divider()
    
    # Market Performance Chart
    st.subheader("S&P 500 Performance - Last 100 Trading Days")
    
    # Get historical data for S&P 500
    spy_hist = get_historical_data("^GSPC", period="100d")
    
    if not spy_hist.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(spy_hist.index, spy_hist['Close'])
        ax.set_xlabel('Date')
        ax.set_ylabel('S&P 500 Price ($)')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig)
    
    # Sector Performance
    st.subheader("Sector Performance (Today)")
    sectors = [
        {"symbol": "XLK", "name": "Technology"},
        {"symbol": "XLF", "name": "Financials"},
        {"symbol": "XLV", "name": "Healthcare"},
        {"symbol": "XLE", "name": "Energy"},
        {"symbol": "XLY", "name": "Consumer Discretionary"},
        {"symbol": "XLP", "name": "Consumer Staples"},
        {"symbol": "XLI", "name": "Industrials"},
        {"symbol": "XLB", "name": "Materials"},
        {"symbol": "XLU", "name": "Utilities"},
        {"symbol": "XLRE", "name": "Real Estate"},
    ]
    
    sector_data = []
    for sector in sectors:
        info, data = get_stock_data(sector["symbol"])
        if not data.empty:
            price = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2] if len(data) > 1 else info.get('previousClose', price)
            change_percent = ((price - prev_close) / prev_close) * 100
            sector_data.append({"Sector": sector["name"], "Change (%)": change_percent})
    
    if sector_data:
        sector_df = pd.DataFrame(sector_data)
        sector_df = sector_df.sort_values("Change (%)", ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['green' if x >= 0 else 'red' for x in sector_df["Change (%)"]]
        ax.bar(sector_df["Sector"], sector_df["Change (%)"], color=colors)
        ax.set_xlabel('Sector')
        ax.set_ylabel('Change (%)')
        ax.set_title('Sector Performance')
        plt.xticks(rotation=45, ha='right')
        fig.tight_layout()
        st.pyplot(fig)

# Stock Analysis Tab
with tab2:
    st.header("Stock Analysis")
    
    # Stock selector
    stock_symbol = st.text_input("Enter Stock Symbol", "AAPL").upper()
    
    if stock_symbol:
        col1, col2 = st.columns([2, 1])
        
        # Current stock data
        info, stock_data = get_stock_data(stock_symbol)
        
        if not stock_data.empty and info:
            with col1:
                price = stock_data['Close'].iloc[-1]
                prev_close = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else info.get('previousClose', price)
                change = price - prev_close
                change_percent = (change / prev_close) * 100
                
                st.subheader(f"{stock_symbol} - ${price:.2f}")
                
                if change >= 0:
                    st.markdown(f"<span style='color:green; font-size:1.5em'>▲ ${change:.2f} ({change_percent:.2f}%)</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:red; font-size:1.5em'>▼ ${abs(change):.2f} ({change_percent:.2f}%)</span>", unsafe_allow_html=True)
                
                # Trading metrics
                st
