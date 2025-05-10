import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# === TITLE SECTION (ohne Emoji, einheitlich gestylt) ===
st.markdown("""
    <h1 style='text-align: center; font-size: 2.5em; color: #2f2f2f;'>Track your Progress</h1>
""", unsafe_allow_html=True)

st.markdown("""
    <p style='text-align: center; font-size: 1.1em; color: #2f5732;'>
        Track your weight and body composition effortlessly.<br>
        Tracking your fitness data is important because it helps you monitor your progress, set realistic goals, stay motivated, 
        and make informed decisions about your exercise routine. It also allows you to identify patterns and areas for improvement, 
        potentially preventing injuries and optimizing your training.
    </p>
""", unsafe_allow_html=True)

# === HORIZONTALE LINIE ===
st.markdown("<hr style='border: none; border-top: 1px solid #a9c4ab;'>", unsafe_allow_html=True)

# === BACKGROUND COLOR ===
def set_background_color(color):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background_color("#d4f4dd")  # Light green background

# File paths
DATA_FILE = "weight_data.csv"
PROFILE_FILE = "profile_data.json"
BODY_COMP_FILE = "body_composition.json"

st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)
# Title for Enter Weights
st.markdown("""
    <h2 style='text-align: center;'>📥 Enter Weights</h2>
    <p style='text-align: center;'>Log your weight to track your progress over time.</p>
""", unsafe_allow_html=True)

# Save/load helpers
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_data():
    try:
        return pd.read_csv(DATA_FILE, parse_dates=["Date"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Weight"])

def save_body_composition(df):
    df.to_json(BODY_COMP_FILE, orient="records")

def load_body_composition():
    try:
        return pd.read_json(BODY_COMP_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Body Fat", "Muscle Mass", "Water Content"])

# Import profile data once if weight file is missing or empty
if os.path.exists(PROFILE_FILE):
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(PROFILE_FILE, "r") as f:
            profile = json.load(f)
            if "weight" in profile and "date" in profile:
                init_entry = pd.DataFrame([{
                    "Date": profile["date"],
                    "Weight": profile["weight"]
                }])
                save_data(init_entry)
                st.success(f"Initial weight ({profile['weight']} kg on {profile['date']}) imported!")


# Dynamic weight input
if "weight_rows" not in st.session_state:
    st.session_state.weight_rows = 3

weight_data = []
for i in range(st.session_state.weight_rows):
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input(f"Weight (kg) {i+1}", min_value=30.0, max_value=300.0, step=0.1, key=f"weight_{i}")
    with col2:
        date = st.date_input(f"Date {i+1}", value=datetime.today().date(), key=f"date_{i}")
    if weight > 0:
        weight_data.append({"Date": date, "Weight": weight})

if st.button("➕ Add another row"):
    st.session_state.weight_rows += 1

if st.button("💾 Save All"):
    if weight_data:
        df = load_data()
        new_entries = pd.DataFrame(weight_data)
        df = pd.concat([df, new_entries], ignore_index=True)
        df = df.drop_duplicates(subset=["Date"], keep="last")
        save_data(df)
        st.success(f"{len(weight_data)} entries saved! ✅")
    else:
        st.warning("Please enter at least one weight.")


st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
# Visualization
st.markdown("""
    <h2 style='text-align: center;'>📊 Show Progress</h2>
    <p style='text-align: center;'>Visualize your weight trends and progress over time.</p>
""", unsafe_allow_html=True)
df = load_data()
if not df.empty:
    time_range = st.selectbox("Select Time Range", ["All", "Last 7 Days", "Last 30 Days"])
    if time_range == "Last 7 Days":
        df = df[pd.Timestamp(df["Date"]) >= pd.Timestamp.today() - pd.Timedelta(days=7)]
    elif time_range == "Last 30 Days":
        df = df[df["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=30)]
    df = df.sort_values("Date")
    st.subheader("📈 Weight Over Time")
    st.line_chart(df.set_index("Date")["Weight"])
    st.subheader("📋 Table")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data available yet. Enter something to get started.")

# ================= NEW ADVANCED BODY COMPOSITION SECTION =================
import matplotlib.pyplot as plt
import numpy as np

BODY_COMP_FILE = "body_composition.json"

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <h1 style='text-align: center;'>Advanced Body Composition Tracking</h1>
    <p style='text-align: center; font-size: 1.05em; color: #2f5732;'>
        Track your body composition step by step. Enter your values for Body Fat, Muscle Mass, and Water Content below.
    </p>
""", unsafe_allow_html=True)

# Load/save helpers
def load_body_composition():
    try:
        if os.path.exists(BODY_COMP_FILE) and os.path.getsize(BODY_COMP_FILE) > 0:
            return pd.read_json(BODY_COMP_FILE)
        else:
            return pd.DataFrame(columns=["Date", "Body Fat", "Muscle Mass", "Water Content"])
    except Exception:
        return pd.DataFrame(columns=["Date", "Body Fat", "Muscle Mass", "Water Content"])

def save_body_composition(df):
    df.to_json(BODY_COMP_FILE, orient="records")

# Load data
comp_df = load_body_composition()

# Input section (combined entry)
st.subheader("➕ New Body Composition Entry")

entry_date = st.date_input("📅 Date", datetime.today())

col1, col2, col3 = st.columns(3)
with col1:
    body_fat = st.slider("Body Fat (%)", 5.0, 50.0, 20.0, 0.1)
with col2:
    muscle_mass = st.slider("Muscle Mass (%)", 10.0, 60.0, 35.0, 0.1)
with col3:
    water_content = st.slider("Water Content (%)", 30.0, 70.0, 50.0, 0.1)

if st.button("💾 Save Entry"):
    new_entry = pd.DataFrame([{
        "Date": entry_date,
        "Body Fat": body_fat,
        "Muscle Mass": muscle_mass,
        "Water Content": water_content
    }])
    comp_df = pd.concat([comp_df, new_entry], ignore_index=True)
    comp_df = comp_df.drop_duplicates(subset=["Date"], keep="last")
    save_body_composition(comp_df)
    st.success("Entry saved successfully!")

# ========== PIE CHART ==========
if not comp_df.empty:
    latest = comp_df.sort_values("Date").iloc[-1]
    bf, mm, wc = latest["Body Fat"], latest["Muscle Mass"], latest["Water Content"]
    other = max(0, 100 - (bf + mm + wc))

    labels = ['Body Fat', 'Muscle Mass', 'Water Content', 'Other']
    values = [bf, mm, wc, other]
    colors = ['#f4a261', '#2a9d8f', '#264653', '#cccccc']

    st.markdown("<h3 style='text-align: center;'>Body Composition Pie Chart</h3>", unsafe_allow_html=True)
    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax1.axis("equal")
    st.pyplot(fig1)

# ========== BAR CHART ==========
if len(comp_df) >= 1:
    st.markdown("<h3 style='text-align: center;'>Recent Entries Overview</h3>", unsafe_allow_html=True)
    last_entries = comp_df.sort_values("Date").tail(3)
    dates = last_entries["Date"].astype(str).tolist()
    x = np.arange(len(dates))
    bar_width = 0.25

    fig2, ax2 = plt.subplots()
    ax2.bar(x - bar_width, last_entries["Body Fat"], width=bar_width, label="Body Fat", color="#f4a261")
    ax2.bar(x, last_entries["Muscle Mass"], width=bar_width, label="Muscle Mass", color="#2a9d8f")
    ax2.bar(x + bar_width, last_entries["Water Content"], width=bar_width, label="Water Content", color="#264653")

    ax2.set_xlabel("Date")
    ax2.set_ylabel("Percentage")
    ax2.set_title("Recent Body Composition Entries")
    ax2.set_xticks(x)
    ax2.set_xticklabels(dates)
    ax2.legend()
    st.pyplot(fig2)

# ========== TABLE ==========
if not comp_df.empty:
    st.markdown("<h3 style='text-align: center;'>All Entries</h3>", unsafe_allow_html=True)
    st.dataframe(comp_df.sort_values("Date", ascending=False), use_container_width=True)
