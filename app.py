import streamlit as st
import pandas as pd
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Application Duplicate Checker", layout="wide")

st.title("📋 Application Duplicate Checker")
st.markdown("This app analyzes your CSV for duplicate application numbers grouped by type.")

# --- 2. DATA LOADING LOGIC ---
# This looks for 'data.csv' in your GitHub folder first
FILENAME = "data.csv" 

@st.cache_data
def process_data(file):
    return pd.read_csv(file, low_memory=False)

# Check if file exists in the GitHub repo
if os.path.exists(FILENAME):
    df = process_data(FILENAME)
    st.success(f"✅ Loaded `{FILENAME}` from GitHub repository.")
else:
    st.warning(f"⚠️ `{FILENAME}` not found in GitHub. Please upload it manually below.")
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
    if uploaded_file:
        df = process_data(uploaded_file)
    else:
        st.stop() # Stops the app until a file is provided

# --- 3. COLUMN SELECTION ---
# Adjust these strings if your CSV headers are different
ID_COL = "Application Number" 
TYPE_COL = "Application Type"

if ID_COL not in df.columns or TYPE_COL not in df.columns:
    st.error(f"Column Name Error! Found: {list(df.columns)}")
    st.info(f"Make sure your columns are named exactly '{ID_COL}' and '{TYPE_COL}'.")
    st.stop()

# --- 4. TOP-LEVEL METRICS ---
total_apps = len(df)
unique_apps = df[ID_COL].nunique()
duplicate_count = total_apps - unique_apps

col1, col2, col3 = st.columns(3)
col1.metric("Total Applications", f"{total_apps:,}")
col2.metric("Unique Applications", f"{unique_apps:,}")
col3.metric("Duplicate Entries", f"{duplicate_count:,}")

# --- 5. BREAKDOWN BY TYPE ---
st.subheader("📊 Statistics by Application Type")

# Calculate stats per category
stats = df.groupby(TYPE_COL)[ID_COL].agg(['count', 'nunique']).reset_index()
stats['Duplicates'] = stats['count'] - stats['nunique']
stats.columns = ["Application Type", "Total Apps", "Unique Apps", "Duplicate Apps"]

# Display table
st.dataframe(stats.sort_values(by="Duplicate Apps", ascending=False), use_container_width=True)

# --- 6. DETAILED DUPLICATE LIST ---
st.divider()
st.subheader("🔍 Inspection: See Duplicate Application Numbers")

# Filter logic: show only actual duplicates
dupe_filter = df[df.duplicated(subset=[ID_COL], keep=False)]

category_list = ["All Types"] + list(df[TYPE_COL].unique())
selected_cat = st.selectbox("Filter duplicates by Application Type:", category_list)

if selected_cat != "All Types":
    display_df = dupe_filter[dupe_filter[TYPE_COL] == selected_cat]
else:
    display_df = dupe_filter

if not display_df.empty:
    st.write(f"Showing {len(display_df):,} duplicate records:")
    # We sort by ID so duplicates appear next to each other
    st.dataframe(display_df.sort_values(by=ID_COL), use_container_width=True)
else:
    st.success("No duplicates found for this selection!")
