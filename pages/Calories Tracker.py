import streamlit as st
import datetime
from streamlit_extras.switch_page_button import switch_page
import calendar
import matplotlib.pyplot as plt
import json

# -------------------- CONFIGURATION --------------------
# Set the page title and layout
st.set_page_config(page_title="Dashboard", layout="centered")


# -------------------- CSS STYLES --------------------
# Load custom CSS styles from a file
with open("ressources/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------- PAGE TITLE --------------------
# Display the main title and subtitle of the page
st.markdown("""
    <div class='title'><em>Welcome to Your Daily Dashboard</em></div>
    <div class='subtitle'><em>Manage your diet more intelligently, effortlessly track your caloric intake, and gain deeper insights into your daily nutritional progress. NutriMentor empowers you to stay consistent, make informed food choices, and achieve your health goals with confidence and ease.</em></div>
""", unsafe_allow_html=True)

# Add custom CSS styles for the page
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body {
            background-color: #f8f9fa;
            font-family: 'Inter', sans-serif;
        }
        .dashboard-container {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px auto;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            max-width: 800px;
        }
        .title {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 5px;
            color: #333;
        }
        .subtitle {
            font-size: 18px;
            text-align: center;
            margin-bottom: 20px;
            color: #666;
        }
        .circle-container {
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: conic-gradient(#4caf50 75%, #e0e0e0 0%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            position: relative;
        }
        .circle-text {
            font-size: 32px;
            font-weight: bold;
            color: #333;
            text-align: center;
        }
        .kcal-label {
            font-size: 14px;
            color: #666;
        }
        .stats-row {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }
        .stats-text {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            text-align: center;
        }
        .label-text {
            font-size: 14px;
            color: #666;
            text-align: center;
        }
        .progress-bar {
            height: 8px;
            border-radius: 5px;
            background-color: #e0e0e0;
            margin-top: 5px;
        }
        .progress {
            height: 100%;
            border-radius: 5px;
            background-color: #4caf50;
        }
        .dashboard-box {
            background-color: #fff;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .dashboard-title {
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .dashboard-stats {
            display: flex;
            justify-content: space-around;
            text-align: center;
        }
        .stat-item {
            font-size: 16px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)


st.markdown("""
    <style>
        .custom-scroll-button {
            display: inline-block;
            background-color: #3E8E41;
            color: white;
            padding: 10px 24px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 500;
            text-decoration: none;
            transition: background-color 0.2s ease;
        }
        .custom-scroll-button:hover {
            background-color: #2e6f32;
        }
    </style>

    <div style="text-align: center; margin-top: 25px;">
        <a href="#manual-entry" class="custom-scroll-button">⬇️ Go to Manual Food Entry</a>
    </div>
""", unsafe_allow_html=True)
# -------------------- LINE SEPARATOR --------------------
# Add a horizontal line separator
st.markdown("""
    <style>
        .separator-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        .separator {
            border: none;
            border-top: 2px solid #3E8E41;
            width: 50%;
        }
    </style>
    <div class="separator-container">
        <hr class='separator'>
    </div>
""", unsafe_allow_html=True)

# -------------------- DASHBOARD --------------------
if "selected_day" in st.session_state:
    selected_day = st.session_state.selected_day
    selected_date = datetime.datetime(
        st.session_state.calendar_year,
        st.session_state.calendar_month,
        selected_day
    ).strftime("%A, %d %B %Y")
    st.markdown(f"""
        <div class='title'><em>Today's Overview</em></div>
        <div class='subtitle'><em>{selected_date}</em></div>
    """, unsafe_allow_html=True)
else:
    today = datetime.datetime.now().strftime("%A, %d %B %Y")
    st.markdown(f"""
        <div class='title'><em>Today's Overview</em></div>
        <div class='subtitle'><em>{today}</em></div>
    """, unsafe_allow_html=True)

# -------------------- TOTAL NUTRITIONAL INFORMATION --------------------
# Carica i dati dal file JSON
def load_calendar_recipes():
    try:
        with open("ressources/calendar_recipes.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

calendar_recipes = load_calendar_recipes()

# Seleziona una data per visualizzare i totali
selected_date = st.date_input("Select a date to view totals:", value=datetime.datetime.now().date())
selected_date_str = selected_date.strftime("%Y-%m-%d")

# Filtra i pasti per la data selezionata
meals_today = [meal for meal in calendar_recipes if meal["selected_date"] == selected_date_str]

# Calcola i totali per la data selezionata
totals = {
    "calories": sum(meal["nutrition"]["calories"] for meal in meals_today),
    "protein": sum(meal["nutrition"]["protein"] for meal in meals_today),
    "fat": sum(meal["nutrition"]["fat"] for meal in meals_today),
    "carbs": sum(meal["nutrition"]["carbohydrates"] for meal in meals_today),
}

# Mostra i totali in un layout a scheda
st.markdown(f"""
<div class="dashboard-box">
    <div class="dashboard-title">Total Nutritional Information for {selected_date_str}</div>
    <div class="dashboard-stats">
        <div>
            <div class="stats-text">Calories</div>
            <div class="stats-value">{totals['calories']:.2f} kcal</div>
        </div>
        <div>
            <div class="stats-text">Protein</div>
            <div class="stats-value">{totals['protein']:.2f} g</div>
        </div>
        <div>
            <div class="stats-text">Fat</div>
            <div class="stats-value">{totals['fat']:.2f} g</div>
        </div>
        <div>
            <div class="stats-text">Carbohydrates</div>
            <div class="stats-value">{totals['carbs']:.2f} g</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------- BAR CHARTS FOR GOALS --------------------

# Add some spacing between sections
st.markdown("<br><br>", unsafe_allow_html=True)

# Load user preferences from profile_data.json
def load_user_preferences():
    try:
        with open('ressources/profile_data.json', 'r') as f:
            data = json.load(f)
            goals = data.get("goals", [])
            goal = goals[0] if goals else "just eat Healthier :)"
            diet = data.get("diet", "No Preference")
            return {"goal": goal, "diet": diet}
    except FileNotFoundError:
        return {"goal": "just eat Healthier :)", "diet": "No Preference"}

# Get user preferences
user_prefs = load_user_preferences()
user_goal = user_prefs.get("goal", "just eat Healthier :)")  # Default to "just eat Healthier :)"

# Define maximum values for each goal
goals = {
    "Build Muscle": {"calories": 3000, "protein": 210, "carbs": 400, "fat": 90},
    "Lose Weight": {"calories": 1900, "protein": 150, "carbs": 350, "fat": 50},
}

# Check if the user's goal is in the defined goals
if user_goal in goals:
    max_values = goals[user_goal]

    # Calculate percentages for each nutrient
    percentages = {
        "calories": min((totals["calories"] / max_values["calories"]) * 100, 100),
        "protein": min((totals["protein"] / max_values["protein"]) * 100, 100),
        "carbs": min((totals["carbs"] / max_values["carbs"]) * 100, 100),
        "fat": min((totals["fat"] / max_values["fat"]) * 100, 100),
    }

    # Create bar chart data
    labels = ["Calories", "Protein", "Carbs", "Fat"]
    values = [percentages["calories"], percentages["protein"], percentages["carbs"], percentages["fat"]]
    max_values_list = [max_values["calories"], max_values["protein"], max_values["carbs"], max_values["fat"]]

    # Plot the bar charts
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=["#4caf50", "#2196f3", "#ff9800", "#f44336"], alpha=0.8)

    # Add value labels on top of the bars
    for bar, value, max_value in zip(bars, values, max_values_list):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            f"{value:.1f}%\n({totals[labels[bars.index(bar)].lower()]:.1f}/{max_value} g)",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Customize the chart
    ax.set_ylim(0, 120)  # Allow some space above 100% for labels
    ax.set_ylabel("Percentage of Goal Reached (%)")
    ax.set_title(f"Progress Towards {user_goal} Goals")
    ax.axhline(100, color="gray", linestyle="--", linewidth=1, alpha=0.7)  # Add a line at 100%
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)

    # Display the chart in Streamlit
    st.pyplot(fig)
else:
    st.info("No goal selected or goal not supported.")

# -------------------- CIRCULAR PROGRESS CHARTS FOR GOALS --------------------

import matplotlib.pyplot as plt

# Check if the user's goal is in the defined goals
if user_goal in goals:
    max_values = goals[user_goal]

    # Calculate percentages for each nutrient
    percentages = {
        "calories": min((totals["calories"] / max_values["calories"]) * 100, 100),
        "protein": min((totals["protein"] / max_values["protein"]) * 100, 100),
        "carbs": min((totals["carbs"] / max_values["carbs"]) * 100, 100),
        "fat": min((totals["fat"] / max_values["fat"]) * 100, 100),
    }

    # Define labels, values, and colors for the circular charts
    labels = ["Calories", "Protein", "Carbs", "Fat"]
    values = [percentages["calories"], percentages["protein"], percentages["carbs"], percentages["fat"]]
    colors = ["#4caf50", "#2196f3", "#ff9800", "#f44336"]  # Green, Blue, Orange, Red

    # Create circular progress charts
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))  # Create 4 subplots side by side

    for i, ax in enumerate(axes):
        # Create a pie chart with the percentage and remaining space
        ax.pie(
            [values[i], 100 - values[i]],
            colors=[colors[i], "#e0e0e0"],  # Use the color and a light gray for the remaining
            startangle=90,
            counterclock=False,
            wedgeprops={"width": 0.3},  # Make it look like a progress ring
        )
        # Add the percentage text in the center
        ax.text(
            0, 0, f"{values[i]:.0f}%", ha="center", va="center", fontsize=16, fontweight="bold", color=colors[i]
        )
        # Add the label below the chart
        ax.set_title(labels[i], fontsize=14, pad=20)

    # Adjust layout and display the charts in Streamlit
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("No goal selected or goal not supported.")

# -------------------- LINE SEPARATOR --------------------
# Add another horizontal line separator
st.markdown("""
    <style>
        .separator-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        .separator {
            border: none;
            border-top: 2px solid #3E8E41;
            width: 50%;
        }
    </style>
    <div class="separator-container">
        <hr class='separator'>
    </div>
""", unsafe_allow_html=True)

# -------------------- CALENDAR --------------------
# Display the calendar section
st.markdown("""
    <div class='title'><em>Calendar</em></div>
    <div class='subtitle'><em>Click the day to add your entries manually</em></div>
""", unsafe_allow_html=True)

# Variables for the month and year
if "calendar_year" not in st.session_state:
    st.session_state.calendar_year = datetime.datetime.now().year
if "calendar_month" not in st.session_state:
    st.session_state.calendar_month = datetime.datetime.now().month

# Functions to change the month
def previous_month():
    if st.session_state.calendar_month == 1:
        st.session_state.calendar_month = 12
        st.session_state.calendar_year -= 1
    else:
        st.session_state.calendar_month -= 1
    st.rerun()

def next_month():
    if st.session_state.calendar_month == 12:
        st.session_state.calendar_month = 1
        st.session_state.calendar_year += 1
    else:
        st.session_state.calendar_month += 1
    st.rerun()

# Variable to store recipes
if "recipes" not in st.session_state:
    st.session_state.recipes = {}

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.button("⬅ Previous", key="prev_month", on_click=previous_month)

with col2:
    st.markdown(
        f"<h3 style='text-align: center;margin-top: 15px'>📅 {calendar.month_name[st.session_state.calendar_month]} {st.session_state.calendar_year}</h3>",
        unsafe_allow_html=True
    )

with col3:
    st.button(" Next ➡", key="next_month", on_click=next_month)

# Get the matrix of weeks
cal = calendar.Calendar(firstweekday=0)
month_days = cal.monthdayscalendar(st.session_state.calendar_year, st.session_state.calendar_month)

# Days of the week
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
cols = st.columns(7)
for idx, day in enumerate(days_of_week):
    cols[idx].markdown(f"**{day}**")

# Draw the calendar
for week in month_days:
    cols = st.columns(7)
    for idx, day in enumerate(week):
        if day == 0:
            cols[idx].markdown(" ")  # empty day
        else:
            with cols[idx]:
                if st.button(f"{day}", key=f"day_{day}_{st.session_state.calendar_month}_{st.session_state.calendar_year}"):
                    st.session_state.selected_day = day

# Display the selected day and allow adding a recipe
if "selected_day" in st.session_state:
    selected_day = st.session_state.selected_day
    selected_date_key = f"{st.session_state.calendar_year}-{st.session_state.calendar_month}-{selected_day}"

    st.markdown(f"### Selected Day: {selected_day} {calendar.month_name[st.session_state.calendar_month]} {st.session_state.calendar_year}")

    # Selettore del tipo di pasto
    meal_type = st.selectbox("Select meal type:", ["Breakfast", "Lunch", "Dinner", "Snack"])

    # Inizializza la struttura se non esiste
    if selected_date_key not in st.session_state.recipes:
        st.session_state.recipes[selected_date_key] = {}

    # Recupera ricetta esistente per il pasto selezionato
    recipe_text = st.session_state.recipes[selected_date_key].get(meal_type, "")
    recipe = st.text_area("Insert your recipe here:", recipe_text)

    if st.button("✅ Save Recipe", key="save_recipe"):
        st.session_state.recipes[selected_date_key][meal_type] = recipe
        st.success(f"{meal_type} saved for {selected_day} {calendar.month_name[st.session_state.calendar_month]} {st.session_state.calendar_year}!")

    if selected_date_key in st.session_state.recipes:
        # Display the saved recipes section
        st.markdown("""
    <div style="text-align: center; color: green;">
        <h2 class="subtitle" style="color: green;">🍽️ Saved Meals</h2>
        <p class="description" style="color: green;">
            View and manage your saved recipes for each day. Keep track of your favorite meals and plan your diet effortlessly.
        </p>
    </div>
""", unsafe_allow_html=True)
        
    

    meal_emojis = {
        "Breakfast": "☕",
        "Lunch": "🥗",
        "Dinner": "🍝",
        "Snack": "🍫"
    }

    for meal in ["Breakfast", "Lunch", "Dinner", "Snack"]:
        if meal in st.session_state.recipes[selected_date_key]:
            content = st.session_state.recipes[selected_date_key][meal]
            st.markdown(f"**{meal_emojis[meal]} {meal}:** {content}")

    filtered_recipes = {
        date_key: recipe for date_key, recipe in st.session_state.recipes.items()
        if len(date_key.split('-')) == 3 and date_key.split('-')[1].isdigit() and date_key.split('-')[0].isdigit()
        and int(date_key.split('-')[1]) == st.session_state.calendar_month and int(date_key.split('-')[0]) == st.session_state.calendar_year
    }

    if filtered_recipes:
        # Create a dropdown menu with days that have saved recipes
        selected_date = st.selectbox(
            "Select a day to view the saved recipe:",
            options=sorted(filtered_recipes.keys()),
            format_func=lambda x: f"Day {x.split('-')[2]} {calendar.month_name[int(x.split('-')[1])]} {x.split('-')[0]}"
        )

        # Display the saved recipes for the selected date
        st.markdown(f"### Recipes for {selected_date.split('-')[2]} {calendar.month_name[int(selected_date.split('-')[1])]} {selected_date.split('-')[0]}")

        meal_emojis = {
            "Breakfast": "☕",
            "Lunch": "🥗",
            "Dinner": "🍝",
            "Snack": "🍫"
        }

        for meal, content in filtered_recipes[selected_date].items():
            st.markdown(f"**{meal_emojis.get(meal, '')} {meal}:** {content}")
    else:
        st.info("No recipes saved for this month.")

   
# -------------------- LINE SEPARATOR --------------------
# Add another horizontal line separator
st.markdown("""
    <style>
        .separator-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        .separator {
            border: none;
            border-top: 2px solid #3E8E41;
            width: 50%;
        }
    </style>
    <div class="separator-container">
        <hr class='separator'>
    </div>
""", unsafe_allow_html=True)

# -------------------- SWITCH PAGE BUTTONS --------------------
# Titolo e descrizione centrati
st.markdown("<a name='manual-entry'></a>", unsafe_allow_html=True) #riconduce al link
st.markdown("""
    <div style="text-align: center; color: green;">
        <h2 class="subtitle">🍽️ Manual Food Entry</h2>
        <p class="description">
            Add and manage your food entries for each day. Keep track of your meals and nutritional intake manually.
        </p>
    </div>
""", unsafe_allow_html=True)

# Layout a 4 colonne per i bottoni
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("☕ Breakfast"):
        st.switch_page("pages/Calories Tracker - Breakfast.py")

with col2:
    if st.button("🥗 Lunch"):
        st.switch_page("pages/Calories Tracker - Lunch.py")

with col3:
    if st.button("🍝 Dinner"):
        st.switch_page("pages/Calories Tracker - Dinner.py")

with col4:
    if st.button("🍫 Snack"):
        st.switch_page("pages/Calories Tracker - Snack.py")