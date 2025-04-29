import streamlit as st
import pandas as pd
from datetime import datetime

# Must be the first Streamlit command
st.set_page_config(page_title="Weight Tracker", layout="centered")

# Title
st.title("NutriMentor")
st.subheader("📉 Weight Tracker")
st.write("Enter up to 5 weights at once and track your progress.")

# File path
DATA_FILE = "weight_data.csv"

# Load data or create an empty table
def load_data():
    try:
        return pd.read_csv(DATA_FILE, parse_dates=["Date"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Weight"])

# Save data
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Input: up to 5 values
st.header("➕ Enter Weights (max. 5)")
weight_data = []

for i in range(5):
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input(f"{i+1}. Weight (kg)", min_value=30.0, max_value=300.0, step=0.1, key=f"weight_{i}")
    with col2:
        date = st.date_input(f"{i+1}. Date", value=datetime.today().date(), key=f"date_{i}")
    
    # Only save if a weight is entered
    if weight > 0:
        weight_data.append({"Date": date, "Weight": weight})

# Save button
if st.button("💾 Save All"):
    if len(weight_data) == 0:
        st.warning("Please enter at least one weight.")
    else:
        df = load_data()
        new_entries = pd.DataFrame(weight_data)
        df = pd.concat([df, new_entries], ignore_index=True)
        df = df.drop_duplicates(subset=["Date"], keep="last")  # Only one entry per date
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
