import streamlit as st
import pandas as pd
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Application Duplicate Tracker", layout="wide")

FILENAME = "data.csv" 

st.title("📋 Application Duplicate Checker")

# --- 2. DATA LOADING LOGIC ---
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        # We read the file and immediately clean the headers
        data = pd.read_csv(file_path, low_memory=False)
        # Clean white space and ensure consistent naming
        data.columns = [str(col).strip() for col in data.columns]
        return data
    return None

df = load_data(FILENAME)

if df is not None:
    # --- 3. DYNAMIC COLUMN MAPPING ---
    # This prevents the KeyError by searching for the best match if exact match fails
    def get_col_name(target, columns):
        if target in columns:
            return target
        # Fallback: look for a column that starts with or contains the name
        for col in columns:
            if target.lower() in col.lower():
                return col
        return None

    ID_COL = get_col_name("Application Number", df.columns)
    TYPE_COL = get_col_name("Application Type (ID) df.columns)
    TITLE_COL = get_col_name("Title in English", df.columns)

    # Safety Stop if columns are completely missing
    if not ID_COL or not TYPE_COL:
        st.error("⚠️ Column Mapping Error")
        st.write("Could not find 'Application Number' or 'Application Type(ID)'")
        st.write("Actual Columns in CSV:", list(df.columns))
        st.stop()

    # --- 4. DATA CLEANING ---
    # Force Type to string and remove rows where it's '0' or 'raw'
    df[TYPE_COL] = df[TYPE_COL].astype(str).str.strip()
    df = df[~df[TYPE_COL].str.lower().isin(['0', 'raw', '0.0'])]

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

    # hide_index=True removes the confusing 0, 1, 2, 3... sequence
    st.dataframe(stats.sort_values(by=TYPE_COL), hide_index=True, use_container_width=True)

    # --- 7. DETAILED INSPECTION (Limited Columns) ---
    st.divider()
    st.subheader("🔍 Inspection: Duplicate Application Details")

    # Find all instances of rows that share an Application Number
    dupe_filter = df[df.duplicated(subset=[ID_COL], keep=False)]

    category_list = ["All Types"] + sorted(list(df[TYPE_COL].unique()))
    selected_cat = st.selectbox("Filter duplicates by Application Type:", category_list)

    if selected_cat != "All Types":
        display_df = dupe_filter[dupe_filter[TYPE_COL] == selected_cat]
    else:
        display_df = dupe_filter

    if not display_df.empty:
        st.write(f"Showing duplicate records (IDs and Titles only):")
        
        # Only show the two columns requested
        # Handling the case where Title might be missing
        cols_to_show = [ID_COL]
        if TITLE_COL:
            cols_to_show.append(TITLE_COL)
            
        final_view = display_df[cols_to_show].sort_values(by=ID_COL)
        
        st.dataframe(final_view, hide_index=True, use_container_width=True)
    else:
        st.success("✅ No duplicates found for this selection!")

else:
    st.error(f"❌ Could not find '{FILENAME}'")
    st.info("Check GitHub Desktop to ensure the file is synced.")
