import streamlit as st
import pandas as pd
import difflib

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

# 3. Dynamic Two-Form Pipeline Merger (CONCAT & SQUASH METHOD)
@st.cache_data(ttl=10)
def load_and_merge_data(feed_url, excess_url):
    try:
        # --- 1. LOAD & CLEAN FEEDING LOG ---
        df_feed = pd.read_csv(feed_url)
        rename_feed = {}
        for col in df_feed.columns:
            c_low = str(col).lower()
            if 'date' in c_low: rename_feed[col] = 'Date'
            elif 'amount' in c_low or 'given' in c_low: rename_feed[col] = 'Amount Given'
            elif 'food' in c_low or 'feed' in c_low or 'diet' in c_low or 'item' in c_low: rename_feed[col] = 'Food Type'
            elif 'type' in c_low or 'species' in c_low: rename_feed[col] = 'Animal Type'
            elif 'cage' in c_low: rename_feed[col] = 'Cage Name'
            elif 'id' in c_low: rename_feed[col] = 'Animal ID'
            elif 'fed by' in c_low or 'person' in c_low: rename_feed[col] = 'Fed By'
        df_feed = df_feed.rename(columns=rename_feed)
        df_feed = df_feed.loc[:, ~df_feed.columns.duplicated()]
        
        for c in ['Date', 'Animal Type', 'Cage Name', 'Animal ID', 'Food Type', 'Amount Given', 'Fed By']:
            if c not in df_feed.columns: df_feed[c] = ''

        df_feed['Amount Given'] = pd.to_numeric(df_feed['Amount Given'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        df_feed['Date'] = pd.to_datetime(df_feed['Date'], errors='coerce').dt.date.astype(str)
        df_feed['Excess Food'] = 0.0  

        # --- 2. LOAD & CLEAN EXCESS LOG ---
        df_excess = pd.read_csv(excess_url)
        rename_ex = {}
        for col in df_excess.columns:
            c_low = str(col).lower()
            if 'date' in c_low: rename_ex[col] = 'Date'
            elif 'id' in c_low: rename_ex[col] = 'Animal ID'
            elif 'type' in c_low or 'species' in c_low: rename_ex[col] = 'Animal Type' 
            elif 'food' in c_low or 'feed' in c_low or 'diet' in c_low or 'item' in c_low: rename_ex[col] = 'Food Type'
            elif 'leftover' in c_low or 'excess' in c_low or 'waste' in c_low: rename_ex[col] = 'Excess Food'
        df_excess = df_excess.rename(columns=rename_ex)
        df_excess = df_excess.loc[:, ~df_excess.columns.duplicated()]
        
        for c in ['Date', 'Animal ID', 'Animal Type', 'Food Type', 'Excess Food']:
            if c not in df_excess.columns: df_excess[c] = ''

        df_excess['Excess Food'] = pd.to_numeric(df_excess['Excess Food'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        df_excess['Date'] = pd.to_datetime(df_excess['Date'], errors='coerce').dt.date.astype(str)
        
        df_excess['Amount Given'] = 0.0
        df_excess['Cage Name'] = ''
        df_excess['Fed By'] = ''

        # --- 3. STANDARDIZE ALL TEXT (REMOVE "UNKNOWN") ---
        null_aliases = ['nan', 'none', 'n/a', '', '0', 'unknown']
        for df_temp in [df_feed, df_excess]:
            for col in ['Animal ID', 'Animal Type', 'Food Type', 'Cage Name', 'Fed By']:
                df_temp[col] = df_temp[col].astype(str).str.strip().str.title()
                df_temp[col] = df_temp[col].apply(lambda x: '' if str(x).lower() in null_aliases else x)

        # --- 4. AGGRESSIVE ALIGNMENT LOOP (Forces Excess rows to perfectly match Feed rows) ---
        for idx, ex_row in df_excess.iterrows():
            date = ex_row['Date']
            ex_id = str(ex_row['Animal ID'])
            ex_type = str(ex_row['Animal Type'])
            ex_food = str(ex_row['Food Type'])
            
            feed_matches = df_feed[df_feed['Date'] == date]
            
            if not feed_matches.empty:
                best_match_idx = None
                
                # Strategy A: Match by ID first
                if ex_id != '':
                    id_matches = feed_matches[feed_matches['Animal ID'] == ex_id]
                    if not id_matches.empty:
                        best_match_idx = id_matches.index[0]
                
                # Strategy B: If no ID, fuzzy match ALL text (fixes "Pedig" typed into Animal Type)
                if best_match_idx is None:
                    search_str = f"{ex_type} {ex_food}".strip()
                    feed_strs = feed_matches['Animal Type'] + " " + feed_matches['Food Type']
                    closest = difflib.get_close_matches(search_str, feed_strs.tolist(), n=1, cutoff=0.1)
                    
                    if closest:
                        best_match_idx = feed_matches[feed_strs == closest[0]].index[0]
                    else:
                        best_match_idx = feed_matches.index[0] # Fallback to prevent orphaned rows
                        
                # Overwrite the broken excess data with perfect feed data
                if best_match_idx is not None:
                    target = df_feed.loc[best_match_idx]
                    df_excess.at[idx, 'Animal Type'] = target['Animal Type']
                    df_excess.at[idx, 'Cage Name'] = target['Cage Name']
                    df_excess.at[idx, 'Animal ID'] = target['Animal ID']
                    df_excess.at[idx, 'Food Type'] = target['Food Type']
                    df_excess.at[idx, 'Fed By'] = target['Fed By']

        # --- 5. STACK AND SQUASH ---
        combined_df = pd.concat([df_feed, df_excess], ignore_index=True)
        
        final_df = combined_df.groupby(
            ['Date', 'Animal Type', 'Cage Name', 'Animal ID', 'Food Type', 'Fed By'], 
            dropna=False, # Allows grouping by empty strings
            as_index=False
        ).agg({
            'Amount Given': 'sum',
            'Excess Food': 'sum'
        })

        # --- 6. CALCULATE TRUE NET ---
        final_df['Net Consumed'] = final_df['Amount Given'] - final_df['Excess Food']
        
        return final_df
    except Exception as e:
        st.error(f"Pipeline Sync Mismatch: {e}")
        return pd.DataFrame()

# --- PASTE BOTH LINKS HERE ---
FEEDING_FORM_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSd6J0Vs0nD1sQ3VF0ksw-QFu8FbWS8uZG-UWpQOxZ5hJGhlpw-fQIPGTb-84utpl-r4QIXG5rKdUJb/pub?gid=771146835&single=true&output=csv"
EXCESS_FORM_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSd6J0Vs0nD1sQ3VF0ksw-QFu8FbWS8uZG-UWpQOxZ5hJGhlpw-fQIPGTb-84utpl-r4QIXG5rKdUJb/pub?gid=1231320326&single=true&output=csv"

df = load_and_merge_data(FEEDING_FORM_CSV, EXCESS_FORM_CSV)

if not df.empty:
    st.write("<br>", unsafe_allow_html=True)
    
    dt_series = pd.to_datetime(df['Date'], errors='coerce')
    df['Month_Sort'] = dt_series.dt.to_period('M')
    df['Month_Name'] = dt_series.dt.strftime('%B %Y').fillna('')
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### 🎛️ Filters")
        
        unique_periods = sorted(df['Month_Sort'].dropna().unique(), reverse=True)
        month_options = [p.strftime('%B %Y') for p in unique_periods]
        selected_month = st.selectbox("📅 Month:", ["All Months"] + month_options)
        
        if selected_month != "All Months":
            month_filtered_df = df[df['Month_Name'] == selected_month]
            unique_dates = sorted(month_filtered_df['Date'].dropna().unique(), reverse=True)
        else:
            unique_dates = sorted(df['Date'].dropna().unique(), reverse=True)
            
        selected_date = st.selectbox("📅 Date:", ["All Dates"] + list(unique_dates))
        
        animal_list = ["Dog", "Cat", "Monkey", "Cow", "Goat", "Buffalo", "Rabbit", "Iguanas", "Turkey", "Duck", "Kannur", "Pigeon", "Peahon", "Alex Parrot", "Rose Parrot", "African Love Birds", "Buggies Birds", "African Greys", "Cockatiel Birds", "Guinea Pigs", "Hen", "Red Ear Slider", "Star Tortoise", "Snake"]
        selected_animal = st.selectbox("🐾 Animal Type:", ["All Animals"] + sorted(animal_list))
        
        if st.button("🔄 Force Synchronize Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    filtered_df = df.copy()
    if selected_month != "All Months":
        filtered_df = filtered_df[filtered_df['Month_Name'] == selected_month]
    if selected_date != "All Dates":
        filtered_df = filtered_df[filtered_df['Date'] == selected_date]
    if selected_animal != "All Animals":
        filtered_df = filtered_df[filtered_df['Animal Type'].astype(str).str.contains(selected_animal, case=False, na=False)]

    total_fed = filtered_df['Amount Given'].sum()
    total_excess = filtered_df['Excess Food'].sum()
    total_net = filtered_df['Net Consumed'].sum()

    with col2:
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Total Food Served", value=f"{total_fed:,.1f} g")
        m2.metric(label="Total Leftovers / Excess", value=f"{total_excess:,.1f} g")
        m3.metric(label="Net Eaten by Animals", value=f"{total_net:,.1f} g")

    st.divider()
    
    st.markdown("### 🌾 Food Stock Consumption Summary")
    
    if not filtered_df.empty:
        summary_df = filtered_df.groupby('Food Type').agg({
            'Amount Given': 'sum',
            'Excess Food': 'sum',
            'Net Consumed': 'sum'
        }).reset_index()
        
        display_summary = pd.DataFrame()
        display_summary['Food Item Name'] = summary_df['Food Type'].astype(str)
        display_summary['Total Served'] = summary_df['Amount Given'].map(lambda x: f"{float(x):,.1f} g")
        display_summary['Total Excess / Leftover'] = summary_df['Excess Food'].map(lambda x: f"{float(x):,.1f} g")
        display_summary['Net Weight Consumed'] = summary_df['Net Consumed'].map(lambda x: f"{float(x):,.1f} g")
        
        st.dataframe(display_summary, use_container_width=True, hide_index=True)
    else:
        st.info("No matching food distribution items found for selected filter criteria.")

    st.divider()
    st.markdown("### 📋 Unified Operational Registry Log")
    
    display_df = pd.DataFrame()
    display_df['Date'] = filtered_df['Date'].astype(str)
    display_df['Animal Type'] = filtered_df['Animal Type'].astype(str)
    display_df['Cage Name'] = filtered_df['Cage Name'].astype(str)
    display_df['Animal ID'] = filtered_df['Animal ID'].astype(str)
    display_df['Food Type'] = filtered_df['Food Type'].astype(str)
    
    def format_val(val):
        try:
            return f"{float(val):,.1f} g"
        except:
            return "0.0 g"
            
    display_df['Amount Given'] = filtered_df['Amount Given'].map(format_val)
    display_df['Excess Food'] = filtered_df['Excess Food'].map(format_val)
    display_df['Net Consumed'] = filtered_df['Net Consumed'].map(format_val)
    display_df['Fed By'] = filtered_df['Fed By'].astype(str)

    display_df = display_df.sort_values(by=['Date', 'Animal Type'], ascending=[False, True])

    st.dataframe(
        display_df,
        use_container_width=True, 
        hide_index=True
    )
else:
    st.info("Awaiting initial system synchronization data stream...")
