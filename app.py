import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Shelter Feeding Tracker",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Advanced CSS Styling (DARK THEME)
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    /* Global Typography and Background Gradient */
    html, body, [class*="css"]  {
        font-family: 'Nunito', sans-serif;
    }
    
    /* The main dark background gradient */
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    }

    /* Main Header Styling */
    .main-header {
        text-align: center;
        color: #F8F9F9; /* Bright White */
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0px;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.6);
    }
    .sub-header {
        text-align: center;
        color: #BDC3C7; /* Light Silver */
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 40px;
    }

    /* Metric Cards (Dark Glassmorphism) */
    div[data-testid="metric-container"] {
        background: rgba(0, 0, 0, 0.4); /* Dark translucent background */
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.15); /* Faint white edge */
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6);
    }
    
    /* Metric Text Colors */
    div[data-testid="metric-container"] label {
        color: #BDC3C7 !important; /* Silver for the title */
        font-weight: 600;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #2ECC71 !important; /* Bright Neon Green for the numbers */
    }

    /* Markdown text color override (for subheaders like "Filter Records") */
    h3 {
        color: #E0E0E0 !important; 
    }
    p {
        color: #E0E0E0 !important;
    }
    
    /* DataFrame Customization */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
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
        selected_date = st.selectbox("Choose a Date:", unique_dates)
    
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
