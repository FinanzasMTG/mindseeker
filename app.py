import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
import gspread
import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Page config and styling
st.set_page_config(
    page_title="MindSeeker by FinanzasMTG",
    page_icon="🦊",
    layout="wide"
)

# Modern dashboard CSS inspired by Nova design
st.markdown("""
    <style>
    /* Main container with background image */
    .main {
        background-image: url("app_bg.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* Semi-transparent overlay */
    .main::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(31, 35, 53, 0.7);
        z-index: -1;
    }
    
    /* Clean up multiselect styling - more aggressive removal of styles */
    .stMultiSelect, 
    .stMultiSelect > div,
    .stMultiSelect > div > div,
    .stMultiSelect [data-baseweb="select"],
    .stMultiSelect [data-baseweb="input"],
    .stMultiSelect [data-baseweb="popover"],
    .stMultiSelect [data-baseweb="select-container"] {
        background-color: transparent !important;
        background-image: none !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    
    /* Style for selected tags only */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #03a088 !important;
        border-radius: 4px;
        margin: 2px;
    }
    
    /* Dropdown menu styling */
    [data-baseweb="menu"] {
        background: #24283b !important;
    }
    
    /* Category headers */
    .category-header {
        color: #03a088 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        padding: 0 !important;
    }
    
    /* Remove any container styling */
    [data-testid="column"] > div > div {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Style for the dropdown menu */
    [data-baseweb="popover"] {
        background: #24283b !important;
    }
    
    [data-baseweb="select"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Style for selected tags */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #03a088 !important;
        border-radius: 4px;
        margin: 2px;
    }
    
    /* Remove any backgrounds from select dropdowns */
    [data-baseweb="select"] * {
        background: transparent !important;
        border: none !important;
    }
    
    /* Style for the dropdown list */
    [data-baseweb="menu"] {
        background: #24283b !important;
    }
    
    /* Category headers */
    .category-header {
        color: #03a088 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        padding: 0 !important;
    }
    
    /* Remove any remaining borders or backgrounds */
    [data-baseweb="select-container"] {
        background: transparent !important;
        border: none !important;
    }
    
    [data-baseweb="input"] {
        background: transparent !important;
        border: none !important;
    }
    
    /* Headers */
    h1 {
        font-size: 28px;
        font-weight: 600;
        color: #c0caf5;
        margin-bottom: 24px;
    }
    
    /* Metrics Cards */
    div[data-testid="stMetricValue"] {
        background: #24283b;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        color: #FFFFFF !important;
    }
    
    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
    }
    
    div[data-testid="stMetricValue"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    /* Metric Labels */
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #7aa2f7 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #24283b;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem 1rem;
    }
    
    .sidebar .sidebar-content {
        background: transparent;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: #1f2335;
        padding: 6px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 500;
        background: transparent;
        color: #a9b1d6;
        border-bottom: none !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #24283b;
        color: #03a088;
        box-shadow: none;
    }
    
    /* Hide sidebar only after username selection */
    [data-testid="stSidebar"][aria-expanded="true"].hide {
        display: none;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"].hide {
        display: none;
    }
    
    /* Adjust main content when sidebar is hidden */
    .main .block-container {
        padding-left: 5% !important;
        padding-right: 5% !important;
    }
    
    /* DataFrames */
    .dataframe {
        border: none !important;
        border-radius: 12px;
        overflow: hidden;
        background: #24283b;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .dataframe th {
        background: #1f2335 !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        color: #03a088;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .dataframe td {
        padding: 12px 16px !important;
        color: #c0caf5;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Plotly Charts */
    .js-plotly-plot {
        background: #24283b;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Multiselect */
    .stMultiSelect {
        background: #24283b;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #c0caf5;
    }
    
    .stMultiSelect:hover {
        border-color: #03a088;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #03a088 !important;
        border-radius: 4px;
        margin: 2px;
    }
    
    /* Hover states */
    .stSelectbox:hover, 
    .stMultiSelect:hover,
    .stTextInput > div:hover {
        border-color: #03a088 !important;
    }
    
    /* Selected states */
    .stCheckbox:checked,
    .stRadio:checked {
        background-color: #03a088 !important;
    }
    
    /* Links and interactive elements */
    a:hover {
        color: #03a088 !important;
    }
    
    /* Metric highlights */
    div[data-testid="stMetricValue"] {
        color: #03a088 !important;
    }
    
    /* Sidebar category headers */
    .sidebar-category {
        color: #03a088;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Change active tab indicator color */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #03a088 !important;
    }
    
    /* Loading state styling */
    .stSpinner {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(31, 35, 53, 0.3);
        backdrop-filter: blur(8px);
        z-index: 1000;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    /* Make container cover full screen */
    .stSpinner > div {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: transparent !important;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Hide the loading text */
    .stSpinner > div > div:last-child {
        display: none;
    }
    
    /* Make spinner bigger and white */
    .stSpinner svg {
        stroke: white !important;
        transform: scale(3) !important;
        stroke-width: 1.5 !important;
    }
    
    /* Make plotly modebar transparent */
    .modebar {
        background: transparent !important;
    }
    
    .modebar-btn {
        background: transparent !important;
        color: #ffffff !important;
    }
    
    /* Hover state for buttons */
    .modebar-btn:hover {
        color: #03a088 !important;
    }
    
    [data-testid="stPlotlyChart"] > div {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    .js-plotly-plot {
        width: 90% !important;
        margin: 0 auto !important;
    }
    
    /* Force transparency on modebar and all its children */
    .modebar,
    .modebar *,
    .modebar-btn,
    .modebar-btn rect,
    .modebar-btn path,
    [data-title="Click to enter pan mode"],
    [data-title="Click to enter zoom mode"],
    [data-title="Reset axes"],
    [data-title="Download plot"] {
        background: transparent !important;
        background-color: transparent !important;
        fill: #ffffff !important;
    }
    
    /* Hover effects */
    .modebar-btn:hover path {
        fill: #03a088 !important;
    }
    
    /* Remove any backgrounds that might be interfering */
    .js-plotly-plot .plotly .modebar {
        background: transparent !important;
    }
    
    .js-plotly-plot .plotly .modebar-container {
        background: transparent !important;
    }
    
    [data-testid="stPlotlyChart"] > div {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    .js-plotly-plot {
        width: 90% !important;
        margin: 0 auto !important;
    }
    </style>
""", unsafe_allow_html=True)

# Add this CSS to your existing styles
st.markdown("""
    <style>
    /* Category headers */
    .category-header {
        color: #03a088 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0 !important;
        padding: 0 !important;
    }
    
    /* Remove any container styling */
    [data-testid="column"] > div > div {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Clean up multiselect styling - more aggressive removal of styles */
    .stMultiSelect, 
    .stMultiSelect > div,
    .stMultiSelect > div > div,
    .stMultiSelect [data-baseweb="select"],
    .stMultiSelect [data-baseweb="input"],
    .stMultiSelect [data-baseweb="popover"],
    .stMultiSelect [data-baseweb="select-container"] {
        background-color: transparent !important;
        background-image: none !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Add this CSS before the sidebar content
st.markdown("""
    <style>
    /* Normal state */
    .stButton > button {
        color: #ffffff;
        border-color: #03a088;
        background-color: #03a088;
    }
    
    /* Hover state */
    .stButton > button:hover {
        color: #ffffff;
        border-color: #03a088;
        background-color: #028474;  /* Slightly darker shade for hover */
    }
    
    /* Click/Active state */
    .stButton > button:active, 
    .stButton > button:focus {
        color: #ffffff !important;
        border-color: #03a088 !important;
        background-color: #03a088 !important;
        box-shadow: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Column name mappings and categories (add this after the imports)
COLUMN_NAMES = {
    'amount': 'Amount',
    'card_name': 'Card Name',
    'card_set': 'Set',
    'language': 'Language',
    'condition': 'Condition',
    'foil': 'Foil',
    'signed': 'Signed',
    'country': 'Country',
    'from_price': 'From Price',
    'trend_price': 'Trend Price',
    'ms_trend_price': 'MS Trend Price',
    'efficient_price': 'Efficient Price',
    'conservative_price': 'Conservative Price',
    'value_price': 'Value Price',
    'alerts': 'Alerts',
    'notes': 'Notes',
    'date': 'Date',
    'total_stock': 'Total Stock',
    'country_stock': 'Country Stock',
    'price_growth': 'Price Growth',
    'equity_in_country': 'Equity in Country',
    'equity_on_cardmarket': 'Equity on Cardmarket',
    'total_efficient_value': 'Total Value',
    'total_conservative_value': 'Conservative Value'
}

# Default columns
DEFAULT_COLUMNS = [
    'amount', 'card_name', 'card_set', 'language', 'condition', 
    'foil', 'signed', 'country', 'from_price', 'trend_price',
    'ms_trend_price', 'efficient_price', 'conservative_price', 'value_price',
    'alerts'
]

# Column categories for the selector
column_categories = {
    "Dimensions": [
        'amount', 'card_name', 'card_set', 'language', 'condition', 
        'foil', 'signed', 'country', 'alerts', 'notes', 'date'
    ],
    "Metrics": [
        'from_price', 'trend_price', 'ms_trend_price', 'efficient_price', 
        'conservative_price', 'value_price', 'total_stock', 'country_stock', 
        'price_growth', 'equity_in_country', 'equity_on_cardmarket',
        'total_efficient_value', 'total_conservative_value'
    ]
}

# Authentication
@st.cache_resource
def get_credentials():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/bigquery",
        ],
    )
    return credentials

def get_user_sheet_id(username):
    """Get the sheet ID for a specific user from the setup sheet"""
    credentials = get_credentials()
    gc = gspread.authorize(credentials)
    
    # Get setup sheet ID from secrets
    setup_sheet_id = st.secrets["sheets_setup_id"]
    setup_sheet = gc.open_by_key(setup_sheet_id)
    setup_worksheet = setup_sheet.get_worksheet(0)
    
    # Get data and convert to DataFrame
    data = setup_worksheet.get_all_values()
    df_setup = pd.DataFrame(data[1:], columns=data[0])
    
    # Filter for the specific user (case insensitive)
    user_row = df_setup[df_setup['user'].str.lower() == username.lower()]
    
    if len(user_row) == 0:
        return None
    
    # Get sheet ID from mtg_input_file column
    if 'mtg_output_file' in df_setup.columns:
        sheet_id = user_row['mtg_output_file'].iloc[0]
        # Extract sheet ID from URL if necessary
        if 'spreadsheets/d/' in sheet_id:
            sheet_id = sheet_id.split('spreadsheets/d/')[1].split('/')[0]
        return sheet_id
    else:
        raise ValueError("MTG input file column not found in setup sheet")

def clean_price(value):
    """Clean price values by removing currency symbols and converting to float"""
    if pd.isna(value) or value == 'N/A':
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        # Remove currency symbols and spaces
        cleaned = str(value).replace('€', '').replace('£', '').replace('$', '').replace(',', '.').strip()
        return float(cleaned)
    except:
        return None

def format_price(value, include_currency=True):
    """Format price values with currency symbol"""
    if pd.isna(value) or value is None:
        return None
    if include_currency:
        return f"€{value:,.2f}"
    return f"{value:,.2f}"

def load_user_data(username):
    """Load data for specific user from their Google Sheet"""
    credentials = get_credentials()
    gc = gspread.authorize(credentials)
    
    # Get user's sheet ID
    sheet_id = get_user_sheet_id(username)
    
    if sheet_id is None:
        raise ValueError("User not found in setup sheet")
    
    sheet = gc.open_by_key(sheet_id)
    worksheet = sheet.get_worksheet(0)
    
    # Get data and convert to DataFrame
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    
    # Price-related columns
    price_columns = [
        'trend_price', 'efficient_price', 'conservative_price', 
        'from_price', 'value_price', 'purchase_price', 'listed_price',
        'total_efficient_value', 'total_conservative_value'
    ]
    
    # Other numeric columns
    numeric_columns = [
        'amount', 'total_stock', 'country_stock', 'listed_stock',
        'price_growth', 'equity_in_country', 'equity_on_cardmarket'
    ]
    
    # Clean price columns
    for col in price_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_price)
    
    # Clean other numeric columns
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].replace('N/A', pd.NA), errors='coerce')
    
    # Clean up text columns
    text_columns = ['card_name', 'card_set', 'language', 'condition', 'foil', 'signed', 'country', 'alerts']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].replace('N/A', None)
    
    return df

# Update the sidebar and main content section
if 'username_selected' not in st.session_state:
    st.session_state.username_selected = False

# Always show sidebar for initial state
with st.sidebar:
    st.title("🦊 Mindseeker by FinanzasMTG")
    username = st.text_input("Enter your username:", value="FinanzasMTG")
    if st.button("Enter"):
        st.session_state.username = username
        st.session_state.username_selected = True
        # Add CSS class to hide sidebar
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            </style>
        """, unsafe_allow_html=True)
        st.rerun()

if st.session_state.username_selected:
    try:
        with st.spinner(''):  # Empty string to remove text
            df = load_user_data(username)
        
        if len(df) == 0:
            st.error("No data found for this username")
        else:
            # Clean welcome header with date
            max_date = pd.to_datetime(df['date']).max().strftime('%d/%m/%Y')
            st.markdown(f"""
                <div style="
                    margin-bottom: 2rem;
                    padding: 1rem 0;
                ">
                    <h1 style="
                        color: #ffffff;
                        margin: 0;
                        padding: 0;
                        font-size: 32px;
                        font-weight: 500;
                        line-height: 1;
                    ">👋🏻 Welcome, {username}!</h1>
                    <p style="
                        color: #03a088;
                        margin: 0;
                        padding: 0;
                        font-size: 16px;
                        line-height: 1.5;
                    ">📅 Data from {max_date}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Metrics with improved styling
            col1, col2, col3, col4 = st.columns(4)
            
            metrics_style = """
                style="
                    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFF 100%);
                    padding: 1.5rem;
                    border-radius: 16px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
                "
            """
            
            with col1:
                total_cards = df['amount'].sum()
                st.metric("Total Cards", f"{total_cards:,.0f}")
            
            with col2:
                total_value = df['total_efficient_value'].sum()
                st.metric("Portfolio Value", f"€{total_value:,.2f}")
            
            with col3:
                avg_price = df['efficient_price'].mean()
                st.metric("Average Price", f"€{avg_price:.2f}")
            
            with col4:
                unique_cards = len(df)
                st.metric("Unique Cards", unique_cards)
            
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["Portfolio Overview", "Price Analysis", "Inventory Details"])
            
            with tab1:
                # Add custom CSS for the chart container and title
                st.markdown("""
                    <style>
                    [data-testid="stPlotlyChart"] > div {
                        width: 100% !important;
                        display: flex !important;
                        justify-content: center !important;
                    }
                    
                    .js-plotly-plot {
                        width: 90% !important;
                        margin: 0 auto !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                # Add title outside the chart
                st.markdown('<h3 style="color: #03a088; margin-bottom: 1rem;">Portfolio Value by Set</h3>', unsafe_allow_html=True)
                
                # Portfolio composition by set
                fig_sets = px.treemap(
                    df,
                    path=['card_set'],
                    values='total_efficient_value',
                )
                
                # Update treemap layout (removed title from here)
                fig_sets.update_layout(
                    height=450,
                    margin=dict(t=20, l=20, r=20, b=20),  # Reduced top margin since title is removed
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(
                        color='#ffffff',
                        size=14
                    ),
                    autosize=True
                )
                
                # Display the chart
                st.plotly_chart(
                    fig_sets, 
                    use_container_width=True,
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select', 'lasso2d'],
                        'responsive': True,
                        'modeBarStyle': {
                            'backgroundColor': 'transparent',
                            'color': '#ffffff'
                        }
                    }
                )
                
            with tab2:
                # Add custom CSS for the chart container
                st.markdown("""
                    <style>
                    [data-testid="stPlotlyChart"] > div {
                        width: 100% !important;
                        display: flex !important;
                        justify-content: center !important;
                    }
                    
                    .js-plotly-plot {
                        width: 90% !important;
                        margin: 0 auto !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                # Price distribution title and chart
                st.markdown('<h3 style="color: #03a088; margin-bottom: 1rem;">Price Distribution</h3>', unsafe_allow_html=True)
                fig_price = px.histogram(
                    df,
                    x='efficient_price',
                    nbins=5000
                )
                
                # Update histogram layout
                fig_price.update_layout(
                    height=450,
                    margin=dict(t=20, l=20, r=20, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff'),
                    autosize=True
                )
                
                st.plotly_chart(
                    fig_price, 
                    use_container_width=True,
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select', 'lasso2d'],
                        'responsive': True,
                        'modeBarStyle': {
                            'backgroundColor': 'transparent',
                            'color': '#ffffff'
                        }
                    }
                )
                
                # Price growth analysis title and chart
                st.markdown('<h3 style="color: #03a088; margin-bottom: 1rem;">Price Growth vs Current Price</h3>', unsafe_allow_html=True)
                fig_growth = px.scatter(
                    df,
                    x='efficient_price',
                    y='price_growth',
                    hover_data=['card_name']
                )
                
                # Update scatter plot layout
                fig_growth.update_layout(
                    height=450,
                    margin=dict(t=20, l=20, r=20, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff'),
                    autosize=True
                )
                
                st.plotly_chart(
                    fig_growth, 
                    use_container_width=True,
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select', 'lasso2d'],
                        'responsive': True,
                        'modeBarStyle': {
                            'backgroundColor': 'transparent',
                            'color': '#ffffff'
                        }
                    }
                )
                
            with tab3:
                # Create two columns for dimensions and metrics
                col1, col2 = st.columns(2)
                
                selected_columns = []
                
                # Dimensions column
                with col1:
                    st.markdown('<p class="category-header">Dimensions</p>', unsafe_allow_html=True)
                    dimension_cols = [col for col in column_categories["Dimensions"] if col in df.columns]
                    if dimension_cols:
                        selected_dims = st.multiselect(
                            "",
                            dimension_cols,
                            default=[col for col in dimension_cols if col in DEFAULT_COLUMNS],
                            format_func=lambda x: COLUMN_NAMES.get(x, x.replace('_', ' ').title()),
                            label_visibility="collapsed"
                        )
                        selected_columns.extend(selected_dims)
                
                # Metrics column
                with col2:
                    st.markdown('<p class="category-header">Metrics</p>', unsafe_allow_html=True)
                    metric_cols = [col for col in column_categories["Metrics"] if col in df.columns]
                    if metric_cols:
                        selected_metrics = st.multiselect(
                            "",
                            metric_cols,
                            default=[col for col in metric_cols if col in DEFAULT_COLUMNS],
                            format_func=lambda x: COLUMN_NAMES.get(x, x.replace('_', ' ').title()),
                            label_visibility="collapsed"
                        )
                        selected_columns.extend(selected_metrics)

                # Format the DataFrame for display
                display_df = df.copy()
                
                # Format price columns with currency symbol
                price_columns = [
                    'trend_price', 'efficient_price', 'conservative_price', 
                    'from_price', 'value_price', 'purchase_price', 'listed_price',
                    'total_efficient_value', 'total_conservative_value'
                ]
                
                # Format percentage columns
                percentage_columns = [
                    'price_growth', 'equity_in_country', 'equity_on_cardmarket'
                ]
                
                # Format prices
                for col in price_columns:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: format_price(x) if x is not None else None)
                
                # Format percentages
                for col in percentage_columns:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"{x*100:.1f}%" if x is not None else None)
                
                # Rename columns for display
                display_df.columns = [COLUMN_NAMES.get(col, col.replace('_', ' ').title()) for col in display_df.columns]
                
                # Update the dataframe display section in tab3
                if selected_columns:
                    display_columns = [COLUMN_NAMES.get(col, col.replace('_', ' ').title()) for col in selected_columns]
                    df_display = display_df[display_columns].copy()
                    df_display.index = range(len(df_display))  # Reset index
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        height=600,
                        hide_index=True  # Use Streamlit's native index hiding
                    )
                else:
                    st.warning("Please select at least one column to display")

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
else:
    st.info("Please enter your username to view your portfolio")

# Footer
# Replace the text with the image
assets_path = os.path.join(os.path.dirname(__file__), 'assets')
logo_path = os.path.join(assets_path, 'Alpha_Logo.png')
with open(logo_path, "rb") as f:
    logo_contents = f.read()
logo_encoded = base64.b64encode(logo_contents).decode()

st.sidebar.markdown(
    f"""
    <div style="display: flex; justify-content: center; padding: 10px; margin-top: auto;">
        <img src="data:image/png;base64,{logo_encoded}" style="width: 100px; height: auto;">
    </div>
    """,
    unsafe_allow_html=True
)

# Add this function at the top of your file
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_bg_image():
    assets_path = os.path.join(os.path.dirname(__file__), 'assets')
    bg_img_path = os.path.join(assets_path, 'app_bg.jpg')
    
    bin_str = get_base64_of_bin_file(bg_img_path)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(31, 35, 53, 0.8);  /* Increased opacity */
        z-index: -1;
    }}
    
    /* Loading state styling */
    .stSpinner {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(31, 35, 53, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        backdrop-filter: blur(8px);
    }}
    
    .stSpinner > div {{
        background: #24283b;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Call this function before your main app code
set_bg_image()

st.markdown("""
    <style>
    /* Sidebar toggle button */
    section[data-testid="stSidebar"] > div.st-emotion-cache-16idsys p {
        font-size: 24px !important;
        font-weight: bold !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    section[data-testid="stSidebar"] > div.st-emotion-cache-16idsys {
        background: #03a088 !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        position: relative;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"] > div.st-emotion-cache-16idsys:hover {
        background: #028474 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True) 