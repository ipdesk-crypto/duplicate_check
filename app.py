import streamlit as st
import pandas as pd

st.set_page_config(page_title="GitHub Data Tracker", layout="wide")

# --- CONFIGURATION ---
# Replace this with the RAW URL you copied in Step 1
GITHUB_CSV_URL = "https://raw.githubusercontent.com/username/repo/main/data.csv"
ID_COL = "Application Number" 
TYPE_COL = "Application Type"

st.title("📋 Automated Duplicate Checker")
st.info(f"Pulling data from GitHub: `{GITHUB_CSV_URL.split('/')[-1]}`")

@st.cache_data
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(GITHUB_CSV_URL)
    
    # --- METRICS CALCULATION ---
    total_apps = len(df)
    total_unique = df[ID_COL].nunique()
    total_dupes = total_apps - total_unique

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Count", total_apps)
    col2.metric("Unique Apps", total_unique)
    col3.metric("Duplicates Found", total_dupes)

    # --- CATEGORY BREAKDOWN ---
    st.subheader("📊 Statistics by Application Type")
    
    # Calculate stats per type
    stats = df.groupby(TYPE_COL)[ID_COL].agg(['count', 'nunique']).reset_index()
    stats['duplicates'] = stats['count'] - stats['nunique']
    stats.columns = ["Type", "Total", "Unique", "Duplicates"]
    
    st.table(stats) # Using a table for a clean, static look

    # --- DRILL DOWN ---
    st.subheader("🔍 View Duplicate Application Numbers")
    
    # Filter for types that actually HAVE duplicates to keep it clean
    types_with_dupes = stats[stats['Duplicates'] > 0]["Type"].tolist()
    
    if types_with_dupes:
        selected_type = st.selectbox("Select Type to see Duplicate IDs:", types_with_dupes)
        
        # Get only the rows for that type where the ID is repeated
        type_df = df[df[TYPE_COL] == selected_type]
        dupe_ids = type_df[type_df.duplicated(subset=[ID_COL], keep=False)].sort_values(by=ID_COL)
        
        st.write(f"Showing duplicate entries for **{selected_type}**:")
        st.dataframe(dupe_ids[[ID_COL, TYPE_COL]], use_container_width=True)
    else:
        st.success("No duplicates found in any category!")

except Exception as e:
    st.error(f"Could not load CSV. Check your URL or Column Names. Error: {e}")
