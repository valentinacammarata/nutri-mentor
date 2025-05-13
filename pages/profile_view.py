import streamlit as st
import datetime
import json
import os
# === Seitenkonfiguration muss als Erstes kommen ===
st.set_page_config(page_title="Your Profile", layout="centered")

active_page = "Profile"  # ⚠️ <- hier anpassen: z. B. "Visual Data", "Recipes", "Calories"

# CSS für gleiches Button-Styling
st.markdown(f"""
    <style>
        .nav-container {{
            display: flex;
            justify-content: center;
            gap: 1.2rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }}
        .stButton > button {{
            background-color: #388e3c !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.2rem !important;
            border: none !important;
        }}
        .active-button > button {{
            background-color: white !important;
            color: #388e3c !important;
            border: 2px solid #388e3c !important;
        }}
    </style>
""", unsafe_allow_html=True)

# Navigation zentriert mit switch_page
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if active_page == "Profile":
        st.markdown('<div class="active-button">', unsafe_allow_html=True)
    else:
        st.markdown('<div>', unsafe_allow_html=True)
    if st.button("👤 Profile"):
        st.switch_page("pages/profile_view.py")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if active_page == "Visual Data":
        st.markdown('<div class="active-button">', unsafe_allow_html=True)
    else:
        st.markdown('<div>', unsafe_allow_html=True)
    if st.button("📊 Visual Data"):
        st.switch_page("pages/data_visualization.py")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    if active_page == "Recipes":
        st.markdown('<div class="active-button">', unsafe_allow_html=True)
    else:
        st.markdown('<div>', unsafe_allow_html=True)
    if st.button("🥗 Recipes"):
        st.switch_page("pages/Recipes Generator.py")
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    if active_page == "Calories":
        st.markdown('<div class="active-button">', unsafe_allow_html=True)
    else:
        st.markdown('<div>', unsafe_allow_html=True)
    if st.button("📒 Calories"):
        st.switch_page("pages/Calories Tracker.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# Stildefinitionen
st.markdown("""
    <style>
        .stApp { background-color: #d4edda; }
        h1, h2, h3, p, label, .stMetricValue, .stMetricLabel { color: black; }
        .stButton>button { background-color: #388e3c; color: white; border-radius: 8px; }
        .section-box {
            background-color: #ffffffcc;
            padding: 25px;
            margin-top: 40px;
            border-radius: 10px;
            border: 1px solid #388e3c;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        }
        .section-title {
            text-align: center;
            margin-bottom: 20px;
        }
        .main-title {
            text-align: center;
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 40px;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            margin-bottom: 20px;
        }
        hr.centered {
            border: 1px solid black;
            width: 80%;
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Begrüßung
st.markdown("""
    <div class='main-title'>🌟 Welcome to Your Nutri Dashboard 🌟</div>
    <div class='subtitle'>Here you can view your profile, track your progress, and calculate your BMI.</div>
    <hr class='centered'>
""", unsafe_allow_html=True)

# gespeicherte Profildaten laden
if os.path.exists("ressources/profile_data.json"):
    with open("ressources/profile_data.json", "r") as f:
        profile_data = json.load(f)
else:
    st.error("No profile data found. Please create your profile first.")
    st.stop()



st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

# Profilübersicht
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
st.markdown("<h2 class='section-title'>👤 Profile Overview</h2>", unsafe_allow_html=True)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Name", profile_data.get("name", "N/A"))
        st.metric("Age", profile_data.get("age", "N/A"))
        st.metric("Gender", profile_data.get("gender", "N/A"))
    with col2:
        goals = ", ".join(profile_data.get("goals", []))
        st.metric("Goal(s)", goals if goals else "N/A")
        st.metric("Diet", profile_data.get("diet", "N/A"))
    st.markdown("</div>", unsafe_allow_html=True)



st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

# Gewichtstracker
st.markdown("<h2 class='section-title'>🏋️ Weight Tracker</h2>", unsafe_allow_html=True)
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center; font-size: 16px; color: black;'>
        Keep track of your progress by logging your weight.<br>
        Enter your current weight below to update your profile and monitor changes over time.
    </p>
""", unsafe_allow_html=True)

with st.container():
    date = st.date_input("🗓️ Select Date", datetime.date.today())
    weight = st.number_input("Your Current Weight (kg)", min_value=30.0, max_value=200.0, step=0.5)

    if st.button("Log Weight"):
        profile_data["weight"] = float(weight)
        profile_data["date"] = str(date)
        with open("ressources/profile_data.json", "w") as f:
            json.dump(profile_data, f)
        st.success(f"Weight of {weight} kg logged for {date}.")

# Gewichtsanalyse Navigation direkt dort hin
st.markdown("<h3 style='text-align: center;'>📈 Full Weight Analysis</h3>", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center; font-size: 16px;'>
        Here you can view your full weight history and track important trends over time.
    </p>
""", unsafe_allow_html=True)

# Zentrierter Button in der Mitte
centered_col = st.columns(3)[1]
with centered_col:
    if st.button("🔍 Go to Weight Dashboard"):
        st.switch_page("pages/data_visualization.py")


st.markdown("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
# BMI Rechner
st.markdown("<h2 class='section-title'>📊 Calculate your BMI</h2>", unsafe_allow_html=True)
st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center; font-size: 16px; color: black;'>
        We also created a cool little tool for you :)<br>
        The Body Mass Index (BMI) is a simple calculation used to assess whether your weight is in a healthy range 
        based on your height. Enter your details below to find out your BMI and what it means for your health.
    </p>
""", unsafe_allow_html=True)
st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
with st.container():
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
    st.markdown("</div>", unsafe_allow_html=True)


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

st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

# Dashboard Navigation
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>🧭 Dashboard Navigation</h3>", unsafe_allow_html=True)

# Custom CSS für Buttons + Text
st.markdown("""
    <style>
        .dashboard-block {
            text-align: left; /* Align content to the left */
        }
        .dashboard-button {
            padding: 16px 40px;
            font-size: 20px;
            font-weight: bold;
            background-color: #388e3c;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            display: inline-block;
            margin: auto;
        }
        .dashboard-button:hover {
            background-color: #2e7d32;
        }
        .dashboard-desc {
            font-size: 17px;
            margin-top: 12px;
            color: #333333;
            text-align: left; /* Align text to the left */
        }
    </style>
""", unsafe_allow_html=True)

# Drei Spalten
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='dashboard-block'>", unsafe_allow_html=True)
    if st.button("📊 Data View", key="data_view"):
        st.switch_page("pages/data_visualization.py")
    st.markdown("<div class='dashboard-desc'>Track your weight data and monitor your progress visually.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='dashboard-block'>", unsafe_allow_html=True)
    if st.button("🥗 Recipes Generator", key="meal_plan"):
        st.switch_page("pages/Recipes Generator.py")
    st.markdown("<div class='dashboard-desc'>Explore our most exciting tool: intelligent recipe search based on your profile!</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='dashboard-block'>", unsafe_allow_html=True)
    if st.button("🔥 Calorie Tracker", key="calo_tracker"):
        st.switch_page("pages/Calories Tracker.py")
    st.markdown("<div class='dashboard-desc'>Use the calorie tracker to manage your nutritional intake precisely.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


    # Footer
st.markdown("""
<div id="bottom"></div>
<div class="footer" style="margin-top: 120px;">
    Created by Team Nutri • 2025 • Made with ❤️
</div>
""", unsafe_allow_html=True)
