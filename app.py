import streamlit as st
import pandas as pd
from datetime import datetime

# Muss als erstes Streamlit-Kommando stehen
st.set_page_config(page_title="Gewichtstracker", layout="centered")

# Titel
st.title("NutriMentor")
st.subheader("📉 Weight Tracker")
st.write("Trage bis zu 5 Gewichte auf einmal ein und sieh deinen Fortschritt.")

# Dateipfad
DATA_FILE = "gewichtsdaten.csv"

# Lade Daten oder erzeuge leere Tabelle
def load_data():
    try:
        return pd.read_csv(DATA_FILE, parse_dates=["Datum"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Datum", "Gewicht"])

# Speichern
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Eingabe: bis zu 5 Werte
st.header("➕ Gewichtseingaben (max. 5)")
gewichtsdaten = []

for i in range(5):
    col1, col2 = st.columns(2)
    with col1:
        gewicht = st.number_input(f"{i+1}. Gewicht (kg)", min_value=30.0, max_value=300.0, step=0.1, key=f"gewicht_{i}")
    with col2:
        datum = st.date_input(f"{i+1}. Datum", value=datetime.today().date(), key=f"datum_{i}")
    
    # Nur speichern, wenn ein Gewicht eingegeben wurde
    if gewicht > 0:
        gewichtsdaten.append({"Datum": datum, "Gewicht": gewicht})

# Speichern-Button
if st.button("💾 Alle speichern"):
    if len(gewichtsdaten) == 0:
        st.warning("Bitte gib mindestens ein Gewicht ein.")
    else:
        df = load_data()
        neue_eintraege = pd.DataFrame(gewichtsdaten)
        df = pd.concat([df, neue_eintraege], ignore_index=True)
        df = df.drop_duplicates(subset=["Datum"], keep="last")  # Pro Datum nur 1 Eintrag
        save_data(df)
        st.success(f"{len(gewichtsdaten)} Einträge gespeichert! ✅")

# Visualisierung
st.header("📊 Verlauf anzeigen")
df = load_data()

if not df.empty:
    zeitraum = st.selectbox("Zeitraum wählen", ["Alle", "Letzte 7 Tage", "Letzte 30 Tage"])

    if zeitraum == "Letzte 7 Tage":
        df = df[df["Datum"] >= pd.Timestamp.today() - pd.Timedelta(days=7)]
    elif zeitraum == "Letzte 30 Tage":
        df = df[df["Datum"] >= pd.Timestamp.today() - pd.Timedelta(days=30)]

    df = df.sort_values("Datum")

    st.subheader("📈 Gewicht über Zeit")
    st.line_chart(df.set_index("Datum")["Gewicht"])

    st.subheader("📋 Tabelle")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Noch keine Daten vorhanden. Gib etwas ein, um zu starten.")
