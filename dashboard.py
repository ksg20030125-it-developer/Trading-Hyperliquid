"""
Hyperliquid Vault Dashboard - Web UI with Charts
Interactive web dashboard similar to Hyperliquid homepage
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
from hyperliquid_api_example import HyperliquidAPI

# Page configuration
st.set_page_config(
    page_title="Hyperliquid Vault Dashboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Hyperliquid-like styling with highlighted text
st.markdown("""
<style>
    .main {
        background-color: #0a0e17;
        color: #ff0000;
    }
    .stMetric {
        background-color: #1a2332;
        padding: 15px;
        border-radius: 8px;
        border: 2px solid #58a6ff;
        box-shadow: 0 0 10px #58a6ff;
    }
    .stMetric label {
        color: #ffd700 !important;
        font-weight: 600 !important;
        font-size: 1.1em !important;
    }
    .stMetric .metric-value {
        color: #58a6ff !important;
        font-weight: 700 !important;
        font-size: 1.3em !important;
        text-shadow: 0 0 8px #58a6ff;
    }
    
    /* Main titles and headings - Blue and highlighted */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-weight: 700 !important;
        text-shadow: 0 0 15px #58a6ff;
        background: linear-gradient(90deg, #1a3a5c, transparent);
        padding: 10px;
        border-left: 4px solid #58a6ff;
    }
    
    h1 {
        font-size: 2.5em !important;
        text-shadow: 0 0 20px #58a6ff;
    }
    
    h2 {
        font-size: 1.8em !important;
        text-shadow: 0 0 15px #58a6ff;
    }
    
    h3 {
        font-size: 1.4em !important;
        text-shadow: 0 0 12px #58a6ff;
    }
    
    .profit {
        color: #3fb950 !important;
        font-weight: 700 !important;
    }
    .loss {
        color: #ff4444 !important;
        font-weight: 700 !important;
    }
    .stDataFrame {
        background-color: #161b22;
        border: 1px solid #58a6ff;
    }
    
    /* Highlighted text elements */
    p, span, div {
        color: #58a6ff !important;
        text-align: left !important;
    }
    
    /* Sidebar highlighting */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #0f1419 !important;
        width: 400px !important;
        min-width: 400px !important;
    }
    
    .css-1d391kg p, [data-testid="stSidebar"] p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* Loading spinner customization */
    .stSpinner > div {
        border-top-color: #ffd700 !important;
    }
    
    /* Status widget styling - All text in black */
    .stStatus {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
    }
    
    /* Status label/title */
    .stStatus > summary {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    .stStatus *,
    .stStatus [data-testid="stStatusWidget"],
    .stStatus [data-testid="stExpanderDetails"],
    .stStatus [data-testid="stExpanderDetails"] *,
    .stStatus label, 
    .stStatus p, 
    .stStatus span, 
    .stStatus div,
    .stStatus [data-testid="stMarkdownContainer"],
    .stStatus [data-testid="stMarkdownContainer"] *,
    .stStatus [data-testid="stMarkdownContainer"] p,
    .stStatus [data-testid="stMarkdownContainer"] strong,
    .stStatus strong,
    .stStatus em,
    .stStatus b,
    .st-emotion-cache-3n56ur *,
    .st-emotion-cache-3n56ur p,
    .st-emotion-cache-3n56ur strong {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1em !important;
        text-shadow: none !important;
    }
    
    /* Status icon colors */
    .stStatus svg {
        color: #000000 !important;
        filter: none !important;
    }
    
    /* Selectbox (Sort by) highlighting */
    .stSelectbox label {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1.1em !important;
        text-shadow: none !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Dropdown menu options */
    .stSelectbox div[role="listbox"] li,
    .stSelectbox div[role="option"],
    [data-baseweb="popover"] div[role="listbox"] li,
    [data-baseweb="popover"] div[role="option"] {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    [data-baseweb="popover"] div[role="listbox"] li:hover,
    [data-baseweb="popover"] div[role="option"]:hover {
        background-color: #e8f4ff !important;
        color: #000000 !important;
    }
    
    /* Smooth transitions */
    .stPlotlyChart {
        transition: opacity 0.3s ease-in-out;
    }
    
    /* Button highlighting */
    .stButton button {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 600 !important;
        border: 2px solid #000000 !important;
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
    }
    
    .stButton button:hover {
        background-color: #f0f0f0 !important;
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.4);
    }
    
    /* Responsive Design - Mobile First */
    
    /* Mobile devices (up to 768px) */
    @media only screen and (max-width: 768px) {
        .st-emotion-cache-zy6yx3 {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 3rem !important;
        }
        
        h1 {
            font-size: 1.8em !important;
        }
        
        h2 {
            font-size: 1.4em !important;
        }
        
        h3 {
            font-size: 1.2em !important;
        }
        
        .stMetric label {
            font-size: 0.9em !important;
        }
        
        .stMetric .metric-value {
            font-size: 1.1em !important;
        }
        
        /* Stack columns vertically */
        .stColumn {
            width: 100% !important;
            min-width: 100% !important;
        }
        
        /* Sidebar adjustments */
        [data-testid="stSidebar"] {
            width: 100% !important;
            min-width: 100% !important;
        }
        
        /* Chart heights for mobile */
        .stPlotlyChart {
            height: 300px !important;
        }
        
        /* Table scrolling */
        .stDataFrame {
            overflow-x: auto !important;
        }
    }
    
    /* Tablet devices (769px to 1024px) */
    @media only screen and (min-width: 769px) and (max-width: 1024px) {
        .st-emotion-cache-zy6yx3 {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        
        h1 {
            font-size: 2.2em !important;
        }
        
        h2 {
            font-size: 1.6em !important;
        }
        
        [data-testid="stSidebar"] {
            width: 300px !important;
            min-width: 300px !important;
        }
        
        /* 2 columns for charts */
        .stColumn {
            width: calc(50% - 0.5rem) !important;
            min-width: calc(50% - 0.5rem) !important;
        }
    }
    
    /* Desktop devices (1025px to 1440px) */
    @media only screen and (min-width: 1025px) and (max-width: 1440px) {
        .st-emotion-cache-zy6yx3 {
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }
        
        [data-testid="stSidebar"] {
            width: 350px !important;
            min-width: 350px !important;
        }
    }
    
    /* Large desktop (1441px and above) */
    @media only screen and (min-width: 1441px) {
        .st-emotion-cache-zy6yx3 {
            padding-left: 5rem !important;
            padding-right: 5rem !important;
        }
        
        [data-testid="stSidebar"] {
            width: 400px !important;
            min-width: 400px !important;
        }
    }
    
    /* Responsive font sizing */
    @media only screen and (max-width: 480px) {
        html {
            font-size: 14px !important;
        }
        
        .stButton button {
            padding: 0.5rem 1rem !important;
            font-size: 0.9em !important;
        }
        
        .stSelectbox label {
            font-size: 0.9em !important;
        }
    }
    
    /* Smooth transitions for responsive changes */
    .stColumn, [data-testid="stSidebar"], .stMetric {
        transition: width 0.3s ease, padding 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 10

@st.cache_data(ttl=60, show_spinner=False)
def fetch_vault_data(vault_address, max_followers=2000):
    """Fetch vault data with caching - uses batched requests for up to 2000 followers"""
    api = HyperliquidAPI()
    
    # Use batched fetching to try to get up to max_followers
    # Note: API currently limits to 100 followers, but this is prepared for future pagination support
    vault_data = api.get_vault_details_batched(vault_address, target_followers=max_followers, batch_size=100)
    
    if not vault_data:
        return None, None
    
    # Use batched mode for leaderboard as well
    leaderboard = api.get_vault_leaderboard(vault_address, use_batched=True, target_followers=max_followers)
    
    return vault_data, leaderboard

def create_leaderboard_df(leaderboard, top_n=50):
    """Convert leaderboard to pandas DataFrame - optimized"""
    if not leaderboard:
        return pd.DataFrame()
    
    # Pre-allocate lists for better performance
    ranks, users, equities, current_pnls, all_time_pnls, rois, days_list = [], [], [], [], [], [], []
    
    for i, entry in enumerate(leaderboard[:top_n], 1):
        user = entry.get('user', 'N/A')
        equity = float(entry.get('vaultEquity', 0))
        current_pnl = float(entry.get('pnl', 0))
        all_time_pnl = float(entry.get('allTimePnl', 0))
        days = entry.get('daysFollowing', 0)
        roi = (all_time_pnl / equity * 100) if equity > 0 else 0
        
        ranks.append(i)
        users.append(f"{user[:8]}...{user[-6:]}")
        equities.append(equity)
        current_pnls.append(current_pnl)
        all_time_pnls.append(all_time_pnl)
        rois.append(roi)
        days_list.append(days)
    
    return pd.DataFrame({
        'Rank': ranks,
        'User': users,
        'Equity': equities,
        'Current PnL': current_pnls,
        'All-Time PnL': all_time_pnls,
        'ROI (%)': rois,
        'Days': days_list
    })

def create_pnl_distribution_chart(df):
    """Create PnL distribution histogram - optimized"""
    if df.empty:
        return go.Figure()
    
    fig = px.histogram(
        df, 
        x='All-Time PnL',
        nbins=30,
        title='PnL Distribution',
        color_discrete_sequence=['#58a6ff']
    )
    fig.update_layout(
        plot_bgcolor='#0d1117',
        paper_bgcolor='#161b22',
        font_color='#e1e4e8',
        xaxis_title='All-Time PnL ($)',
        yaxis_title='Number of Followers',
        height=400
    )
    return fig

def create_roi_vs_equity_chart(df):
    """Create ROI vs Equity scatter plot - optimized"""
    if df.empty:
        return go.Figure()
    
    # Create a positive size metric (absolute value + small offset to avoid zero)
    df_copy = df.copy()
    df_copy['Marker Size'] = df_copy['All-Time PnL'].abs() + 1
    
    fig = px.scatter(
        df_copy,
        x='Equity',
        y='ROI (%)',
        size='Marker Size',
        hover_data=['User', 'Days', 'All-Time PnL'],
        title='ROI vs Equity',
        color='ROI (%)',
        color_continuous_scale=['#f85149', '#ffa657', '#3fb950']
    )
    fig.update_layout(
        plot_bgcolor='#0d1117',
        paper_bgcolor='#161b22',
        font_color='#e1e4e8',
        xaxis_title='Equity ($)',
        yaxis_title='ROI (%)',
        height=400
    )
    return fig

def create_top_performers_bar_chart(df):
    """Create top performers bar chart - optimized"""
    if df.empty:
        return go.Figure()
    
    top_10 = df.head(10)
    colors = ['#ffd700' if i < 3 else '#58a6ff' for i in range(len(top_10))]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_10['User'],
        y=top_10['All-Time PnL'],
        marker_color=colors,
        text=top_10['All-Time PnL'].apply(lambda x: f'${x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>PnL: $%{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Top 10 Performers by All-Time PnL',
        plot_bgcolor='#0d1117',
        paper_bgcolor='#161b22',
        font_color='#e1e4e8',
        xaxis_title='User',
        yaxis_title='All-Time PnL ($)',
        showlegend=False,
        height=400
    )
    return fig

def create_equity_distribution_pie(df):
    """Create equity distribution pie chart - optimized"""
    if df.empty:
        return go.Figure()
    
    # Group by equity ranges
    bins = [0, 100000, 500000, 1000000, 5000000, float('inf')]
    labels = ['<$100K', '$100K-$500K', '$500K-$1M', '$1M-$5M', '>$5M']
    df_copy = df.copy()
    df_copy['Equity Range'] = pd.cut(df_copy['Equity'], bins=bins, labels=labels)
    
    equity_dist = df_copy.groupby('Equity Range', observed=True).size().reset_index(name='Count')
    
    fig = px.pie(
        equity_dist,
        values='Count',
        names='Equity Range',
        title='Equity Distribution',
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig.update_layout(
        plot_bgcolor='#0d1117',
        paper_bgcolor='#161b22',
        font_color='#e1e4e8',
        height=400
    )
    return fig

def create_metrics_over_time(df):
    """Create combined metrics chart"""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('ROI Distribution', 'Days Following Distribution')
    )
    
    # ROI histogram
    fig.add_trace(
        go.Histogram(x=df['ROI (%)'], nbinsx=20, marker_color='#3fb950', name='ROI'),
        row=1, col=1
    )
    
    # Days histogram
    fig.add_trace(
        go.Histogram(x=df['Days'], nbinsx=20, marker_color='#58a6ff', name='Days'),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='#0d1117',
        paper_bgcolor='#161b22',
        font_color='#e1e4e8',
        showlegend=False
    )
    return fig

def style_dataframe(df):
    """Apply styling to dataframe"""
    def color_pnl(val):
        if isinstance(val, (int, float)):
            color = '#3fb950' if val >= 0 else '#f85149'
            return f'color: {color}'
        return ''
    
    def highlight_top_3(row):
        if row['Rank'] <= 3:
            return ['background-color: rgba(255, 215, 0, 0.1)'] * len(row)
        return [''] * len(row)
    
    styled = df.style.applymap(
        color_pnl, 
        subset=['Current PnL', 'All-Time PnL', 'ROI (%)']
    ).apply(highlight_top_3, axis=1).format({
        'Equity': '${:,.2f}',
        'Current PnL': '${:,.2f}',
        'All-Time PnL': '${:,.2f}',
        'ROI (%)': '{:.2f}%'
    })
    
    return styled

# Main Dashboard
def main():
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("🏆 Hyperliquid Vault Dashboard")
    with col2:
        st.markdown(f"**⏰ Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
    with col3:
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
    
    # Sidebar
    st.sidebar.header("⚙️ Dashboard Settings")
    
    # Vault selection
    vault_address = st.sidebar.text_input(
        "Vault Address",
        value="0xdfc24b077bc1425ad1dea75bcb6f8158e10df303",
        help="Enter HLP vault or any other vault address"
    )
    
    # Display settings
    st.sidebar.subheader("📊 Display Options")
    top_n = st.sidebar.slider("Top N Performers", 10, 2000, 2000)
    
    # Filters
    st.sidebar.subheader("🔍 Filters")
    min_equity = st.sidebar.number_input(
        "Min Equity ($)",
        min_value=0,
        value=0,
        step=100000,
        format="%d"
    )
    
    min_roi = st.sidebar.number_input(
        "Min ROI (%)",
        min_value=-100.0,
        value=0.0,
        step=5.0
    )
    
    # Auto-refresh
    st.sidebar.subheader("🔄 Auto-Refresh")
    auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=False)
    if auto_refresh:
        refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)
    
    # Fetch data with status indicator
    with st.status("🔄 Loading vault data...", expanded=True) as status:
        st.markdown("**📡 Fetching vault details in batches...**")
        st.markdown(f"**🎯 Target: {top_n} followers (requesting in batches of 100)**")
        vault_data, leaderboard = fetch_vault_data(vault_address, max_followers=top_n)
        
        if not vault_data or not leaderboard:
            status.update(label="❌ Failed to load data", state="error")
            st.error("❌ Failed to fetch vault data. Please check the vault address.")
            return
        
        followers_count = len(leaderboard)
        st.markdown(f"**✅ Successfully loaded {followers_count} unique followers**")
        
        # Show API limitation notice if we only got 100 followers
        if followers_count == 100 and top_n > 100:
            st.markdown("**⚠️ Note:** Hyperliquid API currently limits responses to 100 followers maximum")
        
        st.markdown("**📊 Processing leaderboard data...**")
        status.update(label="✅ Data loaded successfully!", state="complete")
    
    # Vault Info Cards
    st.subheader("📈 Vault Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Vault Name",
            vault_data.get('name', 'N/A')
        )
    
    with col2:
        apr = vault_data.get('apr', 0)
        apr_percent = apr * 100 if isinstance(apr, float) else 0
        st.metric(
            "APR",
            f"{apr_percent:.2f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            "Total Followers",
            len(leaderboard)
        )
    
    with col4:
        total_tvl = sum(float(f.get('vaultEquity', 0)) for f in leaderboard)
        st.metric(
            "Total TVL",
            f"${total_tvl:,.0f}"
        )
    
    # Create DataFrame with progress
    with st.spinner("📈 Creating leaderboard..."):
        df = create_leaderboard_df(leaderboard, top_n)
    
    # Apply filters
    original_count = len(df)
    if min_equity > 0:
        df = df[df['Equity'] >= min_equity]
    if min_roi > 0:
        df = df[df['ROI (%)'] >= min_roi]
    
    if len(df) < original_count:
        st.info(f"🔍 Filtered from {original_count} to {len(df)} followers")
    
    st.markdown("---")
    
    # Charts Section
    st.subheader("📊 Performance Analytics")
    
    # Row 1: Top performers and PnL distribution
    with st.spinner("📊 Rendering charts..."):
        col1, col2 = st.columns(2)
        with col1:
            with st.spinner("Creating top performers chart..."):
                st.plotly_chart(create_top_performers_bar_chart(df), use_container_width=True)
        with col2:
            with st.spinner("Creating PnL distribution..."):
                st.plotly_chart(create_pnl_distribution_chart(df), use_container_width=True)
        
        # Row 2: ROI vs Equity and Equity Distribution
        col1, col2 = st.columns(2)
        with col1:
            with st.spinner("Creating ROI analysis..."):
                st.plotly_chart(create_roi_vs_equity_chart(df), use_container_width=True)
        with col2:
            with st.spinner("Creating equity distribution..."):
                st.plotly_chart(create_equity_distribution_pie(df), use_container_width=True)
        
        # Row 3: Metrics distributions
        with st.spinner("Creating metrics distribution..."):
            st.plotly_chart(create_metrics_over_time(df), use_container_width=True)
    
    st.markdown("---")
    
    # Leaderboard Table
    st.subheader(f"🏅 Leaderboard (Showing {len(df)} followers)")
    
    # Sort options
    col1, col2 = st.columns([1, 3])
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            ['All-Time PnL', 'ROI (%)', 'Equity', 'Current PnL', 'Days']
        )
    
    # Sort and display with loading indicator
    with st.spinner("🔄 Sorting leaderboard..."):
        df_sorted = df.sort_values(by=sort_by, ascending=False).reset_index(drop=True)
        df_sorted['Rank'] = range(1, len(df_sorted) + 1)
    
    # Display styled table
    with st.spinner("🎨 Styling table..."):
        st.dataframe(
            style_dataframe(df_sorted),
            use_container_width=True,
            height=600
        )
    
    # Download button
    csv = df_sorted.to_csv(index=False)
    st.download_button(
        label="📥 Download Leaderboard as CSV",
        data=csv,
        file_name=f"hyperliquid_leaderboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()
