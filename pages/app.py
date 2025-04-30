import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Must be the first Streamlit command
st.set_page_config(page_title="Weight Tracker", layout="centered")

# Title
st.markdown("<h1 style='text-align: center;'>📉 Data View</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Track your progress and stay motivated!</p>", unsafe_allow_html=True)

# Background color (same as in profilepage.py)
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

st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
# Dynamische Gewichtseingabe (Start mit 3, Button für mehr)
st.markdown("<h2 style='text-align: center;'>➕ Enter Weights</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Tracking your weight regularly helps you monitor your health and achieve your fitness goals effectively.</p>", unsafe_allow_html=True)

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


st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
# Visualization
st.markdown("<h2 style='text-align: center;'>📊 Show Progress</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Visualize your weight trends and stay on track with your goals.</p>", unsafe_allow_html=True)

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

# Advanced Section
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <h1 style='text-align: center;'>🔬 Advanced Body Composition Tracking</h1>
""", unsafe_allow_html=True)

advanced = st.selectbox("", ["Hide", "Show"])
if advanced == "Show":
    # Body Fat
    st.markdown("""
        <h2 style='text-align: center;'>📉 Body Fat (%)</h2>
        <p style='text-align: center;'>Track your body fat percentage over time.</p>
    """, unsafe_allow_html=True)
    with st.form("body_fat_form"):
        bdate = st.date_input("📅 Date", value=datetime.today(), key="fat_date")
        fat_vals = [st.slider(f"Body Fat % {i+1}", 5.0, 50.0, 20.0, key=f"fat_{i}") for i in range(3)]
        submitted = st.form_submit_button("💾 Save Body Fat")
        if submitted:
            comp_df = load_body_composition() 
            new_entry = pd.DataFrame([{"Date": bdate, "Body Fat": sum(fat_vals)/len(fat_vals)}])
            comp_df = pd.concat([comp_df, new_entry], ignore_index=True)
            comp_df = comp_df.drop_duplicates(subset=["Date"], keep="last")
            save_body_composition(comp_df)
            st.success("Body fat data saved!")
    comp_df = load_body_composition()
    if "Body Fat" in comp_df:
        st.bar_chart(comp_df.set_index("Date")["Body Fat"])

    # Muscle Mass
    st.markdown("""
        <h2 style='text-align: center;'>💪 Muscle Mass (%)</h2>
        <p style='text-align: center;'>Follow your progress in building muscle mass.</p>
    """, unsafe_allow_html=True)
    with st.form("muscle_mass_form"):
        mdate = st.date_input("📅 Date", value=datetime.today(), key="muscle_date")
        muscle_vals = [st.slider(f"Muscle Mass % {i+1}", 10.0, 60.0, 35.0, key=f"muscle_{i}") for i in range(3)]
        submitted = st.form_submit_button("💾 Save Muscle Mass")
        if submitted:
            comp_df = load_body_composition()
            new_entry = pd.DataFrame([{"Date": mdate, "Muscle Mass": sum(muscle_vals)/len(muscle_vals)}])
            comp_df = pd.concat([comp_df, new_entry], ignore_index=True)
            comp_df = comp_df.drop_duplicates(subset=["Date"], keep="last")
            save_body_composition(comp_df)
            st.success("Muscle mass data saved!")
    if "Muscle Mass" in comp_df:
        st.bar_chart(comp_df.set_index("Date")["Muscle Mass"])

    # Water Content
    st.markdown("""
        <h2 style='text-align: center;'>💧 Water Content (%)</h2>
        <p style='text-align: center;'>Track hydration and body water balance.</p>
    """, unsafe_allow_html=True)
    with st.form("water_content_form"):
        wdate = st.date_input("📅 Date", value=datetime.today(), key="water_date")
        water_vals = [st.slider(f"Water Content % {i+1}", 30.0, 70.0, 50.0, key=f"water_{i}") for i in range(3)]
        submitted = st.form_submit_button("💾 Save Water Content")
        if submitted:
            comp_df = load_body_composition()
            new_entry = pd.DataFrame([{"Date": wdate, "Water Content": sum(water_vals)/len(water_vals)}])
            comp_df = pd.concat([comp_df, new_entry], ignore_index=True)
            comp_df = comp_df.drop_duplicates(subset=["Date"], keep="last")
            save_body_composition(comp_df)
            st.success("Water content data saved!")
    if "Water Content" in comp_df:
        st.bar_chart(comp_df.set_index("Date")["Water Content"])


    # Hide the sidebar by default
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)