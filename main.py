import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="MAG7 + SPY Options Dashboard", layout="wide")

# Cache duration in hours
CACHE_DURATION_HOURS = 2

# Tickers including SPY
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "SPY"]

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main title styling */
    h1 {
        color: #1f2937;
        padding-bottom: 1rem;
        border-bottom: 3px solid #3b82f6;
        margin-bottom: 2rem;
    }
    
    /* Remove extra padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Selectbox styling */
    .stSelectbox > label {
        font-weight: 600;
        font-size: 1rem;
        color: #374151;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f2937;
    }
    
    /* Dataframe styling */
    .dataframe {
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 MAG7 + SPY Options Dashboard")

# ---------------------------------------------------------------
# Session State Setup
# ---------------------------------------------------------------
if "cache" not in st.session_state:
    st.session_state.cache = {}

if "fetch_times" not in st.session_state:
    st.session_state.fetch_times = {}

# ---------------------------------------------------------------
# Ticker & Expiry Selection
# ---------------------------------------------------------------
col_a, col_b = st.columns([1, 1])

with col_a:
    stock = st.selectbox("📈 Select Stock", TICKERS)

# Get available expiries
t = yf.Ticker(stock)
expiries = t.options

with col_b:
    expiry = st.selectbox("📅 Select Expiry Date", expiries)

# ---------------------------------------------------------------
# Fetch Data (with caching to avoid redundant fetches)
# ---------------------------------------------------------------
cache_key = f"{stock}_{expiry}"

# Check if cache exists and is still valid (within 2 hours)
cache_valid = False
if cache_key in st.session_state.cache and cache_key in st.session_state.fetch_times:
    time_since_fetch = datetime.now() - st.session_state.fetch_times[cache_key]
    cache_valid = time_since_fetch < timedelta(hours=CACHE_DURATION_HOURS)

if not cache_valid:
    with st.spinner(f"Fetching options data for {stock}..."):
        try:
            chain = t.option_chain(expiry)
            st.session_state.cache[cache_key] = {
                "calls": chain.calls,
                "puts": chain.puts,
            }
            st.session_state.fetch_times[cache_key] = datetime.now()
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.stop()

calls = st.session_state.cache[cache_key]["calls"]
puts = st.session_state.cache[cache_key]["puts"]
fetch_time = st.session_state.fetch_times[cache_key]

# ===============================================================
# SUMMARY SECTION
# ===============================================================
st.markdown("---")

# Header with timestamp
col_header1, col_header2 = st.columns([3, 1])
with col_header1:
    st.markdown(f"### Summary for **{stock}** — Expiry: **{expiry}**")
with col_header2:
    st.markdown(f"<div style='text-align: right; color: #6b7280; font-size: 0.9rem; margin-top: 0.5rem;'>🕐 Last pulled: {fetch_time.strftime('%I:%M:%S %p')}</div>", unsafe_allow_html=True)

calls_oi = int(calls["openInterest"].sum())
calls_vol = int(calls["volume"].sum())
puts_oi = int(puts["openInterest"].sum())
puts_vol = int(puts["volume"].sum())

col1, col2 = st.columns(2)

# Calls card — green
with col1:
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border: 2px solid #16a34a;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;">
            <div style="
                font-weight: 700; 
                font-size: 22px; 
                color: #15803d; 
                margin-bottom: 12px;
                display: flex;
                align-items: center;">
                <span style="margin-right: 8px;">📞</span> Calls
            </div>
            <div style="margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #374151; font-size: 15px;">Open Interest:</span>
                <span style="font-weight: 700; font-size: 18px; color: #15803d;">{calls_oi:,}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #374151; font-size: 15px;">Volume:</span>
                <span style="font-weight: 700; font-size: 18px; color: #15803d;">{calls_vol:,}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Puts card — red
with col2:
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            border: 2px solid #dc2626;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;">
            <div style="
                font-weight: 700; 
                font-size: 22px; 
                color: #b91c1c; 
                margin-bottom: 12px;
                display: flex;
                align-items: center;">
                <span style="margin-right: 8px;">📉</span> Puts
            </div>
            <div style="margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #374151; font-size: 15px;">Open Interest:</span>
                <span style="font-weight: 700; font-size: 18px; color: #b91c1c;">{puts_oi:,}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #374151; font-size: 15px;">Volume:</span>
                <span style="font-weight: 700; font-size: 18px; color: #b91c1c;">{puts_vol:,}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===============================================================
# DETAILED SECTION - CALLS TABLE
# ===============================================================
st.markdown("---")
st.markdown("### 📞 Calls Options Chain")

# Prepare calls data
base_cols = ['strike', 'lastPrice', 'volume', 'openInterest', 'impliedVolatility']
optional_cols = ['delta', 'theta', 'gamma', 'vega']

calls_cols = [col for col in base_cols + optional_cols if col in calls.columns]
calls_df = calls[calls_cols].copy()

# Rename columns
rename_map = {
    'strike': 'Strike',
    'lastPrice': 'Premium',
    'volume': 'Volume',
    'openInterest': 'OI',
    'impliedVolatility': 'IV'
}

for greek in optional_cols:
    if greek in calls_df.columns:
        rename_map[greek] = greek.capitalize()

calls_df = calls_df.rename(columns=rename_map)

# Sort controls for calls
col_c1, col_c2 = st.columns([2, 1])
with col_c1:
    calls_sort_col = st.selectbox(
        "Sort Calls by:",
        options=list(calls_df.columns),
        index=list(calls_df.columns).index('Strike'),
        key='calls_sort_col'
    )
with col_c2:
    calls_sort_order = st.selectbox(
        "Order:",
        options=['Low to High', 'High to Low'],
        index=0,
        key='calls_sort_order'
    )

# Apply sorting
calls_df_sorted = calls_df.sort_values(
    by=calls_sort_col,
    ascending=(calls_sort_order == 'Low to High')
).reset_index(drop=True)

# Format columns after sorting
calls_df_display = calls_df_sorted.copy()
if 'Premium' in calls_df_display.columns:
    calls_df_display['Premium'] = calls_df_display['Premium'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
if 'Volume' in calls_df_display.columns:
    calls_df_display['Volume'] = calls_df_display['Volume'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "0")
if 'OI' in calls_df_display.columns:
    calls_df_display['OI'] = calls_df_display['OI'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "0")
if 'IV' in calls_df_display.columns:
    calls_df_display['IV'] = calls_df_display['IV'].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A")

for greek in ['Delta', 'Theta', 'Gamma', 'Vega']:
    if greek in calls_df_display.columns:
        calls_df_display[greek] = calls_df_display[greek].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")

st.dataframe(calls_df_display, hide_index=True, use_container_width=True, height=500)

# ===============================================================
# DETAILED SECTION - PUTS TABLE
# ===============================================================
st.markdown("### 📉 Puts Options Chain")

# Prepare puts data
puts_cols = [col for col in base_cols + optional_cols if col in puts.columns]
puts_df = puts[puts_cols].copy()

# Rename columns
puts_df = puts_df.rename(columns=rename_map)

# Sort controls for puts
col_p1, col_p2 = st.columns([2, 1])
with col_p1:
    puts_sort_col = st.selectbox(
        "Sort Puts by:",
        options=list(puts_df.columns),
        index=list(puts_df.columns).index('Strike'),
        key='puts_sort_col'
    )
with col_p2:
    puts_sort_order = st.selectbox(
        "Order:",
        options=['Low to High', 'High to Low'],
        index=0,
        key='puts_sort_order'
    )

# Apply sorting
puts_df_sorted = puts_df.sort_values(
    by=puts_sort_col,
    ascending=(puts_sort_order == 'Low to High')
).reset_index(drop=True)

# Format columns after sorting
puts_df_display = puts_df_sorted.copy()
if 'Premium' in puts_df_display.columns:
    puts_df_display['Premium'] = puts_df_display['Premium'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
if 'Volume' in puts_df_display.columns:
    puts_df_display['Volume'] = puts_df_display['Volume'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "0")
if 'OI' in puts_df_display.columns:
    puts_df_display['OI'] = puts_df_display['OI'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "0")
if 'IV' in puts_df_display.columns:
    puts_df_display['IV'] = puts_df_display['IV'].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A")

for greek in ['Delta', 'Theta', 'Gamma', 'Vega']:
    if greek in puts_df_display.columns:
        puts_df_display[greek] = puts_df_display[greek].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")

st.dataframe(puts_df_display, hide_index=True, use_container_width=True, height=500)

st.markdown("---")
st.caption("💡 Data provided by Yahoo Finance via yfinance")