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
    st.error("Bild 'image.png' nicht gefunden. Bitte stelle sicher, dass es im selben Ordner wie profile.py liegt.")
    st.stop()

# Design der Seite
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap');

.stApp {
    background: linear-gradient(160deg, #0e3e22, #a9dfbf);
    background-attachment: fixed;
    background-size: cover;
    height: 100vh;
    font-family: 'Roboto', sans-serif;
    position: relative;
}
.title-container {
    min-height: 80vh;
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
.subtitle-text {
    font-size: 40px;
    font-weight: 300;
    color: #e0f2f1;
    margin-top: -10px;
    margin-bottom: 40px;
}
.profile-image {
    width: 300px;
    height: 300px;
    border-radius: 50%;
    margin-bottom: 30px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.4);
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

# Titelbild und Titeltext einfügen (mit eingebettetem Bild)
st.markdown(f'''
<div class="title-container">
    <img class="profile-image" src="data:image/png;base64,{img_base64}">
    <div class="title-text">Nutri Mentor</div>
    <div class="subtitle-text">Healthy Food</div>
</div>
''', unsafe_allow_html=True)

# Button um zur Profilerstellung weiterzugehen (leicht rechtszentriert)
col1, col2, col3 = st.columns([1, 0.3, 1])
with col2:
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    if st.button("Erstelle hier dein Profil !"):
        st.switch_page("pages/profile.py")
