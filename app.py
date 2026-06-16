import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Shelter Feeding Tracker",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Advanced CSS Styling (DARK THEME WITH IMAGE BACKGROUND)
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    /* Global Typography */
    html, body, [class*="css"]  {
        font-family: 'Nunito', sans-serif;
    }
    
    /* THE MAIN BACKROUND IMAGE STYLING */
    .stApp {
        background-color: #0d1117; /* Dark fallback color */
        /* --- REPLACE THE URL BELOW WITH YOUR DIRECT ANIMAL IMAGE URL --- */
        background-image: url('https://images.unsplash.com/photo-1548199973-03cce0bbc87b?q=80&w=2669&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); 
        /* --- Sourcing a subtle, high-res image (e.g., from Unsplash) works best --- */
        background-repeat: no-repeat;
        background-size: cover; /* Scale image to cover whole screen */
        background-position: center; /* Center the image */
    }

    /* Main Header Styling (Keeping bright white) */
    .main-header {
        text-align: center;
        color: #F8F9F9;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0px;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8); /* Stronger shadow over image */
    }
    .sub-header {
        text-align: center;
        color: #BDC3C7;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 40px;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.6);
    }

    /* Metric Cards (Dark Glassmorphism) */
    div[data-testid="metric-container"] {
        background: rgba(0, 0, 0, 0.6); /* Slightly darker cards for contrast against image */
        backdrop-filter: blur(8px); /* Less blur so image shows subtly */
        border: 1px solid rgba(255, 255, 255, 0.1); 
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.8);
    }
    
    /* Metric Text Colors (Keeping bright silver/neon green) */
    div[data-testid="metric-container"] label {
        color: #BDC3C7 !important;
        font-weight: 600;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #2ECC71 !important; 
    }

    /* Markdown text color override (Ensuring bright white/silver is default) */
    h3, p, label {
        color: #F8F9F9 !important; 
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    
    /* Selectbox Styling for Dark Mode visibility */
    div[data-testid="stSelectbox"] label {
        color: #F8F9F9 !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #F8F9F9 !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }
    
    /* DataFrame Customization */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.7);
        background: rgba(0,0,0,0.5); /* Slightly darker table background */
    }
    /* Style table header text for visibility against darker background */
    [data-testid="stDataFrame"] table thead tr th {
        color: #E0E0E0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. App Headers
st.markdown("<h1 class='main-header'>🐾 Animal Shelter Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Daily monitoring of nutritional intake and excess</p>", unsafe_allow_html=True)

# 4. Load Data Function
@st.cache_data(ttl=60)
def load_data(sheet_url):
    try:
        df = pd.read_csv(sheet_url)
        df.columns = ['Timestamp', 'Date', 'Cage Name', 'Animal Name', 'Fed By', 'Amount Fed', 'Excess Food']
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    except Exception as e:
        st.error("Cannot connect to Google Sheets. Please check the URL and ensure it is published to the web.")
        return pd.DataFrame()

# --- MAKE SURE TO PASTE YOUR CSV URL HERE AGAIN ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2lKl_VmCMxoITX40Gtfu5y90Xd2a-eWouVm4f0S4udVRDeK-4jk_QhEUzQR61zFew3Ee5gwM9UJw5/pub?gid=98942158&single=true&output=csv" 

df = load_data(SHEET_URL)

if not df.empty:
    st.write("<br>", unsafe_allow_html=True) 
    
    # 5. Dashboard Controls 
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### 📅 Select Filter")
        unique_dates = sorted(df['Date'].dropna().unique(), reverse=True)
        # Explicitly make date selection bright for dark mode
        selected_date = st.selectbox("Choose a Date:", unique_dates, help="Select a date to filter feeding records.")
    
    filtered_df = df[df['Date'] == selected_date]
    
    # 6. Calculate Metrics
    total_fed = pd.to_numeric(filtered_df['Amount Fed'], errors='coerce').sum()
    total_excess = pd.to_numeric(filtered_df['Excess Food'], errors='coerce').sum()
    
    with col2:
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Total Records", value=len(filtered_df))
        m2.metric(label="Total Food Fed", value=f"{total_fed:.2f} kg") 
        m3.metric(label="Total Excess", value=f"{total_excess:.2f} kg")

    st.divider()
    st.markdown("### 📋 Detailed Feeding Log")
    
    # 7. Display Data
    st.dataframe(
        filtered_df[['Cage Name', 'Animal Name', 'Fed By', 'Amount Fed', 'Excess Food']],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Awaiting data... Please submit a response through the Google Form.")
