import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Must be the first Streamlit command
st.set_page_config(page_title="Weight Tracker", layout="centered")

# Title
st.markdown("<h1 style='text-align: center;'>📉 Weight Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Track your progress and stay motivated!</p>", unsafe_allow_html=True)

#background color
st.markdown("""
    <style>
        .stApp { background-color: #a9dfbf; }
    </style>
""", unsafe_allow_html=True)

# File path
DATA_FILE = "weight_data.csv"
PROFILE_FILE = "profile_data.json"

# Load data or create an empty table
def load_data():
    try:
        return pd.read_csv(DATA_FILE, parse_dates=["Date"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Weight"])
    
# Save data
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Import initial profile weight if available
initial_entry_added = False
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r") as f:
        profile = json.load(f)
        if "weight" in profile and "date" in profile:
            try:
                existing = load_data()
                new_row = pd.DataFrame([{"Date": profile["date"], "Weight": profile["weight"]}])
                df_combined = pd.concat([existing, new_row], ignore_index=True)
                df_combined = df_combined.drop_duplicates(subset=["Date"], keep="last")
                save_data(df_combined)
                initial_entry_added = True
            except Exception as e:
                st.error(f"Error importing initial weight: {e}")

if initial_entry_added:
    st.success(f"Initial weight entry from profile ({profile['weight']} kg on {profile['date']}) imported!")

# Dynamische Gewichtseingabe (Start mit 3, Button für mehr)
st.header("➕ Enter Weights")

if "weight_rows" not in st.session_state:
    st.session_state.weight_rows = 3

weight_data = []

for i in range(st.session_state.weight_rows):
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input(f"{i+1}. Weight (kg)", min_value=30.0, max_value=300.0, step=0.1, key=f"weight_{i}")
    with col2:
        date = st.date_input(f"{i+1}. Date", value=datetime.today().date(), key=f"date_{i}")
    
    if weight > 0:
        weight_data.append({"Date": date, "Weight": weight})

# + Button zum Hinzufügen weiterer Eingaben
if st.button("➕ Add another row"):
    st.session_state.weight_rows += 1
# Save button
if st.button("💾 Save All"):
    if len(weight_data) == 0:
        st.warning("Please enter at least one weight.")
    else:
        df = load_data()
        new_entries = pd.DataFrame(weight_data)
        df = pd.concat([df, new_entries], ignore_index=True)
        df = df.drop_duplicates(subset=["Date"], keep="last")
        save_data(df)
        st.success(f"{len(weight_data)} entries saved! ✅")

# Visualization
st.header("📊 Show Progress")
df = load_data()

if not df.empty:
    time_range = st.selectbox("Select Time Range", ["All", "Last 7 Days", "Last 30 Days"])

    if time_range == "Last 7 Days":
        df = df[df["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=7)]
    elif time_range == "Last 30 Days":
        df = df[df["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=30)]

    df = df.sort_values("Date")

    st.subheader("📈 Weight Over Time")
    st.line_chart(df.set_index("Date")["Weight"])

    st.subheader("📋 Table")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data available yet. Enter something to get started.")  

    # Hide the sidebar by default
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)