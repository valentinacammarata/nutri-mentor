import streamlit as st
import base64
import os

# Konfiguration der Streamlit-Seite
st.set_page_config(page_title='Nutri Mentor', layout='wide')

# Funktion um das Bild zu laden und als Base64 einzubetten (aus aktuellem Verzeichnis)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Lokales Bild (im gleichen Ordner wie profile.py)
image_path = "images/image.png"
if os.path.isfile(image_path):
    img_base64 = get_base64_of_bin_file(image_path)
else:
    st.error("Bild 'image.png' nicht gefunden. Bitte stelle sicher, dass es im Ordner 'images' liegt.")
    st.stop()

# Gruppenbild für den Willkommensteil
group_image_path = "images/Group_image.png"
if os.path.isfile(group_image_path):
    group_base64 = get_base64_of_bin_file(group_image_path)
else:
    st.warning("Gruppenbild nicht gefunden. Stelle sicher, dass 'Group_image.png' im Ordner 'images' liegt.")
    group_base64 = ""

# Design der Seite
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap');

.stApp {
    background: linear-gradient(160deg, #0e3e22, #a9dfbf);
    background-attachment: fixed;
    background-size: cover;
    min-height: 100vh;
    font-family: 'Roboto', sans-serif;
    position: relative;
}
.title-container {
    min-height: 70vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    text-shadow: 2px 2px 10px rgba(0,0,0,0.6);
}
.title-text {
    font-size: 100px;
    font-weight: bold;
    margin-bottom: 10px;
}
.profile-image {
    width: 300px;
    height: 300px;
    border-radius: 50%;
    margin-bottom: 30px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.4);
}
.scroll-down {
    margin-top: 20px;
    font-size: 30px;
    animation: bounce 2s infinite;
    color: #27ae60;
    text-decoration: none;
}
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(10px); }
}
.footer {
    text-align: center;
    color: #c8f7c5;
    font-size: 14px;
    margin-top: 80px;
    padding-bottom: 20px;
}
.stButton > button {
    background-color: #27ae60;
    color: white;
    padding: 1.00em 2em;
    font-size: 18px;
    border: none;
    border-radius: 10px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    transition: 0.5s ease;
    cursor: pointer;
}
.stButton > button:hover {
    background-color: #1e8449;
    transform: scale(1.05);
}
</style>
''', unsafe_allow_html=True)

# Titelbereich
st.markdown(f'''
<div class="title-container">
    <img class="profile-image" src="data:image/png;base64,{img_base64}">
    <div class="title-text">Nutri Mentor</div>
    <a href="#bottom" class="scroll-down">↓</a>
</div>
''', unsafe_allow_html=True)

# Willkommensbereich mit Text und Comicbild
if group_base64:
    st.markdown(f"""
    <div style='text-align: center; margin-top: -40px;'>
        <h2 style='color: white; font-size: 42px;'>Welcome to Nutri Mentor!</h2>
        <p style='color: white; font-size: 26px; max-width: 900px; margin: 20px auto;'>
        We are a team of four passionate students who created Nutri Mentor with a vision: to help people achieve a healthy lifestyle through personalized nutrition guidance. With this tool, you can set your health goals, get meal suggestions tailored to your preferences, and track your progress – all in one place. Let’s work together on building sustainable habits and reaching your full potential.
        </p>
        <img src="data:image/png;base64,{group_base64}" style='width: 80%; max-width: 800px; margin-top: 80px; margin-bottom: 60px; border-radius: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.4);'>
    </div>
    """, unsafe_allow_html=True)

# Button um zur Profilerstellung weiterzugehen
col1, col2, col3 = st.columns([1, 0.3, 1])
with col2:
    st.markdown("<div style='display: flex; justify-content: center; margin-top: 60px;'>", unsafe_allow_html=True)
    if st.button("CREATE YOUR FREE PROFILE!"):
        st.switch_page("pages/profile.py")

# Fußzeile mit Ankerziel für Pfeil oben
st.markdown("""
<div id="bottom"></div>
<div class="footer" style="margin-top: 120px;">
    Created by Team Nutri • 2025 • Made with ❤️
</div>
<style>
.scroll-down {
    color: #27ae60 !important; /* Change arrow color to green */
    display: block;
    text-align: center; /* Center the arrow */
}
.scroll-down::after {
    content: " create your profile !";
    display: block;
    font-size: 14px;
    color: #27ae60;
    margin-top: 5px;
    text-align: center; /* Center the text */
}
</style>
""", unsafe_allow_html=True)

# Add spacing below the welcome text and move everything after the arrow further down, Text hatte zu wenig Abstand
st.markdown("""
<style>
h2 {
    margin-bottom: 80px; /* Add more space below the welcome text */
}
.scroll-down {
    margin-top: 20px; /* Keep the arrow position */
}
div[style*='text-align: center; margin-top: -40px;'] {
    margin-top: 100px !important; /* Move the welcome section further down */
}
.stButton > button {
    margin-top: 120px; /* Move the button further down */
}
.footer {
    margin-top: 200px; /* Move the footer further down */
}
</style>
""", unsafe_allow_html=True)
