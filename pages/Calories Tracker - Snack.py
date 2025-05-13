import streamlit as st
import requests
from datetime import date
from streamlit_extras.switch_page_button import switch_page  
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------------------- JSON FILE CONFIGURATION --------------------
calendar_recipes_path = "ressources/calendar_recipes.json"

def load_calendar_recipes():
    if os.path.exists(calendar_recipes_path):
        with open(calendar_recipes_path, "r") as f:
            return json.load(f)
    return []

def save_calendar_recipes(data):
    os.makedirs(os.path.dirname(calendar_recipes_path), exist_ok=True)
    with open(calendar_recipes_path, "w") as f:
        json.dump(data, f, indent=4)

# Initialize global state
if "saved_meals" not in st.session_state:
    st.session_state.saved_meals = load_calendar_recipes()

# -------------------- STYLES CSS --------------------
with open("ressources/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# -------------------- PAGE TITLE --------------------
# Display the main title and subtitle of the page
st.markdown('<p class="title">Snack Nutrition Tracker</p>', unsafe_allow_html=True)
st.markdown(f'<div class="description">Enter a food item and its quantity to calculate your daily nutritional intake. Nutri Mentor analyzes calories, proteins, fats, and carbohydrates instantly, helping you make informed dietary choices every day.</p>', unsafe_allow_html=True)


if st.button("Go Back to Calorie Tracker", key="go_back_button"):
    switch_page("Calories Tracker")

# -------------------- LINE SEPARATOR --------------------
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) 

# -------------------- CALENDAR --------------------
st.markdown("<div style='text-align: center;'><h2 class='subtitle'>📅 Select the Day for Your Snacks's Entries</h2></div>", unsafe_allow_html=True)
selected_date = st.date_input("Select a date for your meal:", value=date.today(), min_value=date(2000, 1, 1), max_value=date(2100, 12, 31))
date_key = selected_date.strftime("%Y-%m-%d")

# -------------------- USDA API --------------------
API_KEY = os.getenv("API_KEY_USDA")

def fetch_food_data(query):
    if not API_KEY:
        st.error("API key not found. Please check your .env file.")
        return None

    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"api_key": API_KEY, "query": query, "pageSize": 1}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching data from USDA API.")
        return None

# -------------------- LOAD USER PREFERENCES --------------------
def load_user_preferences():
    try:
        with open('ressources/profile_data.json', 'r') as f:
            data = json.load(f)
            goal = data.get("goal")  # Get the goal exactly as it is in the file
            diet = data.get("diet")  # Get the diet exactly as it is in the file
            return {"goal": goal, "diet": diet}
    except FileNotFoundError:
        return {"goal": None, "diet": None}  # Return None if the file is not found

# Get user preferences
user_prefs = load_user_preferences()
user_goal = user_prefs.get("goal", "just eat Healthier :)")  # Default to "just eat Healthier :)"

# Define maximum values for each goal
goals = {
    "Build Muscle": {"calories": 2700, "protein": 180, "carbs": 350, "fat": 80},
    "Lose Weight": {"calories": 1700, "protein": 135, "carbs": 300, "fat": 40},
    "just eat Healthier :)": {"calories": 2200, "protein": 100, "carbs": 275, "fat": 70},
}

# Get max values for the user's goal
max_values = goals.get(user_goal, {"calories": 2200, "protein": 100, "carbs": 275, "fat": 70})

# -------------------- FOOD INPUT --------------------
st.markdown("<h2 class='subtitle' style='text-align: center; color: green;'>🍫 Search for Food Items</h2>", unsafe_allow_html=True)

food_query = st.text_input("Search for a food", placeholder="E.g. Protein Bar Almonds, Yogurt")
quantity = st.number_input(    "Enter the consumed quantity (in grams or ml):",     min_value=1,     value=100,     step=1)

if "totals" not in st.session_state:
    st.session_state.totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}

# -------------------- ADD FOOD BUTTON --------------------
if st.button("Add Food"):
    if food_query:
        data = fetch_food_data(food_query)
        if data:
            foods = data.get("foods", [])[:1]
            for food in foods:
                nutrients = {n['nutrientName']: n['value'] for n in food.get("foodNutrients", [])}
                calories = nutrients.get('Energy', 0) * (quantity / 100)
                protein = nutrients.get('Protein', 0) * (quantity / 100)
                fat = nutrients.get('Total lipid (fat)', 0) * (quantity / 100)
                carbs = nutrients.get('Carbohydrate, by difference', 0) * (quantity / 100)

                # Update session totals
                st.session_state.totals["calories"] += calories
                st.session_state.totals["protein"] += protein
                st.session_state.totals["fat"] += fat
                st.session_state.totals["carbs"] += carbs

              # Create the new meal
                new_entry = {
                    "recipe_title": food.get('description').capitalize(),
                    "selected_date": date_key,
                    "meal_category": "Snack",
                    "nutrition": {
                        "calories": round(calories, 2),
                        "carbohydrates": round(carbs, 2),
                        "fat": round(fat, 2),
                        "protein": round(protein, 2)
                    }
                }

                # Save to session
                st.session_state.saved_meals.append(new_entry)

                # Save to JSON file
                save_calendar_recipes(st.session_state.saved_meals)

                st.success(f"Added {new_entry['recipe_title']} to {date_key}!")

# -------------------- LINE SEPARATOR --------------------
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) 

# -------------------- RESULTS SECTION --------------------
st.markdown("<h2 class='subtitle' style='text-align: center; color: green;'>📊 Total Nutritional Values</h2>", unsafe_allow_html=True)

# Filter meals for the selected date
meals_today = [m for m in st.session_state.saved_meals if m["selected_date"] == date_key and m["meal_category"] == "Snack"]

# Display total nutritional values
if meals_today:
    meal_names = [m["recipe_title"] for m in meals_today]
    selected_meal_name = st.selectbox("Select a saved meal to view its nutritional values:", meal_names)

    selected_meal = next(m for m in meals_today if m["recipe_title"] == selected_meal_name)
    nutrition = selected_meal["nutrition"]

    # Display nutritional information
    with st.expander("View Nutritional Information"):
        st.write(f"- **Calories**: {nutrition['calories']} kcal")
        st.write(f"- **Protein**: {nutrition['protein']} g")
        st.write(f"- **Fat**: {nutrition['fat']} g")
        st.write(f"- **Carbohydrates**: {nutrition['carbohydrates']} g")

    # Display the nutritional values in a bar chart
    with st.expander("Show Total Nutritional Information"):
        total_calories = sum(m["nutrition"]["calories"] for m in meals_today)
        total_protein = sum(m["nutrition"]["protein"] for m in meals_today)
        total_fat = sum(m["nutrition"]["fat"] for m in meals_today)
        total_carbs = sum(m["nutrition"]["carbohydrates"] for m in meals_today)

    # Display total nutritional information
        st.write("### Total Nutritional Information:")
        st.write(f"- **Total Calories**: {total_calories:.2f} kcal")
        st.write(f"- **Total Protein**: {total_protein:.2f} g")
        st.write(f"- **Total Fat**: {total_fat:.2f} g")
        st.write(f"- **Total Carbohydrates**: {total_carbs:.2f} g")

    # Bar chart for nutritional values
        nutrients = ['Carbohydrates', 'Proteins', 'Fats']
        values = [total_carbs, total_protein, total_fat]
        max_values_list = [max_values["carbs"], max_values["protein"], max_values["fat"]]
        colors = ["#4caf50", "#2196f3", "#ff9800"]

        for nutrient, value, max_value, color in zip(nutrients, values, max_values_list, colors):
            bar_color = color if value <= max_value else "#ff5252"
            st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <strong>{nutrient}</strong>
                    <div style="background-color: #e0e0e0; border-radius: 5px; overflow: hidden; height: 20px; width: 100%;">
                        <div style="background-color: {bar_color}; width: {min(value / max_value * 100, 100)}%; height: 100%;"></div>
                    </div>
                    <span>{value:.2f} / {max_value} g</span>
                </div>
            """, unsafe_allow_html=True)

     # Button to delete breakfast meals
    if st.button("🗑️ Delete all snack meals for this date"):
        st.session_state.saved_meals = [
            m for m in st.session_state.saved_meals
            if not (m["selected_date"] == date_key and m["meal_category"] == "Snack")
        ]
        save_calendar_recipes(st.session_state.saved_meals)
        st.success("Meals deleted!")

        # Simulate a page refresh
        st.experimental_rerun()
else:
    st.info("No meals saved for this date.")


#   -------------------- LINE SEPARATOR --------------------
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# -------------------- NAVIGATION BUTTONS--------------------  
st.markdown("<h2 class='subtitle' style='text-align: center; color: green;'>🍽️ Navigate to Other Meals</h2>", unsafe_allow_html=True)

col1, col2, col3= st.columns(3)
   
with col1:
    if st.button("☕ Breakfast"):
        st.switch_page("pages/Calories Tracker - Breakfast.py")

with col2:
    if st.button("🥗 Lunch"):
        st.switch_page("pages/Calories Tracker - Lunch.py")

with col3:
    if st.button("🍝 Dinner"):
        st.switch_page("pages/Calories Tracker - Dinner.py")


# Sidebar ausblenden
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)