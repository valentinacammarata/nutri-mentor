import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
st.markdown("""
    <h1 style='text-align: center;'>📊 Data View</h1>
""", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center;'> Track your weight and body composition effortlessly. <br>
            Tracking your fitness data is important because it helps you monitor your progress, set realistic goals, stay motivated, and make informed decisions about your exercise routine. It also allows you to identify patterns and areas for improvement, potentially preventing injuries and optimizing your training. </p>
""", unsafe_allow_html=True)

# Set background color
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

set_background_color("#d4f4dd")  # Light green color

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

# Import profile data once
if os.path.exists(PROFILE_FILE) and not os.path.exists(DATA_FILE):
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

# ================= ADVANCED BODY SECTION =================
import matplotlib.pyplot as plt

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <h1 style='text-align: center;'>🔬 Advanced Body Composition Tracking</h1>
    <p style='text-align: center;'>Track your body composition step by step. Start with one entry and add more if needed.</p>
""", unsafe_allow_html=True)

# Initial states
for key, default in [("fat_entries", 1), ("muscle_entries", 1), ("water_entries", 1)]:
    if key not in st.session_state:
        st.session_state[key] = default

# Safe loading of composition data
def load_body_composition():
    try:
        if os.path.exists("body_composition.json") and os.path.getsize("body_composition.json") > 0:
            return pd.read_json("body_composition.json")
        else:
            return pd.DataFrame(columns=["Date", "Body Fat", "Muscle Mass", "Water Content"])
    except Exception:
        return pd.DataFrame(columns=["Date", "Body Fat", "Muscle Mass", "Water Content"])

def save_body_composition(df):
    df.to_json("body_composition.json", orient="records")

comp_df = load_body_composition()

# ========== BODY FAT ==========
st.markdown("<h2 style='text-align: center;'>📉 Body Fat (%)</h2>", unsafe_allow_html=True)
fdate = st.date_input("📅 Date", datetime.today(), key="fat_date")
fat_vals = [st.slider(f"Body Fat % {i+1}", 5.0, 50.0, 20.0, key=f"fat_{i}") for i in range(st.session_state.fat_entries)]

col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Add New Fat Entry"):
        st.session_state.fat_entries += 1
with col2:
    if st.button("💾 Save Body Fat"):
        for i, val in enumerate(fat_vals):
            new_entry = pd.DataFrame([{"Date": f"{fdate} - Entry {i+1}", "Body Fat": val}])
            comp_df = pd.concat([comp_df, new_entry], ignore_index=True)
        save_body_composition(comp_df)
        st.success("Body fat saved!")

if "Body Fat" in comp_df:
    st.bar_chart(comp_df["Body Fat"].tail(st.session_state.fat_entries))

# ========== MUSCLE MASS ==========
st.markdown("<h2 style='text-align: center;'>💪 Muscle Mass (%)</h2>", unsafe_allow_html=True)
mdate = st.date_input("📅 Date", datetime.today(), key="muscle_date")
muscle_vals = [st.slider(f"Muscle Mass % {i+1}", 10.0, 60.0, 35.0, key=f"muscle_{i}") for i in range(st.session_state.muscle_entries)]

col3, col4 = st.columns(2)
with col3:
    if st.button("➕ Add New Muscle Entry"):
        st.session_state.muscle_entries += 1
with col4:
    if st.button("💾 Save Muscle Mass"):
        for i, val in enumerate(muscle_vals):
            new_entry = pd.DataFrame([{"Date": f"{mdate} - Entry {i+1}", "Muscle Mass": val}])
            comp_df = pd.concat([comp_df, new_entry], ignore_index=True)
        save_body_composition(comp_df)
        st.success("Muscle mass saved!")

if "Muscle Mass" in comp_df:
    st.bar_chart(comp_df["Muscle Mass"].tail(st.session_state.muscle_entries))

# ========== WATER CONTENT ==========
st.markdown("<h2 style='text-align: center;'>💧 Water Content (%)</h2>", unsafe_allow_html=True)
wdate = st.date_input("📅 Date", datetime.today(), key="water_date")
water_vals = [st.slider(f"Water Content % {i+1}", 30.0, 70.0, 50.0, key=f"water_{i}") for i in range(st.session_state.water_entries)]

col5, col6 = st.columns(2)
with col5:
    if st.button("➕ Add New Water Entry"):
        st.session_state.water_entries += 1
with col6:
    if st.button("💾 Save Water Content"):
        for i, val in enumerate(water_vals):
            new_entry = pd.DataFrame([{"Date": f"{wdate} - Entry {i+1}", "Water Content": val}])
            comp_df = pd.concat([comp_df, new_entry], ignore_index=True)
        save_body_composition(comp_df)
        st.success("Water content saved!")

if "Water Content" in comp_df:
    st.bar_chart(comp_df["Water Content"].tail(st.session_state.water_entries))

# ========== PIE CHART WITH "OTHER" ==========
latest_fat = comp_df["Body Fat"].dropna().iloc[-1] if "Body Fat" in comp_df and not comp_df["Body Fat"].dropna().empty else None
latest_muscle = comp_df["Muscle Mass"].dropna().iloc[-1] if "Muscle Mass" in comp_df and not comp_df["Muscle Mass"].dropna().empty else None
latest_water = comp_df["Water Content"].dropna().iloc[-1] if "Water Content" in comp_df and not comp_df["Water Content"].dropna().empty else None

if all(val is not None for val in [latest_fat, latest_muscle, latest_water]):
    other = max(0, 100 - (latest_fat + latest_muscle + latest_water))
    values = [latest_fat, latest_muscle, latest_water, other]
    labels = ['Body Fat', 'Muscle Mass', 'Water Content', 'Other']

    st.markdown("""
        <h2 style='text-align: center;'>🧬 Your Full Body Composition</h2>
        <p style='text-align: center;'>Here you can see your latest tracked body composition including 'Other' as balance.</p>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.info("Please ensure you've logged values for fat, muscle, and water to see your full composition.")
