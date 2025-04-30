import streamlit as st
import time
import json
import os

# Seitenkonfiguration
st.set_page_config(page_title="Profile Creation", layout="centered", initial_sidebar_state="collapsed")

# Hintergrundfarbe
st.markdown("""
    <style>
        .stApp { background-color: #a9dfbf; }
    </style>
""", unsafe_allow_html=True)

# Überschrift
st.markdown("""
    <h1 style='text-align: center; color: #000000;'>Create Your Nutri Profile</h1>
    <p style='text-align: center; font-size: 20px; color: #ffffff;'>Let's get started on your personalized nutrition journey.</p>
    <hr style='margin: 30px 0; border-color: #ffffff;'>
""", unsafe_allow_html=True)

# Zitat
st.markdown("""
    <blockquote style='text-align: center; font-size: 18px; color: #ffffff;'>
        "Your health is an investment, not an expense."
    </blockquote>
""", unsafe_allow_html=True)

# Formular
with st.form("profile_form"):
    name = st.text_input("Your Name")
    age = st.number_input("Your Age", min_value=10, max_value=120, step=1)
    gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
    
    st.markdown("<p style='color: #ffffff; font-size: 16px;'>What are your health goals?</p>", unsafe_allow_html=True)
    goal_options = ["Lose Weight", "Build Muscle", "just eat Healthier :)"]
    selected_goals = st.multiselect("Select your goals", goal_options)

    st.markdown("<p style='color: #ffffff; font-size: 16px;'>Dietary Preference</p>", unsafe_allow_html=True)
    diet_options = ["No Preference", "Vegetarian", "Vegan", "Low-Carb", "Keto"]
    selected_diet = st.radio("Choose one", diet_options)

    submitted = st.form_submit_button("Submit Profile")

    if submitted:
        profile_data = {
            "name": name,
            "age": age,
            "gender": gender,
            "goals": selected_goals,
            "diet": selected_diet
        }
        
        # Speichern in eine JSON-Datei
        with open("profile_data.json", "w") as f:
            json.dump(profile_data, f)
        
        st.success(f"Thank you, {name}! Your profile has been created.")
        st.balloons()

        # Weiterleitung nach kurzer Verzögerung
        with st.spinner("Redirecting to your profile view..."):
            time.sleep(2)
        st.switch_page("pages/profile_view.py")
