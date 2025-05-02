import streamlit as st
import requests
from datetime import date
from streamlit_extras.switch_page_button import switch_page  

# -------------------- CSS STYLES --------------------
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------- TITLE AND SUB-TITLE --------------------
st.markdown("""
    <div class="title-container">
        <h1 class="title">Lunch Nutritional Tracker</h1>
        <p class="subtitle" style="font-style: italic;">
            Enter a food item and its quantity to calculate your daily nutritional intake. 
            <strong>NutriMentor</strong> analyzes calories, proteins, fats, and carbohydrates instantly, 
            helping you make informed dietary choices every day.
        </p>
    </div>
""", unsafe_allow_html=True)

if st.button("Go Back to Calorie Tracker", key="go_back_button"):
    st.switch_page("pages/calo.py")

# -------------------- LINE SEPARATOR --------------------
st.markdown("""
    <style>
        .separator-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        .separator {
            border: none;
            border-top: 4px solid #3E8E41; /* Increased thickness from 2px to 4px */
            width: 50%;
        }
    </style>
    <div class="separator-container">
        <hr class='separator'>
    </div>
""", unsafe_allow_html=True)

# -------------------- CALENDAR --------------------
# Add a centered date input widget with emojis and styled title
st.markdown("""
    <div style="text-align: center;">
        <h2 class="subtitle">📅 Select the Day for Your Breakfast Entries </h2>
    </div>
""", unsafe_allow_html=True)

# Center the date input widget
st.markdown("""
    <style>
        .date-input-container {
            display: flex;
            justify-content: center;
            margin-top: 10px;
        }
    </style>
    <div class="date-input-container">
""", unsafe_allow_html=True)

selected_date = st.date_input(
    "Select a date for your meal:",
    value=date.today(),
    min_value=date(2000, 1, 1),
    max_value=date(2100, 12, 31)
)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------- LINE SEPARATOR --------------------
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

# -------------------- FOOD SEARCH SECTION --------------------
# Title and description for the food search functionality
st.markdown("""
    <div style="text-align: center; color: green;">
        <h2 class="subtitle" style="color: green;">🍎 Search for Food Items</h2>
        <p class="description" style="color: green;">
            Enter the name of a food item and specify the quantity consumed. 
            NutriMentor will calculate the nutritional values for you.
        </p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state for saved meals
if "saved_meals" not in st.session_state:
    st.session_state.saved_meals = []

# USDA API Key
API_KEY = "aL8QBhKyNY5zMFjZioZY0yQCk8GgtHjtaBjbsMfH"

# Function to fetch nutritional data
def fetch_food_data(query):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": API_KEY,
        "query": query,
        "pageSize": 1  # Limit results to 1 item
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching data from USDA API.")
        return None

# Search bar
food_query = st.text_input("Search for a food", placeholder="E.g. Apple, Banana, Coffee")

# Input for consumed quantity
default_quantity = 100  # Default quantity in grams
quantity = st.number_input(
    "Enter the consumed quantity (in grams or ml):",
    min_value=1,
    value=default_quantity,
    step=1
)

# Initialize total nutrients in session_state if they don't exist
if "totals" not in st.session_state:
    st.session_state.totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}

# When adding a meal, update the totals
if st.button("Add Food"):
    if food_query:
        data = fetch_food_data(food_query)
        if data:
            foods = data.get("foods", [])[:1]  # Show only the first result
            for food in foods:
                # Calculate nutrients based on the quantity
                nutrients = {nutrient['nutrientName']: nutrient['value'] for nutrient in food.get("foodNutrients", [])}
                calories = nutrients.get('Energy', 0) * (quantity / default_quantity)
                protein = nutrients.get('Protein', 0) * (quantity / default_quantity)
                fat = nutrients.get('Total lipid (fat)', 0) * (quantity / default_quantity)
                carbs = nutrients.get('Carbohydrate, by difference', 0) * (quantity / default_quantity)

                # Update totals in session_state
                st.session_state.totals["calories"] += calories
                st.session_state.totals["protein"] += protein
                st.session_state.totals["fat"] += fat
                st.session_state.totals["carbs"] += carbs

                # Save the meal in the list
                st.session_state.saved_meals.append({
                    "name": food.get('description').capitalize(),
                    "calories": calories,
                    "protein": protein,
                    "fat": fat,
                    "carbs": carbs
                })

                st.success(f"Added {food.get('description').capitalize()} to saved meals!")

# -------------------- LINE SEPARATOR --------------------
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

# -------------------- NUTRITIONAL VALUES DISPLAY --------------------
# Title for the total nutritional values display
st.markdown("""
    <div style="text-align: center; color: green;">
        <h2 class="subtitle" style="color: green;">🍽️ Total Nutritional Values</h2>
    </div>
""", unsafe_allow_html=True)

# Dropdown menu to select a saved meal
if st.session_state.saved_meals:
    meal_names = [meal["name"] for meal in st.session_state.saved_meals]
    selected_meal_name = st.selectbox("Select a saved meal to view its nutritional values:", meal_names)
    # Expander to show nutritional information
    with st.expander("View Nutritional Information"):
        # Find the selected meal
        selected_meal = next(meal for meal in st.session_state.saved_meals if meal["name"] == selected_meal_name)

        # Show the nutritional values of the selected meal
        st.write("### Nutritional Information:")
        st.write(f"- **Calories**: {selected_meal['calories']:.2f} kcal")
        st.write(f"- **Protein**: {selected_meal['protein']:.2f} g")
        st.write(f"- **Fat**: {selected_meal['fat']:.2f} g")
        st.write(f"- **Carbohydrates**: {selected_meal['carbs']:.2f} g")

# Option to display totals
if st.session_state.saved_meals:
    with st.expander("Show Total Nutritional Information"):
        # Display total nutrients in text format
        total_calories = sum(meal["calories"] for meal in st.session_state.saved_meals)
        total_protein = sum(meal["protein"] for meal in st.session_state.saved_meals)
        total_fat = sum(meal["fat"] for meal in st.session_state.saved_meals)
        total_carbs = sum(meal["carbs"] for meal in st.session_state.saved_meals)

        st.write("### Total Nutritional Information:")
        st.write(f"- **Total Calories**: {total_calories:.2f} kcal")
        st.write(f"- **Total Protein**: {total_protein:.2f} g")
        st.write(f"- **Total Fat**: {total_fat:.2f} g")
        st.write(f"- **Total Carbohydrates**: {total_carbs:.2f} g")

        # Display total nutrients in graphical format
        st.write("### Nutrient Distribution:")
        nutrients = ['Carbohydrates', 'Proteins', 'Fats']
        values = [total_carbs, total_protein, total_fat]
        max_values = [240, 96, 64]  # Recommended daily intake for each nutrient

        colors = ["#4caf50", "#2196f3", "#ff9800"]  # Different colors for each bar
        for nutrient, value, max_value, color in zip(nutrients, values, max_values, colors):
            bar_color = color if value <= max_value else "#ff5252"  # Use red if exceeded
            st.markdown(f"""
            <div style="margin-bottom: 10px;">
                <strong>{nutrient}</strong>
                <div style="background-color: #e0e0e0; border-radius: 5px; overflow: hidden; height: 20px; width: 100%;">
                <div style="background-color: {bar_color}; width: {min(value / max_value * 100, 100)}%; height: 100%;"></div>
                </div>
                <span>{value:.2f} / {max_value} g</span>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("No meals saved. Add meals to see totals.")