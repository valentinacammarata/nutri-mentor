import streamlit as st
import datetime

# Seitenkonfiguration
st.set_page_config(page_title="Your Profile", layout="centered")

# Hintergrundfarbe
st.markdown("""
    <style>
        .stApp {
            background-color: #d4edda; /* Hellgrün */
        }
        h1, h2, h3, p, label, .stMetricValue, .stMetricLabel {
            color: black;
        }
        .stButton>button {
            background-color: #388e3c;
            color: white;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# 🌿 Begrüßungstitel
st.markdown("""
    <h1 style='text-align: center;'>🌟 Welcome to Your Nutri Dashboard 🌟</h1>
    <p style='text-align: center;'>Here you can view your profile, track your progress and calculate your BMI.</p>
    <hr>
""", unsafe_allow_html=True)

# Profilanzeige (Platzhalter)
st.subheader("👤 Profile Overview")
col1, col2 = st.columns(2)
with col1:
    st.metric("Name", "John Doe")
    st.metric("Age", "25")
    st.metric("Gender", "Male")
with col2:
    st.metric("Goal", "Build Muscle")
    st.metric("Diet", "Low-Carb")

# Gewichtstracker
date = st.date_input("🗓️ Select Date", datetime.date.today())
weight = st.number_input("🏋️ Your Current Weight (kg)", min_value=30.0, max_value=200.0, step=0.5)
if st.button("Log Weight"):
    st.success(f"Weight of {weight} kg logged for {date}.")

# BMI Rechner
st.subheader("📊 Calculate your BMI")
height = st.number_input("Your Height (in meters)", min_value=1.0, max_value=2.5, step=0.01)
weight_bmi = st.number_input("Your Weight (in kg)", min_value=30.0, max_value=200.0, step=0.5, key="bmi_weight")

if height > 0 and weight_bmi > 0:
    bmi = round(weight_bmi / (height ** 2), 2)
    st.metric("Your BMI", bmi)
    if bmi < 18.5:
        st.warning("You're underweight. Consider speaking with a nutritionist.")
    elif bmi < 25:
        st.success("Great! You're in a healthy range.")
    elif bmi < 30:
        st.warning("You're overweight. Consider reviewing your goals.")
    else:
        st.error("Obese range. Please consult with a health professional.")

# Animation oder Feedback
st.markdown("""
    <p style='text-align: center; font-size: 14px; color: #ffffff;'>Made with ❤️ by Team Nutri • 2025</p>
""", unsafe_allow_html=True)

# Hide the sidebar by default
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)