import streamlit as st
import pandas as pd

# 1. Page Configuration (Must remain at the top)
st.set_page_config(
    page_title="Shelter Feeding Tracker",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Advanced CSS Styling
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    /* Global Typography and Background Gradient */
    html, body, [class*="css"]  {
        font-family: 'Nunito', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }

    /* Main Header Styling */
    .main-header {
        text-align: center;
        color: #2E4053;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    .sub-header {
        text-align: center;
        color: #5D6D7E;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 40px;
    }

    /* Metric Cards (Glassmorphism & Hover Effects) */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.15);
    }
    
    /* Metric Text Colors */
    div[data-testid="metric-container"] label {
        color: #7F8C8D !important;
        font-weight: 600;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #27AE60 !important; 
    }

    /* DataFrame Customization */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
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

# --- MAKE SURE YOUR CSV URL IS STILL PASTED HERE ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2lKl_VmCMxoITX40Gtfu5y90Xd2a-eWouVm4f0S4udVRDeK-4jk_QhEUzQR61zFew3Ee5gwM9UJw5/pub?gid=98942158&single=true&output=csv" 

df = load_data(SHEET_URL)

if not df.empty:
    st.write("<br>", unsafe_allow_html=True) # Adds a little breathing room
    
    # 5. Dashboard Controls 
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### 📅 Select Filter")
        unique_dates = sorted(df['Date'].dropna().unique(), reverse=True)
        selected_date = st.selectbox("Choose a Date:", unique_dates)
    
    filtered_df = df[df['Date'] == selected_date]
    
    # 6. Calculate Metrics
    # We use pd.to_numeric to prevent errors if someone types text instead of numbers in the form
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
