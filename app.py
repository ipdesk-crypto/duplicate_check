import streamlit as st
import pandas as pd
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Application Duplicate Tracker", layout="wide")

# The file name you pushed via GitHub Desktop
FILENAME = "data.csv" 

st.title("📋 Application Duplicate Checker")

# --- 2. DATA LOADING LOGIC ---
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        data = pd.read_csv(file_path, low_memory=False)
        # CLEANING STEP: Remove hidden spaces from column headers to prevent KeyErrors
        data.columns = data.columns.str.strip()
        return data
    else:
        return None

df = load_data(FILENAME)

if df is not None:
    # --- 3. COLUMN DEFINITIONS ---
    # These must match your CSV exactly (now stripped of hidden spaces)
    ID_COL = "Application Number" 
    TYPE_COL = "Application Type(ID)"
    TITLE_COL = "Title"

    # Safety check: if the columns still aren't found, show the user what WAS found
    if TYPE_COL not in df.columns:
        st.error(f"Could not find column '{TYPE_COL}'")
        st.write("Columns found in your file:", list(df.columns))
        st.stop()

    # --- 4. DATA CLEANING ---
    # Ensure Type is a string, then remove rows where it's '0' or 'raw'
    df[TYPE_COL] = df[TYPE_COL].astype(str)
    # Filter to keep only the clean types you want
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

    # --- 6. BREAKDOWN BY TYPE (Table 1) ---
    st.subheader("📊 Statistics by Application Type (1-5)")

    stats = df.groupby(TYPE_COL)[ID_COL].agg(['count', 'nunique']).reset_index()
    stats['Duplicates'] = stats['count'] - stats['nunique']
    stats.columns = [TYPE_COL, "Total Apps", "Unique Apps", "Duplicate Apps"]

    # hide_index=True removes the 0, 1, 2, 3... numbers from the side
    st.dataframe(stats.sort_values(by=TYPE_COL), hide_index=True, use_container_width=True)

    # --- 7. DETAILED INSPECTION (Application Number and Title only) ---
    st.divider()
    st.subheader("🔍 Inspection: Duplicate Application Details")

    # Filter for duplicates (keep=False shows all copies of the duplicate)
    dupe_filter = df[df.duplicated(subset=[ID_COL], keep=False)]

    category_list = ["All Types"] + sorted(list(df[TYPE_COL].unique()))
    selected_cat = st.selectbox("Filter duplicates by Application Type:", category_list)

    if selected_cat != "All Types":
        display_df = dupe_filter[dupe_filter[TYPE_COL] == selected_cat]
    else:
        display_df = dupe_filter

    if not display_df.empty:
        st.write(f"Showing duplicate records:")
        
        # Strictly show only the Application Number and Title columns
        final_view = display_df[[ID_COL, TITLE_COL]].sort_values(by=ID_COL)
        
        # hide_index=True removes the confusing row numbers
        st.dataframe(final_view, hide_index=True, use_container_width=True)
    else:
        st.success("No duplicates found for this selection!")

else:
    st.error(f"❌ File not found: Could not find '{FILENAME}' in your repository.")
    st.info("Ensure you have pushed 'data.csv' via GitHub Desktop.")
