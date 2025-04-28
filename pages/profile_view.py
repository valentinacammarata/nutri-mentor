import streamlit as st
import datetime
import json
import os

# Seitenkonfiguration
st.set_page_config(page_title="Your Profile", layout="centered")

# Hintergrundfarbe
st.markdown("""
    <style>
        .stApp { background-color: #d4edda; }
        h1, h2, h3, p, label, .stMetricValue, .stMetricLabel { color: black; }
        .stButton>button { background-color: #388e3c; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# Begrüßung
st.markdown("""
    <h1 style='text-align: center;'>🌟 Welcome to Your Nutri Dashboard 🌟</h1>
    <p style='text-align: center;'>Here you can view your profile, track your progress and calculate your BMI.</p>
    <hr>
""", unsafe_allow_html=True)

# Versuchen, gespeicherte Profildaten zu laden
if os.path.exists("profile_data.json"):
    with open("profile_data.json", "r") as f:
        profile_data = json.load(f)
else:
    st.error("No profile data found. Please create your profile first.")
    st.stop()

# Profilübersicht
st.subheader("👤 Profile Overview")
col1, col2 = st.columns(2)
with col1:
    st.metric("Name", profile_data.get("name", "N/A"))
    st.metric("Age", profile_data.get("age", "N/A"))
    st.metric("Gender", profile_data.get("gender", "N/A"))
with col2:
    goals = ", ".join(profile_data.get("goals", []))
    st.metric("Goal(s)", goals if goals else "N/A")
    st.metric("Diet", profile_data.get("diet", "N/A"))

# Gewichtstracker
st.subheader("🏋️ Weight Tracker")
date = st.date_input("🗓️ Select Date", datetime.date.today())
weight = st.number_input("Your Current Weight (kg)", min_value=30.0, max_value=200.0, step=0.5)
if st.button("Log Weight"):
    st.success(f"Weight of {weight} kg logged for {date}.")

# BMI Rechner
st.subheader("📊 Calculate your BMI")
height = st.number_input("Your Height (m)", min_value=1.0, max_value=2.5, step=0.01)
weight_bmi = st.number_input("Your Weight (kg)", min_value=30.0, max_value=200.0, step=0.5, key="bmi_weight")

if height > 0 and weight_bmi > 0:
    bmi = round(weight_bmi / (height ** 2), 2)
    st.metric("Your BMI", bmi)
    if bmi < 18.5:
        st.warning("You're underweight.")
    elif bmi < 25:
        st.success("You're in a healthy range.")
    elif bmi < 30:
        st.warning("You're overweight.")
    else:
        st.error("Obese range.")

# Footer
st.markdown("""
    <p style='text-align: center; font-size: 14px; color: black;'>Made with ❤️ by Team Nutri • 2025</p>
""", unsafe_allow_html=True)

# Sidebar ausblenden
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)