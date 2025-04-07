import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import datetime
import time
import sys
print(f"Python version: {sys.version}")
print("Attempting to import plotly...")
try:
    import plotly
    print(f"Plotly version: {plotly.__version__}")
    import plotly.graph_objects as go
    import plotly.express as px
    print("Plotly imports successful")
except Exception as e:
    print(f"Error importing plotly: {str(e)}")
    
# Continue with rest of imports
import streamlit as st
import pandas as pd
# etc.

# Page config
st.set_page_config(page_title="Financial Markets Dashboard", layout="wide")

# Your Alpha Vantage API key
API_KEY = 'ZISA2SI7EXPU3H7X'  # Using single quotes instead  # Set this in Streamlit Cloud secrets

# Initialize Alpha Vantage clients
ts = TimeSeries(key=API_KEY, output_format='pandas')
fd = FundamentalData(key=API_KEY, output_format='pandas')

# Header
st.title("Financial Markets Dashboard")
st.markdown(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Market Overview", "Stock Analysis", "Sector Performance", "Economic Indicators"])

# Function to get stock data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol):
    try:
        data, meta_data = ts.get_quote_endpoint(symbol=symbol)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

# Function to get historical data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_historical_data(symbol, interval='daily'):
    try:
        if interval == 'daily':
            data, meta_data = ts.get_daily(symbol=symbol, outputsize='compact')
        elif interval == 'weekly':
            data, meta_data = ts.get_weekly(symbol=symbol)
        elif interval == 'monthly':
            data, meta_data = ts.get_monthly(symbol=symbol)
        return data
    except Exception as e:
        st.error(f"Error fetching historical data for {symbol}: {e}")
        return pd.DataFrame()

# Function to get company overview
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_company_overview(symbol):
    try:
        data, meta_data = fd.get_company_overview(symbol=symbol)
        return data
    except Exception as e:
        st.error(f"Error fetching company overview for {symbol}: {e}")
        return pd.DataFrame()

# Market Overview Tab
with tab1:
    st.header("Market Overview")
    
    # Major Indices
    indices_col1, indices_col2 = st.columns(2)
    
    with indices_col1:
        st.subheader("Major US Indices")
        indices = [
            {"symbol": "SPY", "name": "S&P 500 ETF"},
            {"symbol": "DIA", "name": "Dow Jones Industrial Avg ETF"},
            {"symbol": "QQQ", "name": "Nasdaq-100 ETF"},
            {"symbol": "IWM", "name": "Russell 2000 ETF"}
        ]
        
        for index in indices:
            data = get_stock_data(index["symbol"])
            if not data.empty:
                price = float(data['05. price'][0])
                change_percent = float(data['10. change percent'][0].strip('%'))
                
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
            {"symbol": "VGK", "name": "European Markets ETF"},
            {"symbol": "EWJ", "name": "Japan Markets ETF"},
            {"symbol": "VIX", "name": "Volatility Index"},
            {"symbol": "GLD", "name": "Gold ETF"}
        ]
        
        for index in international_indices:
            data = get_stock_data(index["symbol"])
            if not data.empty:
                price = float(data['05. price'][0])
                change_percent = float(data['10. change percent'][0].strip('%'))
                
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.text(index["name"])
                with col2:
                    st.text(f"${price:.2f}")
                with col3:
                    # For VIX, rising is usually considered negative
                    if index["symbol"] == "VIX":
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
    st.subheader("Market Performance - Last 100 Trading Days")
    
    # Get historical data for SPY
    spy_hist = get_historical_data("SPY")
    
    if not spy_hist.empty:
        fig = px.line(spy_hist.iloc[-100:], y='4. close', labels={'y': 'Price ($)', 'x': 'Date'})
        fig.update_layout(height=400, xaxis_title="Date", yaxis_title="S&P 500 ETF Price ($)")
        st.plotly_chart(fig, use_container_width=True)
    
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
        data = get_stock_data(sector["symbol"])
        if not data.empty:
            change_percent = float(data['10. change percent'][0].strip('%'))
            sector_data.append({"Sector": sector["name"], "Change (%)": change_percent})
    
    if sector_data:
        sector_df = pd.DataFrame(sector_data)
        sector_df = sector_df.sort_values("Change (%)", ascending=False)
        
        fig = px.bar(sector_df, x="Sector", y="Change (%)", 
                    color="Change (%)", 
                    color_continuous_scale=["red", "lightgray", "green"],
                    range_color=[-max(abs(sector_df["Change (%)"])), max(abs(sector_df["Change (%)"]))])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# Stock Analysis Tab
with tab2:
    st.header("Stock Analysis")
    
    # Stock selector
    stock_symbol = st.text_input("Enter Stock Symbol", "AAPL").upper()
    
    if stock_symbol:
        col1, col2 = st.columns([2, 1])
        
        # Current stock data
        stock_data = get_stock_data(stock_symbol)
        
        if not stock_data.empty:
            with col1:
                price = float(stock_data['05. price'][0])
                change = float(stock_data['09. change'][0])
                change_percent = float(stock_data['10. change percent'][0].strip('%'))
                
                st.subheader(f"{stock_symbol} - ${price:.2f}")
                
                if change >= 0:
                    st.markdown(f"<span style='color:green; font-size:1.5em'>▲ ${change:.2f} ({change_percent:.2f}%)</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:red; font-size:1.5em'>▼ ${abs(change):.2f} ({change_percent:.2f}%)</span>", unsafe_allow_html=True)
                
                # Trading metrics
                st.markdown("**Trading Information**")
                trading_info = {
                    "Open": f"${float(stock_data['02. open'][0]):.2f}",
                    "High": f"${float(stock_data['03. high'][0]):.2f}",
                    "Low": f"${float(stock_data['04. low'][0]):.2f}",
                    "Volume": f"{int(float(stock_data['06. volume'][0])):,}",
                    "Latest Trading Day": stock_data['07. latest trading day'][0]
                }
                
                for key, value in trading_info.items():
                    st.text(f"{key}: {value}")
        
            # Company overview
            with col2:
                company_data = get_company_overview(stock_symbol)
                
                if not company_data.empty:
                    st.markdown("**Company Overview**")
                    
                    if 'Name' in company_data:
                        st.markdown(f"**{company_data['Name'][0]}**")
                    
                    if 'Sector' in company_data and 'Industry' in company_data:
                        st.text(f"Sector: {company_data['Sector'][0]}")
                        st.text(f"Industry: {company_data['Industry'][0]}")
                    
                    if 'MarketCapitalization' in company_data:
                        market_cap = float(company_data['MarketCapitalization'][0])
                        if market_cap >= 1e12:
                            formatted_cap = f"${market_cap/1e12:.2f}T"
                        elif market_cap >= 1e9:
                            formatted_cap = f"${market_cap/1e9:.2f}B"
                        elif market_cap >= 1e6:
                            formatted_cap = f"${market_cap/1e6:.2f}M"
                        else:
                            formatted_cap = f"${market_cap:.2f}"
                        st.text(f"Market Cap: {formatted_cap}")
                    
                    if 'PERatio' in company_data:
                        st.text(f"P/E Ratio: {company_data['PERatio'][0]}")
                    
                    if 'DividendYield' in company_data:
                        dividend_yield = float(company_data['DividendYield'][0]) * 100 if company_data['DividendYield'][0] else 0
                        st.text(f"Dividend Yield: {dividend_yield:.2f}%")
        
        # Historical data visualization
        st.subheader("Historical Performance")
        
        # Time period selection
        time_period = st.radio("Select Time Period", ["Daily (3 Months)", "Weekly (1 Year)", "Monthly (5 Years)"], horizontal=True)
        
        if time_period == "Daily (3 Months)":
            hist_data = get_historical_data(stock_symbol, 'daily')
            hist_data = hist_data.iloc[-90:] if not hist_data.empty else hist_data
        elif time_period == "Weekly (1 Year)":
            hist_data = get_historical_data(stock_symbol, 'weekly')
            hist_data = hist_data.iloc[-52:] if not hist_data.empty else hist_data
        else:
            hist_data = get_historical_data(stock_symbol, 'monthly')
            hist_data = hist_data.iloc[-60:] if not hist_data.empty else hist_data
        
        if not hist_data.empty:
            # Candlestick chart
            fig = go.Figure(data=[go.Candlestick(
                x=hist_data.index,
                open=hist_data['1. open'],
                high=hist_data['2. high'],
                low=hist_data['3. low'],
                close=hist_data['4. close'],
                name=stock_symbol
            )])
            
            fig.update_layout(
                title=f'{stock_symbol} Stock Price',
                xaxis_title='Date',
                yaxis_title='Price ($)',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            volume_fig = px.bar(hist_data, x=hist_data.index, y='5. volume', title=f'{stock_symbol} Trading Volume')
            volume_fig.update_layout(height=300, xaxis_title="Date", yaxis_title="Volume")
            st.plotly_chart(volume_fig, use_container_width=True)

# Sector Performance Tab
with tab3:
    st.header("Sector Performance")
    
    # Get historical data for sector ETFs
    sector_etfs = [
        {"symbol": "XLK", "name": "Technology", "color": "#2166ac"},
        {"symbol": "XLF", "name": "Financials", "color": "#4393c3"},
        {"symbol": "XLV", "name": "Healthcare", "color": "#92c5de"},
        {"symbol": "XLE", "name": "Energy", "color": "#d6604d"},
        {"symbol": "XLY", "name": "Consumer Discretionary", "color": "#f4a582"},
        {"symbol": "XLP", "name": "Consumer Staples", "color": "#fddbc7"},
    ]
    
    # Time period selection
    period = st.radio("Select Time Period", ["1 Month", "3 Months", "6 Months", "1 Year"], horizontal=True)
    
    lookback_days = {
        "1 Month": 30,
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 365
    }
    
    # Calculate performance
    performance_data = []
    
    for etf in sector_etfs:
        hist_data = get_historical_data(etf["symbol"], 'daily')
        
        if not hist_data.empty:
            # Filter based on selected time period
            hist_data = hist_data.iloc[-lookback_days[period]:] if len(hist_data) >= lookback_days[period] else hist_data
            
            # Calculate percentage change from first day
            if len(hist_data) > 0:
                first_price = hist_data.iloc[0]['4. close']
                normalized_prices = hist_data['4. close'] / first_price * 100 - 100
                
                for date, price_change in zip(hist_data.index, normalized_prices):
                    performance_data.append({
                        "Date": date,
                        "Sector": etf["name"],
                        "Performance (%)": price_change,
                        "Color": etf["color"]
                    })
    
    if performance_data:
        performance_df = pd.DataFrame(performance_data)
        
        # Create line chart
        fig = px.line(performance_df, x="Date", y="Performance (%)", 
                     color="Sector", 
                     title=f"Sector Performance - Past {period}",
                     color_discrete_map={sector["name"]: sector["color"] for sector in sector_etfs})
        
        fig.update_layout(height=600, xaxis_title="Date", yaxis_title="Performance (%)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Current performance table
        st.subheader(f"Current Sector Performance ({period})")
        
        # Get the most recent date for each sector
        latest_performance = performance_df.groupby("Sector").last().reset_index()
        latest_performance = latest_performance.sort_values("Performance (%)", ascending=False)
        
        # Create a styled dataframe
        performance_styler = pd.DataFrame({
            "Sector": latest_performance["Sector"],
            "Performance (%)": latest_performance["Performance (%)"].round(2)
        }).style.format({"Performance (%)": "{:.2f}%"})
        
        # Apply color based on performance
        def color_performance(val):
            color = 'green' if val > 0 else 'red'
            return f'color: {color}'
        
        performance_styler = performance_styler.applymap(color_performance, subset=['Performance (%)'])
        
        st.dataframe(performance_styler, use_container_width=True)

# Economic Indicators Tab
with tab4:
    st.header("Economic Indicators")
    
    st.info("This tab would typically show economic indicators like Treasury yields, unemployment data, and inflation metrics. However, these require additional API calls that would exceed free tier limits.")
    
    st.subheader("Recommended Economic Indicators to Track")
    
    indicators = [
        {"name": "Treasury Yields (10Y, 2Y)", "importance": "High", "frequency": "Daily", "source": "Alpha Vantage (Premium)"},
        {"name": "Unemployment Rate", "importance": "High", "frequency": "Monthly", "source": "BLS/FRED API"},
        {"name": "Consumer Price Index (CPI)", "importance": "High", "frequency": "Monthly", "source": "BLS/FRED API"},
        {"name": "GDP Growth Rate", "importance": "Medium", "frequency": "Quarterly", "source": "BEA/FRED API"},
        {"name": "Fed Funds Rate", "importance": "High", "frequency": "As changes occur", "source": "Federal Reserve/FRED API"},
        {"name": "Housing Starts", "importance": "Medium", "frequency": "Monthly", "source": "Census Bureau/FRED API"},
        {"name": "Retail Sales", "importance": "Medium", "frequency": "Monthly", "source": "Census Bureau/FRED API"},
        {"name": "ISM Manufacturing Index", "importance": "Medium", "frequency": "Monthly", "source": "ISM/FRED API"},
    ]
    
    indicators_df = pd.DataFrame(indicators)
    st.dataframe(indicators_df, use_container_width=True)
    
    st.markdown("""
    **Upgrade Options:**
    
    - Use the FRED API (Federal Reserve Economic Data) for economic indicators
    - Upgrade Alpha Vantage subscription for economic indicators and intraday data
    - Consider alternative data providers like Yahoo Finance API or Financial Modeling Prep
    """)

# Auto-refresh mechanism
st.sidebar.header("Dashboard Controls")
if st.sidebar.button('Refresh Data'):
    st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("Data automatically refreshes every 5 minutes.")
st.sidebar.markdown("Last update: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
st.sidebar.markdown("---")
st.sidebar.markdown("Data provided by Alpha Vantage")
