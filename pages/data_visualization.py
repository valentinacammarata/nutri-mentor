import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestRegressor  #für Machine Learning

active_page = "Data Visualization"  # Aktive Seite für die Navigation

# CSS für gleiches Button-Styling
st.markdown(f"""
    <style>
        .nav-container {{
            display: flex;
            justify-content: center;
            gap: 2rem; /* This defines the spacing between the buttons */
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

# Add text below the weight input
st.markdown("""
    <p style='text-align: center; font-size: 1em; color: #2f5732;'>
        Please ensure the weight and date are accurate before saving.<br>
        ! The machine learning tool will be available once you have entered at least 3 weight entries !
    </p>
""", unsafe_allow_html=True)

if st.button("➕ Add another row"):
    st.session_state.weight_rows += 1
    st.rerun()

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

st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
    # === MACHINE LEARNING VORHERSAGE: GEWICHTSPROGNOSE FÜR 30 TAGE ===
if len(df) >= 5:
            st.subheader("🤖 Weight Forecast")
            st.markdown("""
            <p style='text-align: center; font-size: 1.05em; color: #2f5732;'>
            This section uses a machine learning model (Random Forest Regression) to forecast your weight for the next days based on your recent history.<br>
            It uses the last 3 entries and their average as predictors. The more data you enter, the more accurate this prediction becomes.
            </p>
            """, unsafe_allow_html=True)
            forecast_days = st.slider("Forecast range (days)", min_value=7, max_value=30, value=30, step=1)
            
            df_ml = df.copy()
            df_ml["Weight_lag1"] = df_ml["Weight"].shift(1)
            df_ml["Weight_lag2"] = df_ml["Weight"].shift(2)
            df_ml["Weight_lag3"] = df_ml["Weight"].shift(3)
            df_ml["Weight_avg"] = df_ml[["Weight_lag1", "Weight_lag2", "Weight_lag3"]].mean(axis=1)
            df_ml = df_ml.dropna()

            X = df_ml[["Weight_lag1", "Weight_lag2", "Weight_lag3", "Weight_avg"]]
            y = df_ml["Weight"]

            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)

            last_known_w1 = df["Weight"].iloc[-1]
            last_known_w2 = df["Weight"].iloc[-2] if len(df) >= 2 else last_known_w1
            last_known_w3 = df["Weight"].iloc[-3] if len(df) >= 3 else last_known_w2
            predictions = []

            for _ in range(forecast_days):
                avg = np.mean([last_known_w1, last_known_w2, last_known_w3])
                features = [[last_known_w1, last_known_w2, last_known_w3, avg]]
                next_pred = model.predict(features)[0]
                predictions.append(next_pred)
                last_known_w3, last_known_w2, last_known_w1 = last_known_w2, last_known_w1, next_pred

            max_date = pd.to_datetime(df["Date"].max(), errors="coerce")
            if pd.notna(max_date):
                future_dates = pd.date_range(pd.to_datetime(max_date) + pd.Timedelta(days=1), periods=forecast_days)
                forecast_df = pd.DataFrame({"Date": future_dates, "Predicted Weight": predictions})

                st.markdown(f"📅 **{forecast_days}-Day Weight Forecast**")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(pd.to_datetime(df["Date"], errors="coerce"), df["Weight"], label="Actual Weight", marker='o')
                ax.plot(pd.to_datetime(forecast_df["Date"], errors="coerce"), forecast_df["Predicted Weight"], label="Forecast", linestyle='--', marker='x', color='orange')
                ax.set_xlabel("Date")
                ax.set_ylabel("Weight (kg)")
                ax.set_title(f"Weight Forecast (Next {forecast_days} Days)")
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)

                if len(df) < 30:
                    st.info("ℹ️ Your prediction may be unstable. For more accurate forecasts, it's recommended to have at least 30 data entries.")

                with st.expander("🔍 Show forecasted values"):
                    st.dataframe(forecast_df, use_container_width=True)
            else:
                st.warning("❗ Date column is missing or invalid, forecast could not be generated.")

# ================= ADVANCED BODY COMPOSITION SECTION =================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <h1 style='text-align: center;'>Advanced Body Composition Tracking</h1>
    <p style='text-align: center; font-size: 1.05em; color: #2f5732;'>
        This tool is designed for individuals who have access to advanced body composition scales or devices. <br>
        These specialized scales provide detailed metrics such as body fat percentage, muscle mass, and water content, 
        offering a comprehensive view of your physical health. By using this tool, you can log and visualize these metrics 
        over time, enabling you to track progress, identify trends, and make informed decisions about your fitness and health journey. 
        Whether you're an athlete, fitness enthusiast, or someone looking to improve their overall well-being, 
        this tool empowers you to take control of your body composition data and achieve your goals.
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

    st.markdown("""
<p style='text-align: center; font-size: 0.95em; color: #444;'>
<b>Other</b> represents the remaining components of your body not captured by fat, muscle, or water. 
This may include bones, organs, and other tissues. If your input values do not add up to 100%, 
"Other" fills in the difference to complete the total body composition.
</p>
""", unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center;'>📊 Single Entry Overview</h3>", unsafe_allow_html=True)
    fig_bar, ax_bar = plt.subplots()
    categories = ['Body Fat', 'Muscle Mass', 'Water Content']
    values = [bf, mm, wc]
    bars = ax_bar.bar(categories, values, color=colors[:3])
    ax_bar.set_ylabel("Percentage")

    # Add value annotations on top of the bars
    for bar in bars:
        height = bar.get_height()
        ax_bar.annotate(f'{height:.1f}%', 
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # Offset text by 3 points above the bar
                        textcoords="offset points",
                        ha='center', va='bottom')

    st.pyplot(fig_bar)

# === MEHRERE EINTRÄGE MÖGLICH NACH DER ERSTEN EINGABE ===
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
st.subheader("📥 Add More Entries")
st.markdown("""
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
    bars_bf = ax2.bar(x - bar_width, last_entries["Body Fat"], width=bar_width, label="Body Fat", color="#f4a261")
    bars_mm = ax2.bar(x, last_entries["Muscle Mass"], width=bar_width, label="Muscle Mass", color="#2a9d8f")
    bars_wc = ax2.bar(x + bar_width, last_entries["Water Content"], width=bar_width, label="Water Content", color="#264653")

    ax2.set_xlabel("Date")
    ax2.set_ylabel("Percentage")
    ax2.set_title("Recent Body Composition Entries")
    ax2.set_xticks(x)
    ax2.set_xticklabels(dates)
    ax2.legend()

    # Add value annotations on top of the bars
    for bars in [bars_bf, bars_mm, bars_wc]:
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f'{height:.1f}%', 
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3),  # Offset text by 3 points above the bar
                         textcoords="offset points",
                         ha='center', va='bottom')

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