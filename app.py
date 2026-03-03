import streamlit as st
import pandas as pd
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Application Duplicate Tracker", layout="wide")

# This tells the app to look for the file you pushed via GitHub Desktop
# IMPORTANT: Ensure your file in GitHub is named exactly "data.csv"
FILENAME = "data.csv" 

st.title("📋 Application Duplicate Checker")

# --- 2. DATA LOADING LOGIC (Local Repo Method) ---
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path, low_memory=False)
    else:
        return None

df = load_data(FILENAME)

if df is not None:
    # --- 3. COLUMN DEFINITIONS ---
    ID_COL = "Application Number" 
    TYPE_COL = "Application Type(ID)"
    TITLE_COL = "Title"

    # --- 4. DATA CLEANING ---
    # Ensure Type is a string, then remove rows where it's '0' or 'raw'
    df[TYPE_COL] = df[TYPE_COL].astype(str)
    df = df[~df[TYPE_COL].str.lower().isin(['0', 'raw'])]

    # --- 5. TOP-LEVEL METRICS ---
    total_apps = len(df)
    unique_apps = df[ID_COL].nunique()
    duplicate_count = total_apps - unique_apps

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Applications", f"{total_apps:,}")
    col2.metric("Unique Applications", f"{unique_apps:,}")
    col3.metric("Duplicate Entries", f"{duplicate_count:,}")

    st.divider()

    # --- 6. BREAKDOWN BY TYPE (Statistics Table) ---
    st.subheader("📊 Statistics by Application Type (1-5)")

    stats = df.groupby(TYPE_COL)[ID_COL].agg(['count', 'nunique']).reset_index()
    stats['Duplicates'] = stats['count'] - stats['nunique']
    stats.columns = [TYPE_COL, "Total Apps", "Unique Apps", "Duplicate Apps"]

    # hide_index=True removes the 0, 1, 2, 3... numbers from the side
    st.dataframe(stats.sort_values(by=TYPE_COL), hide_index=True, use_container_width=True)

    # --- 7. DETAILED INSPECTION (Limited Columns) ---
    st.divider()
    st.subheader("🔍 Inspection: Duplicate Application Details")

    # Filter for all duplicates (shows every instance of a repeated ID)
    dupe_filter = df[df.duplicated(subset=[ID_COL], keep=False)]

    category_list = ["All Types"] + sorted(list(df[TYPE_COL].unique()))
    selected_cat = st.selectbox("Filter duplicates by Application Type:", category_list)

    if selected_cat != "All Types":
        display_df = dupe_filter[dupe_filter[TYPE_COL] == selected_cat]
    else:
        display_df = dupe_filter

    if not display_df.empty:
        st.write(f"Showing duplicate records (Application Number and Title only):")
        
        # Strictly show only the columns you requested
        final_view = display_df[[ID_COL, TITLE_COL]].sort_values(by=ID_COL)
        
        # hide_index=True keeps the view clean and professional
        st.dataframe(final_view, hide_index=True, use_container_width=True)
    else:
        st.success("No duplicates found for this selection!")

else:
    # This error shows only if the file isn't in your GitHub folder
    st.error(f"❌ File not found: Could not find '{FILENAME}' in your repository.")
    st.info("Ensure you have dragged 'data.csv' into your local folder and clicked 'Push' in GitHub Desktop.")
