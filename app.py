import streamlit as st
import pandas as pd

from google.oauth2 import service_account
import gspread
import os
import base64
import numpy as np

from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import random
import sqlite3

import plotly.colors as pc
import plotly.express as px
import plotly.graph_objects as go


tab_descriptions = {
    "Portfolio Overview": """
        Get a high-level view of your collection with key metrics and visualizations. See your portfolio's distribution across different sets, 
        analyze Reserved List composition, and understand your collection's rarity breakdown.
    """,
    
    "Price Analysis": """
        Deep dive into the pricing patterns of your collection. View price distributions, compare growth rates, 
        and identify your top performing cards as well as potential opportunities.
    """,
    
    "Inventory Details": """
        Access detailed information about every card in your collection. Use powerful filtering and sorting tools 
        to find specific cards and analyze their individual performance metrics.
    """,
    
    "Historical Trends": """
        Track how your cards' values have changed over time. View historical price charts and analyze price movements 
        to make informed decisions about your collection.
    """
}


@st.cache_data
def load_historical_data():
    """Load and cache historical data from SQLite database"""
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('mtg_historical.db')
        
        # Read data into DataFrame
        query = "SELECT * FROM mtg_card_prices_historical ORDER BY date, card_name_set"  # Adjust table name if different
        df_historical = pd.read_sql_query(query, conn)
        
        # Close connection
        conn.close() 
        return df_historical
    except Exception as e:
        st.error(f"Error loading historical data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame if there's an error


# Add this near the top of your file with other constants
TRIVIAS = [
    "Your journey to mastering your inventory begins here!",
    # "The *Reserved List* guarantees that certain MTG cards will never be reprinted, making them highly sought-after by collectors and investors.",
    # "The most expensive MTG card ever sold, a *Black Lotus* (1993), fetched over $500,000 at auction in 2021 due to its rarity and iconic status.",
    # "Many cards on the Reserved List have increased in value by over 1,000% since their release, proving their status as valuable assets.",
    # "The Reserved List was introduced in 1996 to appease collectors after concerns over reprints affecting card values.",
    # "MTG cards are considered \"alternative investments,\" similar to fine art or rare coins, due to their strong secondary market.",
    # "Some Reserved List cards, like *The Tabernacle at Pendrell Vale*, are valued at thousands of pounds due to their scarcity and playability.",
    # "MTG's secondary market is estimated to be worth over $1 billion, with Reserved List cards playing a major role in its value.",
    # "Reserved List cards often see spikes in value when new formats or synergies make them more desirable for gameplay.",
    # "High-grade *Alpha* and *Beta* cards from MTG's earliest sets command premium prices, especially if they are on the Reserved List.",
    # "Collectors often grade Reserved List cards through services like PSA or BGS, with top-tier grades significantly boosting their market value."
]

# Page config and styling
st.set_page_config(
    page_title="Kitsune Codex by FinanzasMTG",
    page_icon="🦊",
    layout="wide"
)

# Load app logo for sidebar
assets_path = os.path.join(os.path.dirname(__file__), 'assets')
app_logo_path = os.path.join(assets_path, 'app_logo.png')
with open(app_logo_path, "rb") as f:
    app_logo_contents = f.read()
app_logo_encoded = base64.b64encode(app_logo_contents).decode()

# Modern dashboard CSS inspired by Nova design
st.markdown("""
    <style>
    /* Import Raleway font */
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700&display=swap');
    
    /* Global font settings */
    :root {
        --font-family: 'Raleway', sans-serif !important;
    }
    
    /* Universal selector */
    *, 
    *::before, 
    *::after {
        font-family: 'Raleway', sans-serif !important;
    }
    
    /* Streamlit specific elements */
    .element-container, 
    .stMarkdown, 
    .stButton > button,
    .stSelectbox,
    .stMultiSelect,
    .stTextInput > div,
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricLabel"],
    .dataframe,
    .category-header,
    .category-header-tab3,
    h1, h2, h3, h4, h5, h6,
    p,
    span,
    div,
    button,
    input,
    select,
    textarea,
    .stTabs [data-baseweb="tab"],
    .stAlert > div,
    [data-testid="stForm"] input,
    [data-baseweb="select"] *,
    [data-baseweb="input"] *,
    [data-baseweb="textarea"] * {
        font-family: 'Raleway', sans-serif !important;
    }
    
    /* AG Grid specific */
    .ag-theme-streamlit,
    .ag-theme-streamlit .ag-header-cell,
    .ag-theme-streamlit .ag-cell {
        font-family: 'Raleway', sans-serif !important;
    }
    
    /* Plotly specific */
    .js-plotly-plot .plotly text,
    .js-plotly-plot .plotly .ytick text,
    .js-plotly-plot .plotly .xtick text {
        font-family: 'Raleway', sans-serif !important;
    }
    
    /* Main container with background image */
    .main {
        font-family: 'Raleway', sans-serif !important;
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
        background: #202020 !important;
    }
    
    /* Category headers */
    .category-header {
        color: #03a088 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        padding: 0 !important;
    }
            
    .category-header-tab3 {
        color: #03a088 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: -100px !important;
        margin-top: 10px !important;
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
        background: #202020 !important;
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
        background: #202020 !important;
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
        margin-bottom: 10px;
    }
    
    /* Metrics Cards */
    div[data-testid="stMetricValue"] {
        background: #202020;
        padding: 1.5rem;
        border-radius: 4px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: background 0.3s ease;
        color: #FFFFFF !important;
        font-size: 18px;  /* Adjust this value to change the metric value size */
    }
    
    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
    }
    
    div[data-testid="stMetricValue"]:hover {
        background: linear-gradient(to bottom, #202020 0%, #202020 65%, #004137 100%);
        border: 1px solid #03a088;
    }
    
    /* Metric Labels */
    div[data-testid="stMetricLabel"] {
        font-size: 14px;  /* Adjust this value to change the label size */
        color: #7aa2f7 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #202020;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem 1rem;
    }
    
    .sidebar .sidebar-content {
        background: transparent;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: #202020 !important;
        padding: 6px;
        border-radius: 3px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 3px;
        padding: 12px 24px;
        font-weight: 500;
        background: transparent;
        color: #ffffff;
        border-bottom: none !important;
        transition: all 0.3s ease;  /* Smooth transition for hover effects */
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #00a195;
        text-shadow: 0 0 15px rgba(0, 161, 149, 0.8);  /* Bigger, more intense glow effect */
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #202020;
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
        border-radius: 4px;
        overflow: hidden;
        background: #202020;
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
        background: #202020;
        border-radius: 4px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Multiselect */
    .stMultiSelect {
        background: #202020;
        border-radius: 4px;
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
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background-color: rgba(31, 35, 53, 0.7) !important;
        backdrop-filter: blur(8px) !important;
        z-index: 9999 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    /* Make container cover full screen */
    .stSpinner > div {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background: transparent !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Hide the loading text */
    .stSpinner > div > div:last-child {
        display: none !important;
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
    /* Normal state for login button */
    .stButton > button {
        color: #ffffff !important;
        border-color: #03a088 !important;
        background-color: #03a088 !important;
    }
    
    /* Hover state for login button */
    .stButton > button:hover {
        color: #ffffff !important;  /* Force white color on hover */
        border-color: #03a088 !important;
        background-color: #028474 !important;  /* Slightly darker shade for hover */
    }
    
    /* Click/Active state for login button */
    .stButton > button:active, 
    .stButton > button:focus {
        color: #ffffff !important;
        border-color: #03a088 !important;
        background-color: #03a088 !important;
        box-shadow: none !important;
    }
    
    /* Password toggle button specific styling */
    button[aria-label="Toggle password visibility"],
    button[aria-label="Toggle password visibility"] svg,
    button[aria-label="Toggle password visibility"] path {
        background: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.5) !important;
        fill: rgba(255, 255, 255, 0.5) !important;
        stroke: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Hover states for password toggle */
    button[aria-label="Toggle password visibility"]:hover,
    button[aria-label="Toggle password visibility"]:hover svg,
    button[aria-label="Toggle password visibility"]:hover path {
        background: transparent !important;
        color: rgba(255, 255, 255, 0.8) !important;
        fill: rgba(255, 255, 255, 0.8) !important;
        stroke: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Remove any button styling from password toggle */
    button[aria-label="Toggle password visibility"] {
        border: none !important;
        box-shadow: none !important;
        margin: 0 !important;
        padding: 0 !important;
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# Add this CSS block after your existing login form styling
st.markdown("""
    <style>
    /* Style for username and password input fields */
    [data-testid="stForm"] input[type="text"],
    [data-testid="stForm"] input[type="password"] {
        border-radius: 2px !important;
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
    'trend_price': 'Trend Price',  # Removed "in €"
    'ms_trend_price': 'MS Trend Price',  # Removed "in €"
    'efficient_price': 'Efficient Price',  # Removed "in €"
    'conservative_price': 'Conservative Price',  # Removed "in €"
    'value_price': 'Value Price',  # Removed "in €"
    'alerts': 'Alerts',
    'notes': 'Notes',
    'date': 'Date',
    'last_sold_date': 'Last Sold Date',
    'liquidity': 'Liquidity',
    'listed_price': 'Cardmarket Listed Price',  # Removed "in €"
    'listed_stock': 'Cardmarket Listed Stock',
    'total_stock': 'Total Stock',
    'country_stock': 'Country Stock',
    'price_growth': 'Price Growth',
    'equity_in_country': 'Equity in Country',
    'equity_on_cardmarket': 'Equity on Cardmarket',
    'total_efficient_value': 'Total Value',  # Removed "in €"
    'total_conservative_value': 'Conservative Value',  # Removed "in €"
    'collection_number': 'Collection Number',
    'rarity': 'Rarity',
    'reserved_list': 'Reserved List',
    'set_release_date': 'Set Release Date',
    'frame_era': 'Frame Era',
    'set_type': 'Set Type',
    'price_diff_d7': 'Today vs D7'
}

# Default columns
DEFAULT_COLUMNS = [
    'amount', 'card_name', 'card_set', 'language', 'condition', 
    'foil', 'signed', 'alerts', 'price_diff_d7', 'liquidity', 'last_sold_date', 'from_price', 'trend_price',
    'ms_trend_price', 'efficient_price', 'conservative_price', 'value_price'
]

# Column categories for the selector
column_categories = {
    "Dimensions": [
        'amount', 'card_name', 'card_set', 'language', 'condition', 
        'foil', 'signed', 'country', 'liquidity', 'last_sold_date', 'alerts', 'notes', 
        'collection_number', 'rarity', 'reserved_list', 'set_release_date', 'frame_era', 'set_type'
    ],
    "Metrics": [
        'from_price', 'trend_price', 'ms_trend_price', 'efficient_price', 
        'conservative_price', 'value_price', 'total_stock', 'country_stock', 
        'price_growth', 'equity_in_country', 'equity_on_cardmarket', 'listed_price',
        'listed_stock', 'total_efficient_value', 'total_conservative_value', 'price_diff_d7'
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
    """Clean price values and return with thousand separator"""
    if pd.isna(value) or value == 'N/A':
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        # Remove currency symbols and spaces
        cleaned = str(value).replace('€', '').replace('£', '').replace('$', '').strip()
        # Replace comma with dot for decimal point
        cleaned = cleaned.replace(',', '.')
        # Split by dots and take the last value (assuming it's the decimal part)
        parts = cleaned.split('.')
        if len(parts) > 2:
            # If there are multiple dots, reconstruct the number properly
            integer_part = ''.join(parts[:-1])
            decimal_part = parts[-1]
            cleaned = f"{integer_part}.{decimal_part}"
        return float(cleaned)
    except:
        return None

def format_price(value):
    """Format price values with currency symbol"""
    if pd.isna(value) or value is None:
        return None
    try:
        # Convert to float first
        float_value = float(value)
        return f"{float_value:,.2f}"
    except (ValueError, TypeError):
        return value  # Return original value if conversion fails

def clean_percentage(value):
    """
    Clean percentage values with extensive error handling.
    Returns float as decimal (e.g., 0.05 for 5%)
    """
    if pd.isna(value) or value == 'N/A' or value == '' or value == 'null' or value is None:
        return None
        
    # If already a float/int, just handle the decimal conversion
    if isinstance(value, (float, int)):
        # If it's already in decimal form (between -1 and 1), return as is
        if -1 <= value <= 1:
            return value
        # If it's in percentage form (e.g., 5 for 5%), convert to decimal
        return value / 100
        
    # Handle string values
    try:
        # Remove any whitespace and handle different percentage formats
        cleaned = str(value).strip().replace(',', '.').lower()
        
        # Handle percentage sign
        if '%' in cleaned:
            cleaned = cleaned.replace('%', '').strip()
            value_float = float(cleaned) / 100
        else:
            value_float = float(cleaned)
            # If the number is too large to be a decimal, assume it's a percentage
            if value_float > 1 or value_float < -1:
                value_float = value_float / 100
                
        return value_float
        
    except (ValueError, TypeError, AttributeError):
        return None

def format_percentage(value):
    """
    Format decimal values as percentage strings with 1 decimal place
    e.g., 0.05 becomes '5.0%'
    """
    if pd.isna(value) or value is None:
        return None
        
    try:
        value_float = float(value)
        # Only format if the value is not 0
        if value_float != 0:
            return f"{value_float * 100:,.0f}%"
        else:
            return "0%"
    except (ValueError, TypeError):
        return None

@st.cache_data
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
    
    # Get glossary sheet
    sheet_glossary = gc.open_by_key('1aVRXJ373tp_4gjd1bPpexrpwOrVwr0Z49LB1SMz_90U')
    worksheet_glossary = sheet_glossary.get_worksheet(0)
    
    # Get data and convert to DataFrame
    data_glossary = worksheet_glossary.get_all_values()
    df_glossary = pd.DataFrame(data_glossary[1:], columns=data_glossary[0])

    df = df.merge(df_glossary, left_on=['card_name', 'card_set'], right_on=['card_name', 'card_set'], how='left')

    # Create card_name_set column
    df['card_name_set'] = df.apply(
        lambda x: f"{x['card_name']} - {x['card_set']} - {'Foil' if x['foil'] == 'Yes' else 'Regular'}", 
        axis=1
    )
    
    # Price-related columns
    price_columns = [
        'trend_price', 'efficient_price', 'conservative_price', 
        'from_price', 'value_price', 'purchase_price', 'listed_price',
        'total_efficient_value', 'total_conservative_value', 'ms_trend_price'
    ]
    
    # Other numeric columns
    numeric_columns = [
        'amount', 'total_stock', 'country_stock', 'listed_stock'
    ]
    
    percentage_columns = [
        'price_growth', 'equity_in_country', 'equity_on_cardmarket', 'price_diff_d7'
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
    text_columns = ['card_name', 'card_set', 'language', 'condition', 'foil', 'signed', 'country', 'alerts', 'collection_number', 'rarity', 'reserved_list', 'set_release_date', 'frame_era', 'set_type']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].replace('N/A', None)

    
    # Clean percentage columns first (convert to decimal form)
    for col in percentage_columns:
        if col in df.columns:
            # Convert NaN to None
            df[col] = df[col].replace({pd.NA: None, np.nan: None})
            # Apply cleaning function
            df[col] = df[col].apply(clean_percentage)
    
    df['difference'] = (pd.to_datetime(df['date'], errors='coerce') - pd.to_datetime(df['last_sold_date'], errors='coerce')).dt.days

    # Assign values based on the difference
    def categorize_difference(diff):
        if 0 <= diff <= 1:
            return 'Very High'
        elif 2 <= diff <= 7:
            return 'High'
        elif 8 <= diff <= 14:
            return 'Moderate'
        elif 15 <= diff <= 30:
            return 'Low'
        elif diff > 30:
            return 'Very Low'
        else:
            return 'Not Available'  # In case of negative differences

    # Create the new column based on the difference
    df['liquidity'] = df['difference'].apply(categorize_difference)
    df = df.drop(columns=['difference'])

    return df


def verify_credentials(username, password):
    """Verify username and password against the setup sheet"""
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
        return False
    
    # Check if password matches
    stored_password = user_row['password'].iloc[0]
    return password == stored_password

def render_footer():
        logo_path = os.path.join(assets_path, 'Alpha_Logo.png')
        with open(logo_path, "rb") as f:
            logo_contents = f.read()
        logo_encoded = base64.b64encode(logo_contents).decode()
    
        st.markdown(
            f"""
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                width: 100%;
                padding: 0px;
                margin-top: 0px;
                text-align: center;
            ">
                <p style="
                    color: #dddddd;
                    margin: 50px 0 -10px 0;
                    padding: 0;
                    font-size: 12px;
                    line-height: 1.5;
                ">POWERED BY FINANZAS<span style="color: #00a195; font-weight: bold;">MTG</span></p>
                <img src="data:image/png;base64,{logo_encoded}" style="width: 100px; height: auto;">
            </div>
            """,
            unsafe_allow_html=True
        )

# Move the login form from sidebar to main content
if 'username_selected' not in st.session_state:
    st.session_state.username_selected = False
    st.session_state.username = None  # Initialize username in session state

# Remove the sidebar login content and move it to main
if not st.session_state.username_selected:
    # Center-align the logo
    st.markdown(f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-top: 2rem;
            margin-bottom: 2rem;
        ">
            <img src="data:image/png;base64,{app_logo_encoded}" style="width: 400px; height: auto; margin-bottom: 2rem;">
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        input_username = st.text_input("Enter your username:")
        password = st.text_input("Enter your password:", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if verify_credentials(input_username, password):
                st.session_state.username = input_username
                st.session_state.username_selected = True
                st.rerun()
            else:
                st.error("Invalid username or password")

    # Display the intro text below login form
    st.info("""
    🦊 Welcome to Kitsune Codex, your intelligent MTG Portfolio Tracker!

    This dashboard provides insights into your Magic: The Gathering collection, helping you make informed decisions about your cards.

    All data is obtained from Cardmarket, the #1 MTG marketplace in Europe, to ensure you have up-to-date and relevant information for your collection. Use the tabs above to navigate through different views and discover the full potential of your MTG portfolio.
            
    Enter your username to get started! 🎉
    """)

    # Footer Logo
    logo_path = os.path.join(assets_path, 'Alpha_Logo.png')
    with open(logo_path, "rb") as f:
        logo_contents = f.read()
    logo_encoded = base64.b64encode(logo_contents).decode()

    render_footer()
    

# Main app content (only shown after login)
if st.session_state.username_selected and st.session_state.username:
    try:
        df = load_user_data(st.session_state.username)
        
        if len(df) == 0:
            st.error("No data found for this username")
        else:
            # Clean welcome header with date
            max_date = pd.to_datetime(df['date'], errors='coerce').max().strftime('%d/%m/%Y')
            # First, add the CSS style
            st.markdown("""
                <style>
                @media screen and (max-width: 768px) {
                    .welcome-text {
                        display: none !important;
                    }
                }
                </style>
            """, unsafe_allow_html=True)

            # Then, add the content with f-string
            welcome_text = f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 2rem;
                    padding: 1rem 0;
                ">
                    <div class="welcome-text">
                        <h1 style="
                            color: #ffffff;
                            margin: 0;
                            padding: 0;
                            font-size: 26px;
                            font-weight: 500;
                            line-height: 1;
                        ">👋🏻 Welcome, {st.session_state.username}!</h1>
                        <p style="
                            color: #dddddd;
                            margin: 0;
                            padding: 0;
                            font-size: 14px;
                            line-height: 1.5;
                            text-align: right;
                        ">{random.choice(TRIVIAS)}</p>
                    </div>
                    <img src="data:image/png;base64,{app_logo_encoded}" style="width: 400px; height: auto;">
                </div>
            """
            st.markdown(welcome_text, unsafe_allow_html=True)
            st.markdown(f'''<p style="
                            color: #ff8934;
                            margin: 0;
                            padding: 0;
                            font-size: 12px;
                            line-height: 1.5;
                            text-align: right;
                        ">Data from Cardmarket as of {max_date}</p>''', unsafe_allow_html=True)
            
            # Tabs for different views
            # Add this CSS to your existing styles
            st.markdown("""
                <style>
                /* Target the fifth tab specifically */
                .stTabs [data-baseweb="tab-list"] [data-baseweb="tab"]:nth-child(5) {
                    color: #ff8934 !important;
                }
                
                /* Optional: Change the color when the fifth tab is selected */
                .stTabs [data-baseweb="tab-list"] [data-baseweb="tab"][aria-selected="true"]:nth-child(5) {
                    color: #ff8934 !important;
                }
                         
                .stTabs [data-baseweb="tab-list"] [data-baseweb="tab"]:nth-child(5):hover {
                    color: #fab900 !important;
                    text-shadow: 0 0 20px rgba(255, 137, 52, 0.9) !important;
                    transform: scale(1.1) !important;  /* Grow to 110% size */
                    transition: all 0.3s ease !important;  /* Smooth transition for all properties */
                }

                /* Add base state transition for smooth animation */
                .stTabs [data-baseweb="tab-list"] [data-baseweb="tab"]:nth-child(5) {
                    transition: all 0.3s ease !important;
                }
                </style>
            """, unsafe_allow_html=True)

            tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Overview", "Price Analysis", "Inventory Details", "Historical Trends"])
            
            with tab1:
                st.markdown(f'''
                            <h3 style="color: #03a088; margin-bottom: 0px;">Portfolio Overview</h3>
                            <p style="color: #ffffff; margin: -10px 0 30px 0; line-height: 1.2;">{tab_descriptions["Portfolio Overview"]}</p>''', unsafe_allow_html=True)
            
                col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])

                metrics_style = """
                    style="
                        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFF 100%);
                        padding: 1.5rem;
                        border-radius: 5px;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
                    "
                """
                
                with col1:
                    total_cards = df['amount'].sum()
                    st.metric("Total Cards", f"{int(total_cards):,}")  # Format as integer
                
                with col2:
                    unique_cards = len(df)
                    st.metric("Unique Cards", f"{unique_cards:,}")  # Format as integer

                with col3:
                    total_value = df['total_efficient_value'].sum()
                    # Ensure total_value is float before formatting
                    if pd.notnull(total_value):
                        st.metric("Portfolio Value", f"€{float(total_value):,.0f}")
                    else:
                        st.metric("Portfolio Value", "N/A")
                
                with col4:
                    avg_price = df['efficient_price'].mean()
                    # Ensure avg_price is float before formatting
                    if pd.notnull(avg_price):
                        st.metric("Average Price", f"€{float(avg_price):,.2f}")
                    else:
                        st.metric("Average Price", "N/A")
                    
                with col5:
                    max_price_diff_d7 = df['price_diff_d7'].max()
                    max_price_diff_d7_card_name = df.loc[df['price_diff_d7'] == max_price_diff_d7, 'card_name'].iloc[0]
                    # Format percentage without f-string if it's already a string
                    if pd.notnull(max_price_diff_d7):
                        formatted_diff = format_percentage(max_price_diff_d7)
                        st.metric(
                            "Highest Price Change (7d)", 
                            f"{max_price_diff_d7_card_name}\n({formatted_diff})"
                        )
                    else:
                        st.metric("Highest Price Change (7d)", "N/A")

                # Create a consistent color mapping for all sets
                n_sets = len(df['card_set'].unique())
                colors = pc.sample_colorscale('Spectral', n_sets)  # You can change 'Viridis' to other scales
                
                # Get unique sets with their release dates
                set_dates = df[['card_set', 'set_release_date']].drop_duplicates()
                # Sort by release date
                sorted_sets = set_dates.sort_values('set_release_date')['card_set'].unique()

                # Create color mapping based on chronological order
                color_mapping = dict(zip(sorted_sets, colors))

                st.markdown('<br>', unsafe_allow_html=True)    
                st.markdown('<h5 style="color: #03a088; margin-bottom: -10px;">Portfolio Overview by Set - Card Price</h3>', unsafe_allow_html=True)

                # Calculate total portfolio value
                total_portfolio_value = df['total_efficient_value'].sum()
                
                # Create a temporary dataframe with percentage calculations
                tab_1_df = df.copy()
                tab_1_df['percentage'] = (tab_1_df['total_efficient_value'] / total_portfolio_value * 100)
                
                # Group by set and calculate sums and percentages
                set_data = tab_1_df.groupby('card_set').agg({
                    'total_efficient_value': 'sum',
                    'percentage': 'sum'
                }).reset_index()
                
                # Portfolio composition by set
                fig_sets = px.treemap(
                    set_data,
                    path=['card_set'],
                    values='total_efficient_value',
                    custom_data=['card_set', 'total_efficient_value', 'percentage']  # Add percentage to custom data
                )
                
                # Update treemap layout and hover template
                fig_sets.update_layout(
                    height=450,
                    margin=dict(t=20, l=20, r=20, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(
                        color='#ffffff',
                        size=14
                    ),
                    autosize=True
                )
                
                # Customize hover template
                fig_sets.update_traces(
                    hovertemplate="<br>".join([
                        "<b>%{customdata[0]}</b>",  # Set name
                        f"{COLUMN_NAMES['total_efficient_value']}: €%{{customdata[1]:.2f}}",  # Value with euro symbol
                        "Percentage of Portfolio: %{customdata[2]:.1f}%",  # Percentage with 1 decimal
                        "<extra></extra>"  # Remove secondary box
                    ])
                )
                
                fig_sets.data[0].marker.colors = [color_mapping[set_name] for set_name in set_data['card_set']]
                
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
                
                st.markdown("<br>", unsafe_allow_html=True)

                # Add header for second chart
                st.markdown('<h5 style="color: #03a088; margin-bottom: -10px;">Portfolio Distribution by Set - Amount of Cards</h3>', unsafe_allow_html=True)

                # Create a temporary dataframe for amount calculations
                amount_data = df.groupby('card_set').agg({
                    'amount': 'sum'
                }).reset_index()

                # Calculate percentages for hover info
                total_amount = amount_data['amount'].sum()
                amount_data['percentage'] = (amount_data['amount'] / total_amount * 100)

                # Create treemap for amounts
                fig_amounts = px.treemap(
                    amount_data,
                    path=['card_set'],
                    values='amount',
                    custom_data=['card_set', 'amount', 'percentage']
                )

                # Update treemap layout and hover template - keeping consistent styling
                fig_amounts.update_layout(
                    height=450,
                    margin=dict(t=20, l=20, r=20, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(
                        color='#ffffff',
                        size=14
                    ),
                    autosize=True
                )

                # Customize hover template
                fig_amounts.update_traces(
                    hovertemplate="<br>".join([
                        "<b>%{customdata[0]}</b>",  # Set name
                        "Amount: %{customdata[1]:.0f}",  # Amount without decimal places
                        "Percentage of Collection: %{customdata[2]:.1f}%",  # Percentage with 1 decimal
                        "<extra></extra>"  # Remove secondary box
                    ])
                )

                fig_amounts.data[0].marker.colors = [color_mapping[set_name] for set_name in amount_data['card_set']]

                # Display the chart
                st.plotly_chart(
                    fig_amounts, 
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

                # Add spacing
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Create three columns for pie charts
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Reserved List pie chart
                    st.markdown('<h5 style="color: #03a088; margin-bottom: -10px;">Reserved List Distribution</h3>', unsafe_allow_html=True)
                    
                    # Group by Reserved List status and count distinct cards
                    rl_data = df.groupby('reserved_list')['card_name'].nunique().reset_index()
                    rl_data['percentage'] = (rl_data['card_name'] / rl_data['card_name'].sum() * 100)
                    
                    # Create pie chart
                    fig_rl = px.pie(
                        rl_data,
                        values='card_name',
                        names='reserved_list',
                        custom_data=['percentage']
                    )
                    
                    # Update layout with centered bottom legend
                    fig_rl.update_layout(
                        height=350,
                        margin=dict(t=20, l=20, r=20, b=60),  # Increased bottom margin for legend
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#ffffff'),
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="top",
                            y=-0.2,  # Move legend below chart
                            xanchor="center",
                            x=0.5,  # Center legend horizontally
                            font=dict(size=12)
                        )
                    )
                    
                    # Update traces
                    fig_rl.update_traces(
                        textinfo='percent+label',
                        hovertemplate="<br>".join([
                            "<b>%{label}</b>",
                            "Cards: %{value}",
                            "Percentage: %{customdata[0]:.1f}%",
                            "<extra></extra>"
                        ]),
                        marker=dict(colors=['#5b50c1', '#03a088'])  # Green for Yes, Purple for No
                    )
                    
                    st.plotly_chart(fig_rl, use_container_width=True)
                
                with col2:
                    # Rarity pie chart
                    st.markdown('<h5 style="color: #03a088; margin-bottom: -10px;">Rarity Distribution</h3>', unsafe_allow_html=True)
                    
                    # Group by Rarity and count distinct cards
                    rarity_data = df.groupby('rarity')['card_name'].nunique().reset_index()
                    rarity_data['percentage'] = (rarity_data['card_name'] / rarity_data['card_name'].sum() * 100)
                    
                    # Create pie chart
                    fig_rarity = px.pie(
                        rarity_data,
                        values='card_name',
                        names='rarity',
                        custom_data=['percentage']
                    )
                    
                    # Update layout with centered bottom legend
                    fig_rarity.update_layout(
                        height=350,
                        margin=dict(t=20, l=20, r=20, b=60),  # Increased bottom margin for legend
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#ffffff'),
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="top",
                            y=-0.2,  # Move legend below chart
                            xanchor="center",
                            x=0.5,  # Center legend horizontally
                            font=dict(size=12)
                        )
                    )
                    
                    # Color mapping for rarities
                    rarity_colors = {
                        'Common': '#95a5a6',
                        'Uncommon': '#7f8c8d',
                        'Rare': '#fab900',
                        'Mythic': '#e67e22',
                        'Special': '#9b59b6'
                    }
                    
                    # Update traces
                    fig_rarity.update_traces(
                        textinfo='percent+label',
                        hovertemplate="<br>".join([
                            "<b>%{label}</b>",
                            "Cards: %{value}",
                            "Percentage: %{customdata[0]:.1f}%",
                            "<extra></extra>"
                        ]),
                        marker=dict(colors=[rarity_colors.get(r, '#ffffff') for r in rarity_data['rarity']])
                    )
                    
                    st.plotly_chart(fig_rarity, use_container_width=True)
                
                with col3:
                    # Listed Status pie chart
                    st.markdown('<h5 style="color: #03a088; margin-bottom: -10px;">Listed Cards on Cardmarket</h3>', unsafe_allow_html=True)
                    
                    # Create listed status data
                    df['listed_status'] = df['listed_stock'].apply(lambda x: 'Listed' if pd.notnull(x) and str(x).replace('.', '').isdigit() and float(x) > 0 else 'Not Listed')
                    listed_counts = df.groupby('listed_status')['card_name'].nunique().reset_index()
                    listed_counts['percentage'] = (listed_counts['card_name'] / listed_counts['card_name'].sum() * 100)
                    
                    # Define color mapping
                    listed_colors = {
                        'Listed': '#00a195',
                        'Not Listed': '#e9536f'
                    }
                    
                    # Create pie chart
                    fig_listed = px.pie(
                        listed_counts,
                        values='card_name',
                        names='listed_status',
                        custom_data=['percentage'],
                        color='listed_status',
                        color_discrete_map=listed_colors
                    )
                    
                    # Update layout with centered bottom legend
                    fig_listed.update_layout(
                        height=350,
                        margin=dict(t=20, l=20, r=20, b=60),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#ffffff'),
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="top",
                            y=-0.2,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=12)
                        ),
                        uniformtext_minsize=12,
                        uniformtext_mode='hide'
                    )
                    
                    # Update traces with white text
                    fig_listed.update_traces(
                        textinfo='percent+label',
                        textfont=dict(color='white', size=12),  # Force white text
                        hovertemplate="<br>".join([
                            "<b>%{label}</b>",
                            "Cards: %{value}",
                            "Percentage: %{customdata[0]:.1f}%",
                            "<extra></extra>"
                        ])
                    )
                    
                    st.plotly_chart(fig_listed, use_container_width=True)
                render_footer()

            with tab2:
                st.markdown(f'''
                            <h5 style="color: #03a088; margin-bottom: -10px;">Price Analysis</h3>
                            <p style="color: #ffffff; margin: -10px 0 30px 0; line-height: 1.2;">{tab_descriptions["Price Analysis"]}</p>''', unsafe_allow_html=True)

                # Add custom CSS for the chart container and dropdown
                st.markdown("""
                    <style>
                    /* Existing chart container styles ... */
                    
                    /* Style for the metric selector */
                    .metric-selector {
                        margin-bottom: 1rem;
                        margin-top: 30px;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                # Price distribution title and chart
                st.markdown('<h5 style="color: #03a088; margin-bottom: 0px;">Price Distribution</h3>', unsafe_allow_html=True)
                fig_price = px.histogram(
                    df,
                    x='efficient_price',
                    nbins=5000,
                    labels={'efficient_price': 'Card Price (€)', 'count': 'Number of Cards'}
                )

                fig_price.update_traces(
                    marker_color='#9b8ac1',  # Main color for bars
                    marker_line_color='#9b8ac1',  # Border color for bars
                    marker_line_width=3  # Border width
                )
                
                # Update histogram layout with explicit y-axis title
                fig_price.update_layout(
                    height=450,
                    margin=dict(t=20, l=20, r=20, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff'),
                    autosize=True,
                    xaxis_title='Card Price (€)',
                    yaxis_title='Number of Cards'  # This will force the y-axis label
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
                
                # Create two columns for title and dropdown
                col_title, col_dropdown = st.columns([2, 1])  # Adjust ratio as needed (3:1 here)

                # Add styling for the dropdown
                st.markdown("""
                    <style>
                    /* Dropdown container and input */
                    div[data-baseweb="select"] {
                        background-color: #202020 !important;
                        border: 1px solid rgba(255, 255, 255, 0.1) !important;
                        border-radius: 4px !important;
                        width: 100% !important;  /* Changed from 200px to 100% */
                        margin-top: 30px;
                    }
                    
                    /* Make the select container fill the width */
                    [data-testid="column"] [data-testid="stMultiSelect"] {
                        width: 100% !important;
                    }
                    
                    /* Force width on the select container */
                    div[data-baseweb="select"] > div[data-baseweb="select-container"] {
                        width: 100% !important;
                    }
                    
                    /* Make the input field fill the width */
                    div[data-baseweb="select"] input {
                        width: 100% !important;
                    }
                    
                    /* Dropdown options menu */
                    div[role="listbox"] {
                        background-color: #202020 !important;
                        border: 1px solid #03a088 !important;
                        width: 100% !important;
                    }
                    
                    /* Make sure the multiselect container fills the column */
                    .stMultiSelect {
                        width: 100% !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                # Dropdown in the right column with right alignment
                with col_dropdown:
                    # Create a container with right alignment
                    container = st.container()
                    with container:
                        selected_metric = st.selectbox(
                            "Select Price Metric",
                            ["Today vs D7", "Price Growth"],
                            key="price_metric_selector",
                            label_visibility="collapsed"
                        )

                # Title in the left column
                with col_title:
                    st.markdown(f'<h5 style="color: #03a088; margin-bottom: -10px; margin-top: 30px;">{selected_metric} vs Current Price</h3>', unsafe_allow_html=True)


                # Create a temporary dataframe with formatted values based on selection
                temp_df = df.copy()
                if selected_metric == "Price Growth":
                    y_column = 'price_growth'
                    y_label = 'Price Growth (%)'
                    temp_df['plot_value'] = temp_df['price_growth'].apply(lambda x: x * 100 if pd.notnull(x) else x)
                else:  # Today vs D7
                    y_column = 'price_diff_d7'
                    y_label = 'Today vs D7 (%)'
                    temp_df['plot_value'] = temp_df['price_diff_d7'].apply(lambda x: x * 100 if pd.notnull(x) else x)

                fig_growth = px.scatter(
                    temp_df,
                    x='efficient_price',
                    y='plot_value',
                    hover_data={
                        'card_name': True,
                        'plot_value': ':.1f',  # Format to 1 decimal place
                    },
                    labels={
                        'efficient_price': 'Current Price (€)',
                        'plot_value': y_label,
                        'card_name': 'Card Name'
                    }
                )

                # Update the layout maintaining transparent background and adding % suffix
                fig_growth.update_layout(
                    height=450,
                    margin=dict(t=20, l=20, r=20, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff'),
                    autosize=True,
                    yaxis=dict(
                        ticksuffix="%",  # Add % to tick labels
                    )
                )
                
                fig_growth.update_traces(
                    marker=dict(
                        color='#9b8ac1',  # Dot color
                        size=8,  # Dot size
                        opacity=1,  # Dot opacity
                        line=dict(
                            color='#9b8ac1',  # Dot border color
                            width=0  # Dot border width
                        )
                    ))
                
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
                
                
                # Add spacing after charts
                st.markdown("<br>", unsafe_allow_html=True)

                # Create two columns for the tables
                col1, col2 = st.columns(2)

                # Prepare the data for both tables
                table_columns = ['card_name', 'card_set', 'efficient_price', 'price_diff_d7']
                display_columns = ['Rank', 'Card Name', 'Set', 'Price', '7d Change']

                def format_price_diff(value):
                    """Format price difference with color based on value"""
                    if pd.isna(value) or value is None:
                        return "N/A"
                    
                    percentage = value * 100
                    color = '#fab900'  # Default color (0%)
                    if percentage > 0:
                        color = '#00a195'  # Positive
                    elif percentage < 0:
                        color = '#e9536f'  # Negative
                    
                    return f'<span style="color: {color}">{percentage:.1f}%</span>'

                # Reserved List Cards (Left table)
                
                
                with col1:
                    st.markdown('<h5 style="color: #03a088; margin-bottom: -10px;">Top 10 Reserved List Cards</h3>', unsafe_allow_html=True)
                    
                    # Filter and sort reserved list cards
                    rl_cards = df[df['reserved_list'] == 'Yes'].sort_values('efficient_price', ascending=False)
                    top_10_rl = rl_cards[table_columns].head(10).copy()
                    top_10_rl.insert(0, 'rank', range(1, len(top_10_rl) + 1))
                    top_10_rl['efficient_price'] = top_10_rl['efficient_price'].apply(lambda x: f"€{x:,.2f}")
                    top_10_rl['price_diff_d7'] = top_10_rl['price_diff_d7'].apply(format_price_diff)
                    
                    # Rename columns for display
                    top_10_rl.columns = display_columns
                    
                    # Display table with styling
                    st.markdown(
                        top_10_rl.to_html(index=False, escape=False),
                        unsafe_allow_html=True
                    )

                # Non-Reserved List Cards (Right table)
                with col2:
                    st.markdown('<h5 style="color: #03a088; margin-bottom: -10px;">Top 10 Non-Reserved List Cards</h3>', unsafe_allow_html=True)
                    
                    # Filter and sort non-reserved list cards
                    non_rl_cards = df[df['reserved_list'] == 'No'].sort_values('efficient_price', ascending=False)
                    top_10_non_rl = non_rl_cards[table_columns].head(10).copy()
                    top_10_non_rl.insert(0, 'rank', range(1, len(top_10_non_rl) + 1))
                    top_10_non_rl['efficient_price'] = top_10_non_rl['efficient_price'].apply(lambda x: f"€{x:,.2f}")
                    top_10_non_rl['price_diff_d7'] = top_10_non_rl['price_diff_d7'].apply(format_price_diff)
                    
                    # Rename columns for display
                    top_10_non_rl.columns = display_columns
                    
                    # Display table with styling
                    st.markdown(
                        top_10_non_rl.to_html(index=False, escape=False),
                        unsafe_allow_html=True
                    )

                # After the existing Reserved List and Non-Reserved List tables in tab2
                # Add two more columns for price changes
                st.markdown("<br>", unsafe_allow_html=True)
                # Create two columns for the tables
                col3, col4 = st.columns(2)

                # Biggest Gainers (Left table)
                with col3:
                    st.markdown('<h5 style="color: #03a088; margin-bottom: -10px;">Top 10 Price Gainers (7d)</h3>', unsafe_allow_html=True)
                    
                    # Filter and sort by price_diff_d7 descending
                    top_gainers = df[table_columns].sort_values('price_diff_d7', ascending=False).head(10).copy()
                    
                    # Add rank and format columns
                    top_gainers.insert(0, 'rank', range(1, len(top_gainers) + 1))
                    top_gainers['efficient_price'] = top_gainers['efficient_price'].apply(lambda x: f"€{x:,.2f}")
                    top_gainers['price_diff_d7'] = top_gainers['price_diff_d7'].apply(format_price_diff)
                    
                    # Rename columns for display
                    top_gainers.columns = display_columns
                    
                    # Display table with styling
                    st.markdown(
                        top_gainers.to_html(index=False, escape=False),
                        unsafe_allow_html=True
                    )

                # Biggest Losers (Right table)
                with col4:
                    st.markdown('<h5 style="color: #03a088; margin-bottom: -10px;">Top 10 Price Losers (7d)</h3>', unsafe_allow_html=True)
                    
                    # Filter and sort by price_diff_d7 ascending
                    top_losers = df[table_columns].sort_values('price_diff_d7', ascending=True).head(10).copy()
                    
                    # Add rank and format columns
                    top_losers.insert(0, 'rank', range(1, len(top_losers) + 1))
                    top_losers['efficient_price'] = top_losers['efficient_price'].apply(lambda x: f"€{x:,.2f}")
                    top_losers['price_diff_d7'] = top_losers['price_diff_d7'].apply(format_price_diff)
                    
                    # Rename columns for display
                    top_losers.columns = display_columns
                    
                    # Display table with styling
                    st.markdown(
                        top_losers.to_html(index=False, escape=False),
                        unsafe_allow_html=True
                    )

                st.markdown("""
                    <style>
                    /* Table styling */
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 0;
                        background: #202020;
                        border-radius: 2px !important;
                        overflow: hidden;
                        font-size: 12px;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                        border: 1px solid #1f2335 !important;  /* Added border color */
                    }
                    
                    /* More specific border styling */
                    table, 
                    table.dataframe,
                    .dataframe table {
                        border: 1px solid #363636 !important;
                        border-color: #363636 !important;
                    }
                    
                    /* Add border color to cells if needed */
                    table td,
                    table th {
                        border-color: #363636 !important;
                    }   

                    th {
                        background: #363636 !important;
                        padding: 12px 16px !important;
                        font-weight: 600 !important;
                        color: #03a088 !important;
                        text-align: left !important;
                    }
                    
                    td {
                        padding: 12px 16px !important;
                        color: #ffffff !important;
                        
                    }
                    
                    /* Rank column styling */
                    td:first-child {
                        font-weight: 700;
                        color: #c1c1c1 !important;
                    }
                    
                    /* Price change column styling */
                    td:last-child {
                        font-weight: 500;
                    }
                    
                    /* Hover effect on rows */
                    tr:hover td {
                        background: #292e42;
                    }
                    </style>
                """, unsafe_allow_html=True)

                render_footer()

            with tab3:
                st.markdown(f'''
                            <h3 style="color: #03a088; margin-bottom: 0px;">Inventory Details</h3>
                            <p style="color: #ffffff; margin: -10px 0 30px 0; line-height: 1.2;">{tab_descriptions["Inventory Details"]}</p>''', unsafe_allow_html=True)
                
                # Create two columns for dimensions and metrics
                col1, col2 = st.columns(2)
                
                selected_columns = []
                
                # Dimensions column
                with col1:
                    st.markdown('<p class="category-header-tab3">Dimensions</p>', unsafe_allow_html=True)
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
                    st.markdown('<p class="category-header-tab3">Metrics</p>', unsafe_allow_html=True)
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
                
                # Define percentage columns
                percentage_columns = [
                    'price_growth', 'equity_in_country', 'equity_on_cardmarket', 'price_diff_d7'
                ]
                
                price_columns = [
                    'trend_price', 'efficient_price', 'conservative_price', 
                    'from_price', 'value_price', 'purchase_price', 'listed_price',
                    'total_efficient_value', 'total_conservative_value', 'ms_trend_price']

                # Convert price columns to float before display
                for col in price_columns:
                    if col in display_df.columns:
                        # Keep the original numeric values instead of formatting them
                        display_df[col] = pd.to_numeric(display_df[col], errors='coerce')
                
                # Format percentage columns
                for col in percentage_columns:
                    if col in display_df.columns:
                        # Convert NaN to None before formatting
                        display_df[col] = display_df[col].replace({pd.NA: None, np.nan: None})
                        display_df[col] = display_df[col].apply(format_percentage)
                
                # Rename columns for display
                display_df.columns = [COLUMN_NAMES.get(col, col.replace('_', ' ').title()) for col in display_df.columns]
                
                # Update the dataframe display section
                if selected_columns:
                    display_columns = [COLUMN_NAMES.get(col, col.replace('_', ' ').title()) for col in selected_columns]
                    df_display = display_df[display_columns].copy()
                    
                    # Transform Alerts column
                    if 'Alerts' in df_display.columns:
                        def transform_alerts(value):
                            if pd.isna(value) or value is None:
                                return None
                            # Convert to string to handle all cases
                            value = str(value)
                            # Handle L and U cases first
                            if value == 'L':
                                return 'Listed'
                            if value == 'U':
                                return 'Urgent'
                            # Remove € sign and try to convert to integer
                            try:
                                cleaned_value = value.replace('€', '').strip()
                                return str(int(float(cleaned_value)))
                            except Exception:
                                return value
                        
                        df_display['Alerts'] = df_display['Alerts'].apply(transform_alerts)
                    
                    gb = GridOptionsBuilder.from_dataframe(df_display)
                    
                    # Set default column properties
                    gb.configure_default_column(
                        filterable=True,
                        sorteable=True,
                        resizable=True,
                        filter=True,
                        menuTabs=['filterMenuTab', 'generalMenuTab']
                    )
                    
                    # Configure specific columns
                    for col in df_display.columns:
                        if col == 'Card Name':
                            # Make Card Name column wider
                            gb.configure_column(
                                col,
                                minWidth=300,  # Minimum width in pixels
                                type=["textColumn", "textColumnFilter"],
                                filter=True,
                                filterParams={
                                    'buttons': ['reset', 'apply'],
                                    'closeOnApply': True
                                }
                            )
    
                        elif col in ['From Price', 'Trend Price', 'MS Trend Price', 'Efficient Price', 'Conservative Price', 'Value Price', 'Purchase Price', 'Cardmarket Listed Price', 'Listed Price']:
                            # Make Card Name column wider
                            gb.configure_column(
                                col,
                                valueFormatter="'€' + x.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})"
                            )

                        elif col in ['Today vs D7', 'Price Growth', 'Equity in Country', 'Equity on Cardmarket']:
                            cellStyle = JsCode("""
                            function(params) {
                                if (params.value === null || params.value === undefined) return {};
                                const val = parseFloat(params.value.replace('%', ''));
                                if (val > 0) return { color: '#00a195' };
                                if (val < 0) return { color: '#e9536f' };
                                return { color: '#fab900' };
                            }
                            """)
                            gb.configure_column(
                                col,
                                type=["numericColumn", "numberColumnFilter"],
                                filter=True,
                                filterParams={
                                    'buttons': ['reset', 'apply'],
                                    'closeOnApply': True
                                },
                                cellStyle=cellStyle
                            )
                        else:
                            gb.configure_column(
                                col,
                                type=["textColumn", "textColumnFilter"],
                                filter=True,
                                filterParams={
                                    'buttons': ['reset', 'apply'],
                                    'closeOnApply': True
                                }
                            )

                    # Add this specific configuration for the Alerts column
                    if 'Alerts' in df_display.columns:
                        alerts_cell_style = JsCode("""
                        function(params) {
                            if (params.value === null || params.value === undefined) return {};
                            if (params.value === 'Listed') return { color: '#6d6ed1' };
                            if (params.value === 'Urgent') return { color: '#5b50c1' };
                            const val = parseInt(params.value);
                            if (isNaN(val)) return {};
                            const colors = {
                                0: '#ffffff',
                                1: '#ffd4d4',
                                2: '#ffb3b3',
                                3: '#ff8080',
                                4: '#ff4d4d',
                                5: '#e9536f'
                            };
                            return { color: colors[val] || '#ffffff' };
                        }
                        """)
                        
                        gb.configure_column(
                            'Alerts',
                            type=["textColumn", "textColumnFilter"],
                            filter=True,
                            filterParams={
                                'buttons': ['reset', 'apply'],
                                'closeOnApply': True
                            },
                            cellStyle=alerts_cell_style
                        )

                    if 'Liquidity' in df_display.columns:
                        liquidity_cell_style = JsCode("""
                        function(params) {
                            if (params.value === null || params.value === undefined) return {};
                            if (params.value === 'Very High') return { color: '#43aa8b' };
                            if (params.value === 'High') return { color: '#90be6d' };
                            if (params.value === 'Moderate') return { color: '#f9c74f' };
                            if (params.value === 'Low') return { color: '#f8961e' };
                            if (params.value === 'Very Low') return { color: '#f94144' };
                            const val = parseInt(params.value);
                            if (isNaN(val)) return {};
                            return { color: colors[val] || '#ffffff' };
                        }
                        """)
                        
                        gb.configure_column(
                            'Liquidity',
                            type=["textColumn", "textColumnFilter"],
                            filter=True,
                            filterParams={
                                'buttons': ['reset', 'apply'],
                                'closeOnApply': True
                            },
                            cellStyle=liquidity_cell_style
                        )

                    # Add additional grid options
                    grid_options = gb.build()
                    grid_options['enableRangeSelection'] = True
                    grid_options['enableColumnFilter'] = True
                    grid_options['enableFilter'] = True
                    
                    # Custom CSS for AgGrid
                    grid_css = {
                        ".ag-root.ag-theme-streamlit": {"background-color": "#202020"},
                        ".ag-theme-streamlit .ag-header": {"background-color": "#1f2335"},
                        ".ag-theme-streamlit .ag-header-cell": {"color": "#03a088"},
                        ".ag-theme-streamlit .ag-cell": {"color": "#c0caf5"},
                        ".ag-theme-streamlit .ag-row-even": {"background-color": "#202020"},
                        ".ag-theme-streamlit .ag-row-odd": {"background-color": "#1f2335"},
                        ".ag-theme-streamlit .ag-row:hover": {"background-color": "#292e42"},
                        ".ag-theme-streamlit .ag-filter-toolpanel-header": {"background-color": "#1f2335", "color": "#03a088"},
                        ".ag-theme-streamlit .ag-filter": {"background-color": "#202020"},
                        ".ag-theme-streamlit .ag-filter-header": {"background-color": "#1f2335"},
                        ".ag-theme-streamlit .ag-filter-filter": {"background-color": "#1f2335", "color": "#c0caf5", "border-color": "#03a088"},
                        ".ag-theme-streamlit .ag-filter-value": {"background-color": "#1f2335", "color": "#c0caf5", "border-color": "#03a088"},
                        ".ag-theme-streamlit .ag-menu": {"background-color": "#202020", "border-color": "#03a088"},
                        ".ag-theme-streamlit .ag-menu-option": {"color": "#c0caf5"},
                        ".ag-theme-streamlit .ag-menu-option:hover": {"background-color": "#292e42"}
                    }
                    
                    # Display the grid
                    AgGrid(
                        df_display,
                        gridOptions=grid_options,
                        height=600,
                        custom_css=grid_css,
                        theme="streamlit",
                        allow_unsafe_jscode=True,
                        update_mode="model_changed",
                        enable_enterprise_modules=False
                    )
                else:
                    st.warning("Please select at least one column to display")

                render_footer()

            with tab4:
                st.markdown(f'''
                            <h3 style="color: #03a088; margin-bottom: 0px;">Historical Trends</h3>
                            <p style="color: #ffffff; margin: -10px 0 30px 0; line-height: 1.2;">{tab_descriptions["Historical Trends"]}</p>''', unsafe_allow_html=True)
                
                # Load historical data
                df_historical = load_historical_data()
                
                if not df_historical.empty:
                    # Get user's cards
                    user_cards = df['card_name_set'].unique()
                    
                    # Filter historical data for user's cards only
                    df_historical_filtered = df_historical[df_historical['card_name_set'].isin(user_cards)]
                    if not df_historical_filtered.empty:
                        # Convert date column to datetime if it's not already
                        df_historical_filtered['date'] = pd.to_datetime(df_historical_filtered['date'], errors='coerce')
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            selected_card = st.selectbox(
                                "Select a Card",
                                options=sorted(user_cards),
                                index=0,
                                label_visibility="visible",
                                key="tab4_select"
                            )

                        st.markdown('<br>', unsafe_allow_html=True)

                        # Filter data for selected card
                        card_data = df_historical_filtered[df_historical_filtered['card_name_set'] == selected_card]

                        if not card_data.empty:
                            # Add metrics before the chart
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                min_price = card_data['efficient_price'].min()
                                st.metric(f"Lowest Price", f"€{min_price:.2f}")
                            
                            with col2:
                                max_price = card_data['efficient_price'].max()
                                st.metric(f"Highest Price", f"€{max_price:.2f}")
                            
                            with col3:
                                current_price = card_data.iloc[-1]['efficient_price']
                                st.metric(f"Current Price", f"€{current_price:.2f}")

                            with col4:
                                avg_price = card_data['efficient_price'].mean()
                                st.metric(f"Average Price", f"€{avg_price:.2f}")
                            
                            #st.markdown(f'<p style="color: #ffffff; margin-bottom: 1rem;">Price History for {selected_card}</p>', unsafe_allow_html=True)

                            # Create the figure with both series
                            fig = px.line(
                                card_data,
                                x='date',
                                y='efficient_price',
                                labels={
                                    'date': 'Date',
                                    'efficient_price': 'Price (€)'
                                }
                            )

                            # Add the constant average price line
                            fig.add_hline(
                                y=avg_price,
                                line_dash="dash",
                                line_width=1,
                                line_color="#fab900",
                                annotation_text=f"Avg: €{avg_price:.2f}",
                                annotation_position="left",
                                annotation_font_color="#fab900"
                            )

                            # Update the layout to ensure colors are applied
                            fig.update_layout(
                                showlegend=True,
                                hovermode='x unified'
                            )

                            # Update legend names
                            fig.data[0].name = 'Price'
                            
                            # Update layout with specific title font size
                            fig.update_layout(
                                height=550,
                                margin=dict(t=30, l=30, r=30, b=30),
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#ffffff'),
                                autosize=True,
                                showlegend=False,
                                title=dict(
                                    text=f'Price History for {selected_card}',
                                    font=dict(size=14),
                                    y=1,  # Move title down from top (1.0 is top, 0 is bottom)
                                    yanchor='top',  # Anchor point for the y position
                                    pad=dict(b=20, l=20)  # Add padding above (t) and below (b) the title
                                ),
                                xaxis=dict(
                                    showgrid=True,
                                    gridcolor='rgba(255, 255, 255, 0.1)',
                                    tickformat='%Y-%m-%d',
                                    title=None 
                                ),
                                yaxis=dict(
                                    showgrid=True,
                                    gridcolor='rgba(255, 255, 255, 0.1)',
                                    tickprefix='€',
                                    range=[0, (card_data['efficient_price'].max() * 1.15)]
                                )
                            )
                            
                            # Update line style
                            fig.update_traces(
                                line=dict(color='#03a088', width=2),
                                hovertemplate='<b>Date</b>: %{x|%Y-%m-%d}<br>' +
                                            '<b>Price</b>: €%{y:.2f}<extra></extra>'
                            )
                            
                            # Display the chart
                            st.plotly_chart(
                                fig,
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
                            
                        else:
                            st.warning("No historical data available for selected card")
                    else:
                        st.warning("No historical data found for your cards")
                else:
                    st.error("Unable to load historical data")

                # Add targeted CSS
                st.markdown("""
                    <style>
                    /* Target the specific selectbox in tab4 */
                    [data-key="tab4_card_select"] {
                        width: 100vw !important;  /* Use viewport width */
                        max-width: none !important;
                    }

                    [data-testid="stSelectbox"],
                    [data-testid="stSelectbox"] > div {
                        width: 800px;
                    }


                    /* Remove any padding or margins that might be limiting width */
                    .main .block-container {
                        max-width: 100% !important;
                        padding-left: 1rem !important;
                        padding-right: 1rem !important;
                    }
                    </style>
                """, unsafe_allow_html=True)

                render_footer()

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

else:

    # Add social media links with logos
    assets_path = os.path.join(os.path.dirname(__file__), 'assets')



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
        background: #202020;
        padding: 2rem;
        border-radius: 4px;
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
        border-radius: 4px !important;
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

st.markdown("""
    <style>
    /* Remove header link styling */
    .stMarkdown a {
        text-decoration: none !important;
        color: inherit !important;
        pointer-events: none !important;
    }
    
    /* Ensure headers don't show link behavior */
    h1, h2, h3, h4, h5, h6 {
        pointer-events: none !important;
    }
    
    /* Remove hover effects */
    .stMarkdown a:hover {
        text-decoration: none !important;
        color: inherit !important;
    }
    </style>
""", unsafe_allow_html=True) 

# In the main CSS block where other styles are defined (after the existing styles)
st.markdown("""
    <style>
    /* Style for Twitter link */
    .stAlert a {
        color: inherit;
        text-decoration: none;
    }

    .stAlert a:hover {
        color: #03a088 !important;
    }

    .fa-x-twitter {
        font-size: 32px;
        color: #ffffff;
        transition: color 0.3s ease;
    }

    .fa-x-twitter:hover {
        color: #03a088;
    }
    </style>
""", unsafe_allow_html=True) 

# Update the sidebar CSS in your styles
st.markdown("""
    <style>
    /* Sidebar width adjustment */
    [data-testid="stSidebar"] {
        width: 420px !important;  /* Default is usually 400px */
    }
    
    /* Adjust collapsed state width if needed */
    [data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: -420px !important;
    }
    
    /* Sidebar styling (keeping existing styles) */
    section[data-testid="stSidebar"] {
        background: #202020;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem 1rem;
    }
    
    .sidebar .sidebar-content {
        background: transparent;
    }
    </style>
""", unsafe_allow_html=True) 

# Add this CSS before the metrics
st.markdown("""
    <style>
    /* Regular metrics styling */
    div[data-testid="stMetricValue"] > div {
        font-size: 22px !important;
        line-height: 1.2 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    </style>
""", unsafe_allow_html=True) 

# Add this CSS for login form styling
st.markdown("""
    <style>
    /* Form container styling */
    [data-testid="stForm"] {
        max-width: 300px !important;
        margin: 0 auto !important;
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    
    /* Form inputs container */
    [data-testid="stForm"] .stTextInput > div {
        width: 300px !important;
        position: relative !important;  /* For absolute positioning of button */
    }
    
    /* Input fields */
    [data-testid="stForm"] input[type="text"],
    [data-testid="stForm"] input[type="password"] {
        width: 100% !important;
        padding-right: 40px !important;  /* Space for the toggle button */
    }
    
    /* Password toggle button */
    [data-testid="stForm"] button[aria-label="Toggle password visibility"] {
        position: absolute !important;
        right: 8px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 1 !important;
        background: transparent !important;
        border: none !important;
        cursor: pointer !important;
        padding: 4px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: 32px !important;
        height: 32px !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    /* Password toggle button icon */
    [data-testid="stForm"] button[aria-label="Toggle password visibility"] svg {
        width: 20px !important;
        height: 20px !important;
        opacity: 0.7 !important;
    }
    
    /* Form button styling */
    [data-testid="stForm"] .stButton > button {
        width: 300px !important;
        color: #ffffff !important;
        border-color: #03a088 !important;
        background-color: #03a088 !important;
    }
    
    /* Form elements container */
    [data-testid="stForm"] > div {
        width: 300px !important;
        margin: 0 auto !important;
    }
    
    /* Remove any hidden overflow */
    [data-testid="stForm"] .stTextInput {
        width: 100% !important;
        overflow: visible !important;
    }
    
    /* Ensure button container is visible */
    [data-testid="stForm"] .stTextInput > div > div {
        overflow: visible !important;
    }
    </style>
""", unsafe_allow_html=True)

# Add this CSS to force hide the sidebar and its toggle button
st.markdown("""
    <style>
    /* Hide sidebar */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Hide sidebar toggle button */
    button[kind="header"] {
        display: none !important;
    }
    
    /* Adjust main content to take full width */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 5% !important;
        padding-right: 5% !important;
        padding-top: 1rem !important;
    }
    
    /* Hide any remaining sidebar elements */
    .st-emotion-cache-16idsys {
        display: none !important;
    }
    
    /* Remove sidebar transition effects */
    @media (width: 0) {
        section[data-testid="stSidebar"] {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            visibility: hidden !important;
            transform: none !important;
            transition: none !important;
        }
    }
    </style>
""", unsafe_allow_html=True) 

st.markdown("""
    <style>
    /* Info box styling */
    .stAlert {
        max-width: 600px !important;  /* Reduced from 800px */
        margin: 2rem auto !important;
        background-color: #202020 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 5px !important;
    }
    
    /* Style for info icon */
    .stAlert [data-testid="stInfoBadge"] {
        background-color: transparent !important;
        color: #03a088 !important;
    }
    
    /* Style for info text */
    .stAlert > div {
        color: #ffffff !important;
    }
    
    /* Style for Twitter link */
    .stAlert a {
        color: inherit;
        text-decoration: none;
    }

    .stAlert a:hover {
        color: #03a088 !important;
    }
    </style>
""", unsafe_allow_html=True) 

st.markdown("""
    <style>
    /* Target the password toggle icon and its SVG specifically */
    [data-testid="stForm"] button[aria-label="Toggle password visibility"],
    [data-testid="stForm"] button[aria-label="Toggle password visibility"] svg,
    [data-testid="stForm"] button[aria-label="Toggle password visibility"] path {
        background: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.5) !important;
        fill: rgba(255, 255, 255, 0.5) !important;
        stroke: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Hover states */
    [data-testid="stForm"] button[aria-label="Toggle password visibility"]:hover,
    [data-testid="stForm"] button[aria-label="Toggle password visibility"]:hover svg,
    [data-testid="stForm"] button[aria-label="Toggle password visibility"]:hover path {
        background: transparent !important;
        color: rgba(255, 255, 255, 0.8) !important;
        fill: rgba(255, 255, 255, 0.8) !important;
        stroke: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Remove any button styling */
    [data-testid="stForm"] button[aria-label="Toggle password visibility"] {
        border: none !important;
        box-shadow: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
""", unsafe_allow_html=True) 

# Add this CSS before any other CSS blocks
st.markdown("""
    <style>
    /* Import Raleway font */
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700&display=swap');
    
    /* Apply Raleway to all elements */
    * {
        font-family: 'Raleway', sans-serif !important;
    }
    
    /* Specific element overrides */
    .stMarkdown,
    .stButton > button,
    .stSelectbox,
    .stMultiSelect,
    .stTextInput > div,
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricLabel"],
    .dataframe,
    .category-header,
    .category-header-tab3,
    h1, h2, h3, h4, h5, h6,
    p,
    .stTabs [data-baseweb="tab"],
    .stAlert > div,
    [data-testid="stForm"] input {
        font-family: 'Raleway', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

# Add custom CSS for alignment and dropdown width
st.markdown("""
    <style>
    .metric-label {
        margin-top: 12px;
        color: #ffffff;
        text-align: right;
        padding-right: 15px;
        font-size: 14px;
    }
    
    /* Force wider select box */
    [data-testid="stSelectbox"] {
        width: 100% !important;  /* Increased fixed width */
    }
    
    /* Override all nested select elements */
    [data-testid="stSelectbox"] > div,
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stSelectbox"] div[data-baseweb="select"],
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stSelectbox"] div[data-baseweb="select"] span,
    [data-testid="stSelectbox"] div[role="combobox"] {
        min-width: 300px !important;
        max-width: 100% !important;
    }
    
    /* Prevent text truncation */
    [data-testid="stSelectbox"] span {
        max-width: none !important;
        white-space: normal !important;
        text-overflow: unset !important;
        overflow: visible !important;
    }
    </style>
""", unsafe_allow_html=True)

# Add custom CSS specifically for the price metric selector
st.markdown("""
    <style>
    /* Target the select container and all its children */
    [data-testid="stSelectbox"]:has(select#price_metric_selector),
    [data-testid="stSelectbox"]:has(select#price_metric_selector) *,
    div:has(> select#price_metric_selector),
    div:has(> select#price_metric_selector) * {
        font-size: 10px !important;
    }

    /* Target the actual select element */
    select#price_metric_selector {
        font-size: 10px !important;
    }

    /* Target the dropdown options */
    select#price_metric_selector option {
        font-size: 10px !important;
    }

    /* Additional specificity for BaseWeb components */
    [data-baseweb="select"]:has(input[id*="price_metric_selector"]),
    [data-baseweb="select"]:has(input[id*="price_metric_selector"]) * {
        font-size: 10px !important;
    }

    /* Target the popover/dropdown menu */
    [data-baseweb="popover"],
    [data-baseweb="popover"] * {
        font-size: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Add this CSS block after your existing multiselect styling
st.markdown("""
    <style>
    /* Style for selected tags in multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #03a088 !important;
        border-radius: 4px;
        margin: 2px;
        font-size: 12px !important;  /* Set font size for selected items */
    }
    
    /* Style for the text inside tags */
    .stMultiSelect [data-baseweb="tag"] span {
        font-size: 12px !important;
    }
    
    /* Style for the remove (x) button in tags */
    .stMultiSelect [data-baseweb="tag"] button {
        font-size: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Add this CSS to prevent text truncation in the selectbox
st.markdown("""
    <style>
    /* Prevent text truncation in selectbox */
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div > div {
        width: auto !important;
        min-width: 100% !important;
        font-size: 14px !important;  /* Set font size for label */
    }
    
    [data-testid="stSelectbox"] div[data-baseweb="select"] span,
    [data-testid="stSelectbox"] div[data-baseweb="select"] div[aria-selected="true"] {
        width: auto !important;
        max-width: none !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        font-size: 14px !important;  /* Set font size for selected value */
    }
    
    /* Ensure the container and all nested elements use available space */
    [data-testid="stSelectbox"] > div,
    [data-testid="stSelectbox"] [data-baseweb="select"],
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        width: 100% !important;
        position: relative !important;
    }
    
    /* Target the label specifically */
    [data-testid="stSelectbox"] [data-baseweb="select"] [role="option"] {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        font-size: 14px !important;  /* Set font size for dropdown options */
    }

    /* Keep the default arrow styling */
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        padding-right: 24px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Create columns with specific widths
label_col, dropdown_col = st.columns([0.8, 1])

# Add or update this CSS
st.markdown("""
    <style>
    /* Headers */
    h3 {
        font-size: 24px;
        font-weight: 600;
        color: #03a088;
        margin-bottom: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Add or update the tabs styling CSS
st.markdown("""
    <style>
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: #202020;
        padding: 6px;
        border-radius: 3px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 3px;
        padding: 12px 24px;
        font-weight: 500;
        background: transparent;
        color: #ffffff;
        border-bottom: none !important;
        transition: all 0.3s ease;  /* Smooth transition for hover effects */
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #00a195;
        text-shadow: 0 0 15px rgba(0, 161, 149, 0.8);  /* Changed to teal color */
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #202020;
        color: #03a088;
        box-shadow: none;
    }
    </style>
""", unsafe_allow_html=True)

# Add this CSS to your existing styles
st.markdown("""
    <style>
    /* Fix for selectbox text truncation */
    .stSelectbox div[data-baseweb="select"] > div {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        width: auto !important;
        max-width: none !important;
    }
    
    /* Style for the dropdown options */
    div[role="listbox"] div {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        width: auto !important;
        max-width: none !important;
    }
    
    /* Ensure dropdown container is wide enough */
    .stSelectbox div[data-baseweb="popover"] {
        min-width: 300px !important;  /* Adjust this value as needed */
    }
    
    /* Ensure the select container itself is wide enough */
    .stSelectbox {
        width: 100% !important;
        max-width: 600px !important;  /* Adjust this value as needed */
    }
            

    div[data-baseweb="select"] {
        width: 100% !important;  /* Subtract padding if needed */
        max-width: 100% !important;
    }
            
    div[data-baseweb="select"] .stSelectbox {
        white-space: normal !important; /* Allow multi-line wrapping */
        word-wrap: break-word !important;
    }

    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Target specifically the selectbox with key="tab4_select" */
    [data-testid="stSelectbox"] div[data-key="tab4_select"]
        width: 800px !important;
        min-width: 800px !important;
        max-width: none !important;
        background-color: #202020 !important;
    }
    
    /* Make dropdown menu match width and background */
    div[data-key="tab4_select"] ~ [data-baseweb="popover"] {
        min-width: 800px !important;
        width: 800px !important;
        background-color: #202020 !important;
    }

    /* Style the dropdown options */
    div[data-key="tab4_select"] ~ [data-baseweb="popover"] [role="option"] {
        background-color: #202020 !important;
        color: #ffffff !important;
    }

    /* Hover state for options */
    div[data-key="tab4_select"] ~ [data-baseweb="popover"] [role="option"]:hover {
        background-color: #363636 !important;
    }
            
    .stMultiSelect [data-baseweb=select] span{
            max-width: 300px !important;
            font-size: 12px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Alternative selector if the above doesn't work */
    [data-testid="stSelectbox"] > label {
        margin-bottom: -30px !important;
        padding-bottom: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

def format_table_html(df, display_columns):
    html = f"""
    <div class="table-container">
        <table class="custom-table">
            <thead>
                <tr>
                    {''.join(f'<th>{col}</th>' for col in display_columns)}
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in df.iterrows():
        html += "<tr>"
        for i, val in enumerate(row):
            # Add title attribute for tooltip on hover
            title_attr = f'title="{val}"' if i in [1, 2] else ''  # For Card Name and Set columns
            html += f'<td {title_attr}>{val}</td>'
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    """
    return html
