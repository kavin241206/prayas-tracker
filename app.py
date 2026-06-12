import streamlit as st
import pandas as pd
import datetime

# -----------------------------------------------------------------------------
# 1. SETUP & CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Prayas Live Feeding", page_icon="🐾", layout="centered")

st.title("🐾 Prayas Animal Shelter")
st.markdown("**Live Enclosure Feeding Tracker**")
st.info("Scan, check the daily limits, and help us feed the rescues!")

# -----------------------------------------------------------------------------
# 2. CONNECT TO GOOGLE SHEETS (Your Background Excel)
# -----------------------------------------------------------------------------
# PASTE YOUR PUBLISHED CSV LINKS HERE
INVENTORY_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRxLZLqr0_8_qb_hxJg9HjVjQX6LU4OaDESQN2dXqsonIzKnw-GuaVKQIfkvjjlVh4ZjxYst3U5j4Gi/pub?gid=0&single=true&output=csv"
LOGS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRxLZLqr0_8_qb_hxJg9HjVjQX6LU4OaDESQN2dXqsonIzKnw-GuaVKQIfkvjjlVh4ZjxYst3U5j4Gi/pub?gid=61294346&single=true&output=csv"

@st.cache_data(ttl=30) # Refreshes data every 30 seconds in the background
def load_data():
    try:
        df_inv = pd.read_csv(INVENTORY_CSV_URL)
        df_logs = pd.read_csv(LOGS_CSV_URL)
        return df_inv, df_logs
    except Exception as e:
        st.error("Error loading data. Please check the Google Sheets links.")
        return pd.DataFrame(), pd.DataFrame()

df_inventory, df_logs = load_data()
# --- DIAGNOSTIC TOOL ---
st.error("Here are the exact columns Python sees in your Inventory sheet:")
st.write(df_inventory.columns.tolist())
st.stop()
    # -----------------------
# -----------------------------------------------------------------------------
# 3. BACKGROUND LOGIC (Same as your Excel rules)
# -----------------------------------------------------------------------------
if not df_inventory.empty:
    # Calculate target for today
    df_inventory["Target_Kg"] = df_inventory["Animal_Count"] * df_inventory["Quota_Per_Animal"]
    
    # Filter logs for TODAY only
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    if not df_logs.empty and "Date" in df_logs.columns:
        # Ensure dates are strings for comparison
        df_logs["Date"] = df_logs["Date"].astype(str)
        logs_today = df_logs[df_logs["Date"] == today_str]
        
        # Sum food given today per cage
        fed_today = logs_today.groupby("Cage_Name")["Food_Given_Kg"].sum().reset_index()
    else:
        # If no logs exist yet today, create an empty framework
        fed_today = pd.DataFrame(columns=["Cage_Name", "Food_Given_Kg"])

    # Merge inventory with today's feeding data
    df_dashboard = pd.merge(df_inventory, fed_today, on="Cage_Name", how="left")
    df_dashboard["Food_Given_Kg"] = df_dashboard["Food_Given_Kg"].fillna(0.0)
    
    # Calculate remaining
    df_dashboard["Remaining_Kg"] = df_dashboard["Target_Kg"] - df_dashboard["Food_Given_Kg"]
    df_dashboard["Remaining_Kg"] = df_dashboard["Remaining_Kg"].apply(lambda x: max(0.0, x))

    # -----------------------------------------------------------------------------
    # 4. MOBILE INTERFACE (What the donor sees)
    # -----------------------------------------------------------------------------
    st.markdown("### Today's Status")
    
    # Create visual cards for each cage
    for _, row in df_dashboard.iterrows():
        cage = row["Cage_Name"]
        target = row["Target_Kg"]
        fed = row["Food_Given_Kg"]
        remaining = row["Remaining_Kg"]
        
        # Determine color status
        if remaining == 0:
            status_color = "🟢"
            status_text = "Fully Fed"
        elif fed > 0:
            status_color = "🟡"
            status_text = "Needs More"
        else:
            status_color = "🔴"
            status_text = "Empty - Needs Food!"
            
        # Display the data in a clean mobile card format
        with st.container():
            st.markdown(f"#### {status_color} {cage}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Daily Limit", f"{target:.1f} kg")
            col2.metric("Fed Today", f"{fed:.1f} kg")
            col3.metric("Remaining", f"{remaining:.1f} kg")
            st.divider()
else:
    st.warning("Awaiting data from Google Sheets...")
