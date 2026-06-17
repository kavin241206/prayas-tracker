import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Prayas Animal Tracker",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Advanced CSS Styling (DARK THEME WITH IMAGE BACKGROUND)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Nunito', sans-serif;
    }
    
    .stApp {
        background-color: #0d1117; 
        /* --- REPLACE THE URL BELOW WITH YOUR DIRECT ANIMAL IMAGE URL --- */
        background-image: url('https://images.unsplash.com/photo-1548199973-03cce0bbc87b?q=80&w=2669&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); 
        background-repeat: no-repeat;
        background-size: cover; 
        background-position: center; 
    }

    .main-header {
        text-align: center;
        color: #F8F9F9;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0px;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8); 
    }
    .sub-header {
        text-align: center;
        color: #BDC3C7;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 40px;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.6);
    }

    div[data-testid="metric-container"] {
        background: rgba(0, 0, 0, 0.6); 
        backdrop-filter: blur(8px); 
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
    
    div[data-testid="metric-container"] label {
        color: #BDC3C7 !important;
        font-weight: 600;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #2ECC71 !important; 
    }

    h3, p, label {
        color: #F8F9F9 !important; 
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    
    div[data-testid="stSelectbox"] label {
        color: #F8F9F9 !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #F8F9F9 !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }
    
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.7);
        background: rgba(0,0,0,0.5); 
    }
    [data-testid="stDataFrame"] table thead tr th {
        color: #E0E0E0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. App Headers (UPDATED WITH BRANDING)
st.markdown("<h1 class='main-header'>🐾 Prayas Animal Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Daily monitoring of nutritional intake and excess</p>", unsafe_allow_html=True)

# 4. Smart Load Data Function
@st.cache_data(ttl=60)
def load_data(sheet_url):
    try:
        df = pd.read_csv(sheet_url)
        
        rename_dict = {}
        for col in df.columns:
            lower_col = col.lower()
            if 'date' in lower_col: rename_dict[col] = 'Date'
            elif 'type' in lower_col or 'species' in lower_col: rename_dict[col] = 'Animal Type'
            elif 'cage' in lower_col: rename_dict[col] = 'Cage Name'
            elif 'id' in lower_col: rename_dict[col] = 'Animal ID'
            elif 'fed by' in lower_col or 'person' in lower_col: rename_dict[col] = 'Fed By'
            elif 'amount' in lower_col: rename_dict[col] = 'Amount Fed'
            elif 'excess' in lower_col: rename_dict[col] = 'Excess Food'
            
        df = df.rename(columns=rename_dict)
        
        # REMOVED: 'Animal Name' from expected columns tracking
        expected_cols = ['Date', 'Animal Type', 'Cage Name', 'Animal ID', 'Fed By', 'Amount Fed', 'Excess Food']
        for c in expected_cols:
            if c not in df.columns:
                df[c] = 'N/A'

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        return df
    except Exception as e:
        st.error(f"Cannot connect to Google Sheets. Error details: {e}")
        return pd.DataFrame()

# --- PASTE YOUR CSV URL HERE ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2lKl_VmCMxoITX40Gtfu5y90Xd2a-eWouVm4f0S4udVRDeK-4jk_QhEUzQR61zFew3Ee5gwM9UJw5/pub?gid=98942158&single=true&output=csv" 

df = load_data(SHEET_URL)

if not df.empty:
    st.write("<br>", unsafe_allow_html=True) 
    
    # 5. Dashboard Controls
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### 🎛️ Filters")
        
        # Date Filter
        unique_dates = sorted(df['Date'].dropna().unique(), reverse=True)
        selected_date = st.selectbox("📅 Date:", ["All Dates"] + list(unique_dates))
        
        # Animal Type Filter
        animal_list = [
            "Dog", "Cat", "Monkey", "Cow", "Goat", "Buffalo", "Rabbit", "Iguanas", 
            "Turkey", "Duck", "Kannur", "Pigeon", "Peahon", "Alex Parrot", "Rose Parrot", 
            "African Love Birds", "Buggies Birds", "African Greys", "Cockatiel Birds", 
            "Guinea Pigs", "Hen", "Red Ear Slider", "Star Tortoise", "Snake"
        ]
        selected_animal = st.selectbox("🐾 Animal Type:", ["All Animals"] + sorted(animal_list))
        
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🔄 Force Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Filtering logic
    filtered_df = df.copy()
    
    if selected_date != "All Dates":
        filtered_df = filtered_df[filtered_df['Date'] == selected_date]
        
    if selected_animal != "All Animals":
        filtered_df = filtered_df[filtered_df['Animal Type'].str.contains(selected_animal, case=False, na=False)]
    
    # 6. Calculate Metrics (Grams)
    clean_fed = filtered_df['Amount Fed'].astype(str).str.replace(r'[^\d.]', '', regex=True)
    total_fed = pd.to_numeric(clean_fed, errors='coerce').sum()
    
    clean_excess = filtered_df['Excess Food'].astype(str).str.replace(r'[^\d.]', '', regex=True)
    total_excess = pd.to_numeric(clean_excess, errors='coerce').sum()
    
    with col2:
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Total Records", value=len(filtered_df))
        m2.metric(label="Total Food Fed", value=f"{total_fed:,.2f} g") 
        m3.metric(label="Total Excess", value=f"{total_excess:,.2f} g")

    st.divider()
    st.markdown("### 📋 Detailed Feeding Log")
    
    # 7. Display Data (REMOVED: 'Animal Name' from display selection array)
    st.dataframe(
        filtered_df[['Date', 'Animal Type', 'Cage Name', 'Animal ID', 'Fed By', 'Amount Fed', 'Excess Food']],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Awaiting data... Please submit a response through the Google Form.")
