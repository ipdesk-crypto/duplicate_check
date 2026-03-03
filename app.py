import streamlit as st
import pandas as pd
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Application Duplicate Tracker", layout="wide")

st.title("📋 Application Duplicate Checker")

# --- 2. DATA LOADING LOGIC ---
FILENAME = "data.csv" 

@st.cache_data
def process_data(file):
    return pd.read_csv(file, low_memory=False)

# Check if file exists in the GitHub repo
if os.path.exists(FILENAME):
    df = process_data(FILENAME)
else:
    st.warning(f"⚠️ `{FILENAME}` not found in GitHub. Please upload it manually.")
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
    if uploaded_file:
        df = process_data(uploaded_file)
    else:
        st.stop()

# --- 3. COLUMN DEFINITIONS ---
ID_COL = "Application Number" 
TYPE_COL = "Application Type(ID)"
TITLE_COL = "Title" # Assuming the column name is 'Title'

# Verification
if ID_COL not in df.columns or TYPE_COL not in df.columns:
    st.error(f"Column Name Error! Make sure columns are named '{ID_COL}' and '{TYPE_COL}'.")
    st.stop()

# --- 4. DATA CLEANING (Removing 0 and raw from the Type) ---
# Filter to keep only types 1-5 (assuming they are numeric or strings "1"-"5")
# We remove anything that is exactly 0 or "raw"
df = df[~df[TYPE_COL].astype(str).str.lower().isin(['0', 'raw'])]

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

# Display table WITHOUT the index (the 0-5 sequence numbers)
st.dataframe(stats.sort_values(by=TYPE_COL), hide_index=True, use_container_width=True)

# --- 7. DETAILED INSPECTION (Limited Columns) ---
st.divider()
st.subheader("🔍 Inspection: Duplicate Application Details")

# Filter for duplicates
dupe_filter = df[df.duplicated(subset=[ID_COL], keep=False)]

category_list = ["All Types"] + sorted(list(df[TYPE_COL].unique().astype(str)))
selected_cat = st.selectbox("Filter duplicates by Application Type:", category_list)

if selected_cat != "All Types":
    display_df = dupe_filter[dupe_filter[TYPE_COL].astype(str) == selected_cat]
else:
    display_df = dupe_filter

if not display_df.empty:
    st.write(f"Showing duplicate records (Application Number and Title only):")
    
    # Strictly show only the Application Number and Title columns
    # We use sort_values so the duplicates appear right next to each other
    final_view = display_df[[ID_COL, TITLE_COL]].sort_values(by=ID_COL)
    
    st.dataframe(final_view, hide_index=True, use_container_width=True)
else:
    st.success("No duplicates found for this selection!")
