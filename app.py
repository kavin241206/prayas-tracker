import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Prayas Animal Tracker",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Advanced CSS Styling (Dark Theme Glassmorphism)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');
    html, body, [class*="css"]  { font-family: 'Nunito', sans-serif; }
    .stApp {
        background-color: #0d1117; 
        background-image: url('https://images.unsplash.com/photo-1548199973-03cce0bbc87b?q=80&w=2669&auto=format&fit=crop'); 
        background-repeat: no-repeat; background-size: cover; background-position: center; 
    }
    .main-header { text-align: center; color: #F8F9F9; font-weight: 800; font-size: 3rem; margin-bottom: 0px; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }
    .sub-header { text-align: center; color: #BDC3C7; font-size: 1.2rem; font-weight: 600; margin-bottom: 40px; text-shadow: 1px 1px 5px rgba(0,0,0,0.6); }
    div[data-testid="metric-container"] {
        background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.1); 
        padding: 20px; border-radius: 15px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }
    div[data-testid="metric-container"] label { color: #BDC3C7 !important; font-weight: 600; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #2ECC71 !important; }
    h3, p, label, h4 { color: #F8F9F9 !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.5); }
    div[data-testid="stSelectbox"] label { color: #F8F9F9 !important; }
    div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.1) !important; color: #F8F9F9 !important; border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 8px;
    }
    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.7); background: rgba(0,0,0,0.5); }
    [data-testid="stDataFrame"] table thead tr th { color: #E0E0E0 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🐾 Prayas Animal Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Daily monitoring of nutritional intake and excess</p>", unsafe_allow_html=True)

# 4. Smart Multi-Data Pipeline Merger
@st.cache_data(ttl=30)
def load_and_merge_data(feed_url, excess_url):
    try:
        # Load Form 1 (Feeding Log)
        df_feed = pd.read_csv(feed_url)
        rename_feed = {}
        for col in df_feed.columns:
            c_low = col.lower()
            if 'date' in c_low: rename_feed[col] = 'Date'
            elif 'type' in c_low or 'species' in c_low: rename_feed[col] = 'Animal Type'
            elif 'cage' in c_low: rename_feed[col] = 'Cage Name'
            elif 'id' in c_low: rename_feed[col] = 'Animal ID'
            elif 'food' in c_low or 'feed' in c_low or 'diet' in c_low or 'item' in c_low: rename_feed[col] = 'Food Type'
            elif 'amount' in c_low or 'given' in c_low: rename_feed[col] = 'Amount Given'
            elif 'fed by' in c_low or 'person' in c_low: rename_feed[col] = 'Fed By'
        df_feed = df_feed.rename(columns=rename_feed)
        
        # Safeguards for columns
        if 'Food Type' not in df_feed.columns: df_feed['Food Type'] = 'General Feed'
        if 'Animal ID' not in df_feed.columns: df_feed['Animal ID'] = 'N/A'
        if 'Amount Given' not in df_feed.columns: df_feed['Amount Given'] = 0
        if 'Animal Type' not in df_feed.columns: df_feed['Animal Type'] = 'Dog'
        if 'Cage Name' not in df_feed.columns: df_feed['Cage Name'] = 'General'
        if 'Fed By' not in df_feed.columns: df_feed['Fed By'] = 'Staff'

        df_feed['Amount Given'] = pd.to_numeric(df_feed['Amount Given'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        df_feed['Date'] = pd.to_datetime(df_feed['Date'], errors='coerce').dt.date
        df_feed['Animal ID'] = df_feed['Animal ID'].astype(str).str.strip()
        df_feed['Food Type'] = df_feed['Food Type'].astype(str).str.strip().str.title()

        # Load Form 2 (Excess Log)
        df_excess = pd.read_csv(excess_url)
        rename_ex = {}
        for col in df_excess.columns:
            c_low = col.lower()
            if 'date' in c_low: rename_ex[col] = 'Date'
            elif 'id' in c_low: rename_ex[col] = 'Animal ID'
            elif 'food' in c_low or 'feed' in c_low or 'diet' in c_low or 'item' in c_low: rename_ex[col] = 'Food Type'
            elif 'leftover' in c_low or 'excess' in c_low: rename_ex[col] = 'Excess Food'
        df_excess = df_excess.rename(columns=rename_ex)
        
        if 'Food Type' not in df_excess.columns: df_excess['Food Type'] = 'General Feed'
        if 'Animal ID' not in df_excess.columns: df_excess['Animal ID'] = 'N/A'
        if 'Excess Food' not in df_excess.columns: df_excess['Excess Food'] = 0

        df_excess['Excess Food'] = pd.to_numeric(df_excess['Excess Food'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        df_excess['Date'] = pd.to_datetime(df_excess['Date'], errors='coerce').dt.date
        df_excess['Animal ID'] = df_excess['Animal ID'].astype(str).str.strip()
        df_excess['Food Type'] = df_excess['Food Type'].astype(str).str.strip().str.title()

        # Group leftover logs to handle single matching keys cleanly
        df_excess_grouped = df_excess.groupby(['Date', 'Animal ID', 'Food Type'], as_index=False)['Excess Food'].sum()

        # Safe Left Merge matching operations
        merged_df = pd.merge(df_feed, df_excess_grouped, on=['Date', 'Animal ID', 'Food Type'], how='left')
        merged_df['Excess Food'] = merged_df['Excess Food'].fillna(0)
        merged_df['Net Consumed'] = merged_df['Amount Given'] - merged_df['Excess Food']
        
        return merged_df
    except Exception as e:
        st.error(f"Pipeline Execution Mismatch: {e}")
        return pd.DataFrame()

# --- PASTE YOUR LINKS HERE ---
FEEDING_FORM_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTEUNzMPPuzvwxGl6DZuHSOrdkpyi9JWWzj3cywT3V4zDqxEvRGdhmItuboqFkHLN1l1f39uSGTQMeP/pub?gid=1774010924&single=true&output=csv"
EXCESS_FORM_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTEUNzMPPuzvwxGl6DZuHSOrdkpyi9JWWzj3cywT3V4zDqxEvRGdhmItuboqFkHLN1l1f39uSGTQMeP/pub?gid=556161144&single=true&output=csv"

df = load_and_merge_data(FEEDING_FORM_CSV, EXCESS_FORM_CSV)

if not df.empty:
    st.write("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### 🎛️ Filters")
        unique_dates = sorted(df['Date'].dropna().unique(), reverse=True)
        selected_date = st.selectbox("📅 Date:", ["All Dates"] + list(unique_dates))
        
        # Segregation values list for your 24 items
        animal_list = ["Dog", "Cat", "Monkey", "Cow", "Goat", "Buffalo", "Rabbit", "Iguanas", "Turkey", "Duck", "Kannur", "Pigeon", "Peahon", "Alex Parrot", "Rose Parrot", "African Love Birds", "Buggies Birds", "African Greys", "Cockatiel Birds", "Guinea Pigs", "Hen", "Red Ear Slider", "Star Tortoise", "Snake"]
        selected_animal = st.selectbox("🐾 Animal Type:", ["All Animals"] + sorted(animal_list))
        
        if st.button("🔄 Force Synchronize Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Filtering Operations
    filtered_df = df.copy()
    if selected_date != "All Dates":
        filtered_df = filtered_df[filtered_df['Date'] == selected_date]
    if selected_animal != "All Animals":
        filtered_df = filtered_df[filtered_df['Animal Type'].str.contains(selected_animal, case=False, na=False)]

    # Metrics Layout Engine (Grams)
    total_fed = filtered_df['Amount Given'].sum()
    total_excess = filtered_df['Excess Food'].sum()
    total_net = filtered_df['Net Consumed'].sum()

    with col2:
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Total Food Served", value=f"{total_fed:,.1f} g")
        m2.metric(label="Total Leftovers / Excess", value=f"{total_excess:,.1f} g")
        m3.metric(label="Net Eaten by Animals", value=f"{total_net:,.1f} g")

    st.divider()
    st.markdown("### 📋 Unified Operational Registry Log")
    
    # CRITICAL FIX: Convert table content explicitly to text strings to completely bypass PyArrow serialization crashes
    display_df = filtered_df[['Date', 'Animal Type', 'Cage Name', 'Animal ID', 'Food Type', 'Amount Given', 'Excess Food', 'Net Consumed', 'Fed By']].copy()
    
    display_df['Date'] = display_df['Date'].astype(str)
    display_df['Amount Given'] = display_df['Amount Given'].map(lambda x: f"{x:,.1f} g")
    display_df['Excess Food'] = display_df['Excess Food'].map(lambda x: f"{x:,.1f} g")
    display_df['Net Consumed'] = display_df['Net Consumed'].map(lambda x: f"{x:,.1f} g")
    
    for col in ['Animal Type', 'Cage Name', 'Animal ID', 'Food Type', 'Fed By']:
        display_df[col] = display_df[col].astype(str)

    # Render Clean Table
    st.dataframe(
        display_df,
        use_container_width=True, 
        hide_index=True
    )
else:
    st.info("Awaiting initial system synchronization data stream...")
