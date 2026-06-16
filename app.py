import streamlit as st
import pandas as pd

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="Shelter Feeding Tracker",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Custom CSS for an Elegant UI
st.markdown("""
    <style>
    /* Main background and font */
    .stApp {
        background-color: #FAFAFA;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    /* Stylish Header */
    .main-header {
        text-align: center;
        color: #2C3E50;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .sub-header {
        text-align: center;
        color: #7F8C8D;
        font-size: 1.2rem;
        margin-bottom: 40px;
    }
    /* Metric Cards Styling */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 3. App Headers
st.markdown("<h1 class='main-header'>🐾 Animal Shelter Feeding Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Daily monitoring of nutritional intake and waste.</p>", unsafe_allow_html=True)

# 4. Load Data Function
# @st.cache_data ensures the app doesn't redownload the sheet on every single click
@st.cache_data(ttl=60) # Refreshes data every 60 seconds
def load_data(sheet_url):
    try:
        # Read the CSV from Google Sheets
        df = pd.read_csv(sheet_url)
        # Rename columns to match your script logic (Change these to match your exact Google Form column headers)
        df.columns = ['Timestamp', 'Date', 'Cage Name', 'Animal Name', 'Fed By', 'Amount Fed', 'Excess Food']
        # Convert Date column to actual datetime objects for easy filtering
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# --- INSERT YOUR GOOGLE SHEETS CSV URL HERE ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2lKl_VmCMxoITX40Gtfu5y90Xd2a-eWouVm4f0S4udVRDeK-4jk_QhEUzQR61zFew3Ee5gwM9UJw5/pub?gid=98942158&single=true&output=csv" 

df = load_data(SHEET_URL)

if not df.empty:
    st.divider()
    
    # 5. Dashboard Controls (Filter by Date)
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Filter Records")
        # Create a dropdown of unique dates available in the data
        unique_dates = sorted(df['Date'].dropna().unique(), reverse=True)
        selected_date = st.selectbox("Select a Date:", unique_dates)
    
    # Filter the dataframe based on the selected date
    filtered_df = df[df['Date'] == selected_date]
    
    # 6. Calculate Metrics for the specific day
    total_fed = filtered_df['Amount Fed'].sum()
    total_excess = filtered_df['Excess Food'].sum()
    
    with col2:
        # Display key metrics in elegant cards
        m1, m2, m3 = st.columns(3)
        m1.metric(label=f"Records on {selected_date}", value=len(filtered_df))
        m2.metric(label="Total Food Fed", value=f"{total_fed:.2f} kg") # Adjust unit as needed
        m3.metric(label="Total Excess Food", value=f"{total_excess:.2f} kg")

    st.write("### 📋 Detailed Feeding Log")
    
    # Display the filtered dataframe cleanly, hiding the index
    st.dataframe(
        filtered_df[['Cage Name', 'Animal Name', 'Fed By', 'Amount Fed', 'Excess Food']],
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("No data found. Please ensure your Google Form has responses and the CSV link is correct.")
