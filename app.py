import streamlit as st
import pandas as pd

# 1. SETUP & CONFIG
st.set_page_config(page_title="App Duplicate Tracker", layout="wide")

# IMPORTANT: Ensure this is the RAW link (Right-click "Raw" button on GitHub -> Copy Link Address)
# It should start with 'https://raw.githubusercontent.com/...'
GITHUB_CSV_URL = "https://raw.githubusercontent.com/YourUsername/YourRepo/main/YourFile.csv"

# 2. LOAD DATA (With Caching for Large Files)
@st.cache_data(show_spinner="Downloading large dataset from GitHub...")
def load_data(url):
    try:
        # low_memory=False handles large files better
        # on_bad_lines='skip' prevents crashes if a row is corrupted
        return pd.read_csv(url, low_memory=False, on_bad_lines='skip')
    except Exception as e:
        st.error(f"❌ Error loading CSV: {e}")
        return None

df = load_data(GITHUB_CSV_URL)

# 3. APP LOGIC
if df is not None:
    st.title("📋 Application Duplicate Checker")
    
    # --- DYNAMIC COLUMN SELECTION ---
    # This prevents errors if your CSV headers change slightly
    st.sidebar.header("Column Settings")
    all_columns = df.columns.tolist()
    
    id_col = st.sidebar.selectbox("Select ID Column (Application Number):", all_columns, 
                                 index=0 if "Application Number" not in all_columns else all_columns.index("Application Number"))
    
    type_col = st.sidebar.selectbox("Select Category Column (Application Type):", all_columns, 
                                   index=1 if "Application Type" not in all_columns else all_columns.index("Application Type"))

    # --- TOP LEVEL METRICS ---
    total_apps = len(df)
    total_unique = df[id_col].nunique()
    total_dupes = total_apps - total_unique

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Rows", f"{total_apps:,}")
    m2.metric("Unique Applications", f"{total_unique:,}")
    m3.metric("Duplicates Found", f"{total_dupes:,}", delta_color="inverse")

    st.divider()

    # --- CATEGORY BREAKDOWN ---
    st.subheader("📊 Breakdown by Type")
    
    # Grouping logic
    stats = df.groupby(type_col)[id_col].agg(['count', 'nunique']).reset_index()
    stats['duplicates'] = stats['count'] - stats['nunique']
    stats.columns = ["Application Type", "Total Count", "Unique Count", "Duplicate Count"]
    
    # Show the table
    st.dataframe(stats.sort_values(by="Duplicate Count", ascending=False), use_container_width=True)

    # --- DRILL DOWN: SEE THE NUMBERS ---
    st.divider()
    st.subheader("🔍 Inspection Tool")
    
    show_only_dupes = st.checkbox("Show ONLY rows that are duplicates", value=True)
    
    selected_type = st.selectbox("Filter by Type:", ["All"] + list(stats["Application Type"].unique()))

    # Filter logic
    display_df = df.copy()
    if selected_type != "All":
        display_df = display_df[display_df[type_col] == selected_type]
    
    if show_only_dupes:
        # Finds all instances of IDs that appear more than once
        display_df = display_df[display_df.duplicated(subset=[id_col], keep=False)]

    st.write(f"Showing **{len(display_df):,}** entries:")
    st.dataframe(display_df.sort_values(by=id_col), use_container_width=True)

else:
    st.warning("⚠️ Waiting for data... Please check your GitHub URL in the code.")

