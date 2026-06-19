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
st.markdown("<p class='sub-header'>Operational Data Merging & Cost Verification Platform</p>", unsafe_allow_html=True)

# 4. Smart Multi-Data Pipeline Merger (Reinforced against KeyErrors)
@st.cache_data(ttl=30)
def load_and_merge_data(feed_url, excess_url):
    try:
        # Load Form 1 (Feeding)
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
        
        # Guard rails to inject default structures if mapping failed
        if 'Food Type' not in df_feed.columns: df_feed['Food Type'] = 'General Feed'
        if 'Animal ID' not in df_feed.columns: df_feed['Animal ID'] = 'N/A'
        if 'Amount Given' not in df_feed.columns: df_feed['Amount Given'] = 0
        if 'Animal Type' not in df_feed.columns: df_feed['Animal Type'] = 'Dog'
        if 'Cage Name' not in df_feed.columns: df_feed['Cage Name'] = 'General'
        if 'Fed By' not in df_feed.columns: df_feed['Fed By'] = 'Staff'

        df_feed['Amount Given'] = pd.to_numeric(df_feed['Amount Given'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        df_feed['Date'] = pd.to_datetime(df_feed.get('Date', pd.Timestamp.now()), errors='coerce').dt.date
        df_feed['Animal ID'] = df_feed['Animal ID'].astype(str).str.strip()
        df_feed['Food Type'] = df_feed['Food Type'].astype(str).str.strip().str.title()

        # Load Form 2 (Excess)
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
        df_excess['Date'] = pd.to_datetime(df_excess.get('Date', pd.Timestamp.now()), errors='coerce').dt.date
        df_excess['Animal ID'] = df_excess['Animal ID'].astype(str).str.strip()
        df_excess['Food Type'] = df_excess['Food Type'].astype(str).str.strip().str.title()

        # Group duplicate cleanups
        df_excess_grouped = df_excess.groupby(['Date', 'Animal ID', 'Food Type'], as_index=False)['Excess Food'].sum()

        # Execute Merge safely
        merged_df = pd.merge(df_feed, df_excess_grouped, on=['Date', 'Animal ID', 'Food Type'], how='left')
        merged_df['Excess Food'] = merged_df['Excess Food'].fillna(0)
        merged_df['Net Consumed'] = merged_df['Amount Given'] - merged_df['Excess Food']
        
        return merged_df
    except Exception as e:
        st.error(f"Pipeline Execution Mismatch: {e}")
        return pd.DataFrame()

# --- PASTE BOTH LINKS HERE ---
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
        
        animal_list = ["Dog", "Cat", "Monkey", "Cow", "Goat", "Buffalo", "Rabbit", "Iguanas", "Turkey", "Duck", "Kannur", "Pigeon", "Peahon", "Alex Parrot", "Rose Parrot", "African Love Birds", "Buggies Birds", "African Greys", "Cockatiel Birds", "Guinea Pigs", "Hen", "Red Ear Slider", "Star Tortoise", "Snake"]
        selected_animal = st.selectbox("🐾 Animal Type:", ["All Animals"] + sorted(animal_list))
        
        if st.button("🔄 Force Synchronize Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Filtering Logic
    filtered_df = df.copy()
    if selected_date != "All Dates":
        filtered_df = filtered_df[filtered_df['Date'] == selected_date]
    if selected_animal != "All Animals":
        filtered_df = filtered_df[filtered_df['Animal Type'].str.contains(selected_animal, case=False, na=False)]

    # Dynamic Calculations
    total_fed = filtered_df['Amount Given'].sum()
    total_excess = filtered_df['Excess Food'].sum()
    total_net = filtered_df['Net Consumed'].sum()

    with col2:
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Total Food Served", value=f"{total_fed:,.1f} g")
        m2.metric(label="Total Leftovers / Excess", value=f"{total_excess:,.1f} g")
        m3.metric(label="Net Eaten by Animals", value=f"{total_net:,.1f} g")

    st.divider()
    
    # Financial Evaluation Matrix
    st.markdown("### 💰 Owner's Food Cost Evaluation Matrix")
    st.markdown("<p style='color: #BDC3C7;'>Type in the price per gram to compute immediate financial layout.</p>", unsafe_allow_html=True)
    
    unique_foods = df['Food Type'].dropna().unique()
    
    cost_dict = {}
    if len(unique_foods) > 0:
        cost_cols = st.columns(min(len(unique_foods), 4))
        for idx, food_name in enumerate(unique_foods):
            with cost_cols[idx % 4]:
                cost_dict[food_name] = st.number_input(f"Price/g for {food_name}:", min_value=0.0, value=0.0, step=0.01, format="%.4f")
    
    summary_df = filtered_df.groupby('Food Type').agg(
        Total_Given=('Amount Given', 'sum'),
        Total_Excess=('Excess Food', 'sum'),
        Net_Eaten=('Net Consumed', 'sum')
    ).reset_index()
    
    summary_df['Unit Cost'] = summary_df['Food Type'].map(cost_dict).fillna(0.0)
    summary_df['Total Valuation Cost'] = summary_df['Total_Given'] * summary_df['Unit Cost']
    summary_df['Wasted Cost Value'] = summary_df['Total_Excess'] * summary_df['Unit Cost']
    
    st.dataframe(
        summary_df.rename(columns={
            'Total_Given': 'Total Given (g)', 'Total_Excess': 'Total Excess (g)', 
            'Net_Eaten': 'Net Eaten (g)', 'Unit Cost': 'Rate / gram',
            'Total Valuation Cost': 'Total Cost Spent', 'Wasted Cost Value': 'Financial Waste Value'
        }),
        use_container_width=True, hide_index=True
    )

    st.divider()
    st.markdown("### 📋 Unified Operational Registry Log")
    st.dataframe(
        filtered_df[['Date', 'Animal Type', 'Cage Name', 'Animal ID', 'Food Type', 'Amount Given', 'Excess Food', 'Net Consumed', 'Fed By']],
        use_container_width=True, hide_index=True
    )
else:
    st.info("Awaiting initial system synchronization data stream...")
