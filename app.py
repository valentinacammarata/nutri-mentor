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

# Lokales Bild
image_path = "images/image.png"
if os.path.isfile(image_path):
    img_base64 = get_base64_of_bin_file(image_path)
else:
    st.error("Bild 'image.png' nicht gefunden. Bitte stelle sicher, dass es im Ordner 'images' liegt.")
    st.stop()

# Gruppenbild
group_image_path = "images/Group_image.png"
if os.path.isfile(group_image_path):
    group_base64 = get_base64_of_bin_file(group_image_path)
else:
    st.warning("Gruppenbild nicht gefunden. Stelle sicher, dass 'Group_image.png' im Ordner 'images' liegt.")
    group_base64 = ""

# Style & Layout
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap');

.stApp {
    background: linear-gradient(160deg, #0e3e22, #a9dfbf);
    background-attachment: fixed;
    background-size: cover;
    min-height: 100vh;
    font-family: 'Roboto', sans-serif;
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
    font-size: 30px;
    animation: bounce 2s infinite;
    color: #ffffff !important;
    text-decoration: none;
    display: block;
    text-align: center;
}
.scroll-down::after {
    content: "create your profile !";
    display: block;
    font-size: 16px;
    color: #ffffff;
    margin-top: 8px;
    text-align: center;
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
    margin-top: 40px;
}
.stButton > button:hover {
    background-color: #1e8449;
    transform: scale(1.05);
}
</style>
''', unsafe_allow_html=True)

# Header-Block
st.markdown(f'''
<div class="title-container">
    <img class="profile-image" src="data:image/png;base64,{img_base64}">
    <div class="title-text">Nutri Mentor</div>
    <a href="#bottom" class="scroll-down">↓</a>
</div>
''', unsafe_allow_html=True)

# Welcome-Bereich
if group_base64:
    st.markdown(f"""
    <div style='text-align: center; margin-top: -30px;'>
        <h2 style='color: white; font-size: 42px;'>Welcome to Nutri Mentor!</h2>
        <p style='color: white; font-size: 26px; max-width: 900px; margin: 20px auto; line-height: 1.8;'>
        We are a team of four passionate students who created Nutri Mentor with a vision:
        To help people achieve a healthy lifestyle through personalized nutrition guidance.
        With this tool, you can set your health goals, get meal suggestions tailored to your preferences,
        and track your progress – all in one place. Let’s work together on building sustainable habits
        and reaching your full potential.
        </p>
        <img src="data:image/png;base64,{group_base64}" style='width: 80%; max-width: 800px; margin-top: 80px; margin-bottom: 60px; border-radius: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.4);'>
    </div>
    """, unsafe_allow_html=True)

# Textblock zentriert über gesamter Breite (nicht in einer schmalen Column!)
st.markdown("""
<div style='text-align: center; margin-top: 60px;'>
    <p style='color: white; font-size: 18px; max-width: 900px; margin: 0 auto; line-height: 1.6;'>
    After a quick signup, you’ll be guided through creating your personalized profile.
    This will allow us to provide you with nutrition recommendations that match your lifestyle,
    health goals, and dietary preferences – all in one place.
    </p>
</div>
""", unsafe_allow_html=True)

# Button zentriert unter dem Text
col1, col2, col3 = st.columns([1, 0.3, 1])
with col2:
    if st.button("CREATE YOUR FREE PROFILE!", key="create_profile_button"):
        st.switch_page("pages/profilecreation.py")

# Footer
st.markdown("""
<div id="bottom"></div>
<div class="footer" style="margin-top: 120px;">
    Created by Team Nutri • 2025 • Made with ❤️
</div>
""", unsafe_allow_html=True)

# Sidebar ausblenden
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Code developed with the help of ChatGPT and Copilot.