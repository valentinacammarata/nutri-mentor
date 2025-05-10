import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import matplotlib.pyplot as plt
import numpy as np

active_page = "Data Visualization"  # Aktive Seite für die Navigation

st.markdown(f"""
    <style>
        .nav-wrapper {{
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 1rem;
        }}
        .nav-button {{
            background-color: #388e3c;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            border: 2px solid transparent;
        }}
        .nav-button:hover {{
            background-color: #2e7d32;
        }}
        .nav-button.active {{
            background-color: white;
            color: #2e7d32;
            border: 2px solid #2e7d32;
        }}
    </style>

    <div class="nav-wrapper">
        <a href="/pages/profile_view" class="nav-button {'active' if active_page == 'Profile' else ''}">👤 Profile</a>
        <a href="/pages/data_visualization" class="nav-button {'active' if active_page == 'Visual Data' else ''}">📊 Visual Data</a>
        <a href="/pages/Recipes Generator" class="nav-button {'active' if active_page == 'Recipes' else ''}">🥗 Recipes</a>
        <a href="/pages/Calories Tracker" class="nav-button {'active' if active_page == 'Calories' else ''}">📒 Calories</a>
    </div>
""", unsafe_allow_html=True)

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
DATA_FILE = "ressources/weight_data.csv"
PROFILE_FILE = "ressources/profile_data.json"
BODY_COMP_FILE = "ressources/body_composition.json"

# === PROFILE IMPORT BLOCK (immer importieren) ===
imported_msg = None  # Zum Anzeigen oben

if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r") as f:
        profile = json.load(f)

    if "weight" in profile and "date" in profile:
        init_entry = pd.DataFrame([{
            "Date": profile["date"],
            "Weight": profile["weight"]
        }])

        if os.path.exists(DATA_FILE):
            df_existing = pd.read_csv(DATA_FILE)
            df_combined = pd.concat([init_entry, df_existing], ignore_index=True)
            df_combined = df_combined.drop_duplicates(subset=["Date"], keep="first")
            df_combined.to_csv(DATA_FILE, index=False)
        else:
            init_entry.to_csv(DATA_FILE, index=False)

        imported_msg = f"✅ Initial weight ({profile['weight']} kg on {profile['date']}) imported from profile!"

# Erfolgsmeldung anzeigen, wenn Daten importiert wurden
if imported_msg:
    st.success(imported_msg)

# Title for Enter Weights
st.markdown("""
    <div style='margin-top: 70px;'></div>
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
        df = pd.read_json(BODY_COMP_FILE)
        if df.empty or not all(col in df.columns for col in ["Date", "Body Fat", "Muscle Mass", "Water Content"]):
            return pd.DataFrame(columns=["Date", "Body Fat", "Muscle Mass", "Water Content"])
        return df
    except Exception:
        return pd.DataFrame(columns=["Date", "Body Fat", "Muscle Mass", "Water Content"])

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

if st.button("📄 Save All"):
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
    df = df.sort_values("Date")
    st.subheader("📈 Weight Over Time")
    st.line_chart(df.set_index("Date")["Weight"])
    st.subheader("📋 Table")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data available yet. Enter something to get started.")
# ================= ADVANCED BODY COMPOSITION SECTION =================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <h1 style='text-align: center;'>Advanced Body Composition Tracking</h1>
    <p style='text-align: center; font-size: 1.05em; color: #2f5732;'>
        Start by entering a single body composition entry. Below, you can add more entries and compare them visually. 
    </p>
""", unsafe_allow_html=True)

# Load data
comp_df = load_body_composition()
comp_df["Date"] = pd.to_datetime(comp_df["Date"], errors="coerce")  # ✅ NEU: zur Sicherheit

# === EINZELNE ERSTEINGABE MIT SOFORTIGEM DIAGRAMM ===
st.subheader("📥 First Entry or Today's Body Composition")
entry_date = st.date_input("🗓️ Date", datetime.today(), key="main_entry_date")

col1, col2, col3 = st.columns(3)
with col1:
    body_fat = st.slider("Body Fat (%)", 5.0, 50.0, 20.0, 0.1, key="main_bf")
with col2:
    muscle_mass = st.slider("Muscle Mass (%)", 10.0, 60.0, 35.0, 0.1, key="main_mm")
with col3:
    water_content = st.slider("Water Content (%)", 30.0, 70.0, 50.0, 0.1, key="main_wc")

if st.button("📄 Save Today's Entry", key="main_save_btn"):
    new_entry = pd.DataFrame([{
        "Date": entry_date,
        "Body Fat": body_fat,
        "Muscle Mass": muscle_mass,
        "Water Content": water_content
    }])
    comp_df = pd.concat([comp_df, new_entry], ignore_index=True)
    comp_df = comp_df.drop_duplicates(subset=["Date"], keep="last")
    save_body_composition(comp_df)
    st.success("Today's entry saved successfully!")

    # === Direkte Visualisierung: Kreis- und Balkendiagramm ===
    latest = new_entry.iloc[0]
    bf, mm, wc = latest["Body Fat"], latest["Muscle Mass"], latest["Water Content"]
    other = max(0, 100 - (bf + mm + wc))

    labels = ['Body Fat', 'Muscle Mass', 'Water Content', 'Other']
    values = [bf, mm, wc, other]
    colors = ['#f4a261', '#2a9d8f', '#264653', '#cccccc']

    st.markdown("<h3 style='text-align: center;'>🧭 Composition Breakdown</h3>", unsafe_allow_html=True)
    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax1.axis("equal")
    st.pyplot(fig1)

    st.markdown("<h3 style='text-align: center;'>📊 Single Entry Overview</h3>", unsafe_allow_html=True)
    fig_bar, ax_bar = plt.subplots()
    categories = ['Body Fat', 'Muscle Mass', 'Water Content']
    values = [bf, mm, wc]
    ax_bar.bar(categories, values, color=colors[:3])
    ax_bar.set_ylabel("Percentage")
    st.pyplot(fig_bar)

# === MEHRERE EINTRÄGE MÖGLICH NACH DER ERSTEN EINGABE ===
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <h2 style='text-align: center;'>➕ Add More Entries</h2>
    <p style='text-align: center;'>Track additional progress over time.</p>
""", unsafe_allow_html=True)

new_date = st.date_input("📅 Date", datetime.today(), key="extra_date")
col1, col2, col3 = st.columns(3)
with col1:
    new_bf = st.slider("Body Fat (%)", 5.0, 50.0, 20.0, 0.1, key="extra_bf")
with col2:
    new_mm = st.slider("Muscle Mass (%)", 10.0, 60.0, 35.0, 0.1, key="extra_mm")
with col3:
    new_wc = st.slider("Water Content (%)", 30.0, 70.0, 50.0, 0.1, key="extra_wc")

if st.button("💾 Save Additional Entry"):
    extra_entry = pd.DataFrame([{
        "Date": new_date,
        "Body Fat": new_bf,
        "Muscle Mass": new_mm,
        "Water Content": new_wc
    }])
    comp_df = pd.concat([comp_df, extra_entry], ignore_index=True)
    comp_df = comp_df.drop_duplicates(subset=["Date"], keep="last")
    save_body_composition(comp_df)
    st.success("Additional entry saved!")

# === VERGLEICH NUR WENN MEHR ALS 1 EINTRAG VORHANDEN IST ===
if len(comp_df) > 1:
    comp_df["Date"] = pd.to_datetime(comp_df["Date"], errors="coerce")  # ✅ NEU: vor Sortierung
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <h2 style='text-align: center;'>📈 Compare Recent Entries</h2>
        <p style='text-align: center;'>Automatic comparison of your latest entries.</p>
    """, unsafe_allow_html=True)

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

# === MANUELLER VERGLEICH AB 2 EINTRÄGEN ===
if len(comp_df) >= 2:
    comp_df["Date"] = pd.to_datetime(comp_df["Date"], errors="coerce")  # ✅ NEU: vor Auswahl
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <h2 style='text-align: center;'>🔍 Manual Comparison</h2>
        <p style='text-align: center;'>Select two dates to compare them directly.</p>
    """, unsafe_allow_html=True)

    dates = comp_df["Date"].dropna().sort_values().unique()
    compare_date_1 = st.selectbox("Select first date", dates, key="comp1")
    compare_date_2 = st.selectbox("Select second date", dates, key="comp2")

    if compare_date_1 != compare_date_2:
        entry1 = comp_df[comp_df["Date"] == compare_date_1].iloc[0]
        entry2 = comp_df[comp_df["Date"] == compare_date_2].iloc[0]

        comparison_df = pd.DataFrame({
            "Category": ["Body Fat", "Muscle Mass", "Water Content"],
            str(compare_date_1): [entry1["Body Fat"], entry1["Muscle Mass"], entry1["Water Content"]],
            str(compare_date_2): [entry2["Body Fat"], entry2["Muscle Mass"], entry2["Water Content"]]
        })

        st.dataframe(comparison_df, use_container_width=True)