import streamlit as st
import requests
from datetime import date
from streamlit_extras.switch_page_button import switch_page  
import json
import os

# -------------------- CONFIGURAZIONE FILE JSON --------------------
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

# Inizializza lo stato globale
if "saved_meals" not in st.session_state:
    st.session_state.saved_meals = load_calendar_recipes()

# -------------------- STILI CSS --------------------
with open("ressources/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------- TITOLO --------------------
st.markdown("""
    <div class="title-container">
        <h1 class="title">Snack Nutritional Tracker</h1>
        <p class="subtitle" style="font-style: italic;">
            Enter a food item and its quantity to calculate your daily nutritional intake. 
            <strong>NutriMentor</strong> analyzes calories, proteins, fats, and carbohydrates instantly, 
            helping you make informed dietary choices every day.
        </p>
    </div>
""", unsafe_allow_html=True)

if st.button("Go Back to Calorie Tracker", key="go_back_button"):
    switch_page("Calories Tracker")

# -------------------- DATA --------------------
st.markdown("<div style='text-align: center;'><h2 class='subtitle'>📅 Select the Day for Your Snacks's Entries</h2></div>", unsafe_allow_html=True)
selected_date = st.date_input("Select a date for your meal:", value=date.today(), min_value=date(2000, 1, 1), max_value=date(2100, 12, 31))
date_key = selected_date.strftime("%Y-%m-%d")

# -------------------- API USDA --------------------
API_KEY = "aL8QBhKyNY5zMFjZioZY0yQCk8GgtHjtaBjbsMfH"

def fetch_food_data(query):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"api_key": API_KEY, "query": query, "pageSize": 1}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching data from USDA API.")
        return None

# -------------------- INPUT ALIMENTO --------------------
st.markdown("<h2 class='subtitle' style='text-align: center; color: green;'>🍎 Search for Food Items</h2>", unsafe_allow_html=True)

food_query = st.text_input("Search for a food", placeholder="E.g. Apple, Banana, Coffee")
quantity = st.number_input(    "Enter the consumed quantity (in grams or ml):",     min_value=1,     value=100,     step=1)

if "totals" not in st.session_state:
    st.session_state.totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}

# -------------------- AGGIUNTA CIBO --------------------
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

                # Aggiorna i totali per la sessione
                st.session_state.totals["calories"] += calories
                st.session_state.totals["protein"] += protein
                st.session_state.totals["fat"] += fat
                st.session_state.totals["carbs"] += carbs

                # Crea il nuovo pasto
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

                # Salva nella sessione
                st.session_state.saved_meals.append(new_entry)

                # Salva nel file JSON
                save_calendar_recipes(st.session_state.saved_meals)

                st.success(f"Added {new_entry['recipe_title']} to {date_key}!")

# -------------------- SEZIONE RISULTATI --------------------
st.markdown("<h2 class='subtitle' style='text-align: center; color: green;'>🍽️ Total Nutritional Values</h2>", unsafe_allow_html=True)

# Filtra i pasti per la data selezionata
meals_today = [m for m in st.session_state.saved_meals if m["selected_date"] == date_key and m["meal_category"] == "Snack"]

if meals_today:
    meal_names = [m["recipe_title"] for m in meals_today]
    selected_meal_name = st.selectbox("Select a saved meal to view its nutritional values:", meal_names)

    selected_meal = next(m for m in meals_today if m["recipe_title"] == selected_meal_name)
    nutrition = selected_meal["nutrition"]

    with st.expander("View Nutritional Information"):
        st.write(f"- **Calories**: {nutrition['calories']} kcal")
        st.write(f"- **Protein**: {nutrition['protein']} g")
        st.write(f"- **Fat**: {nutrition['fat']} g")
        st.write(f"- **Carbohydrates**: {nutrition['carbohydrates']} g")

    with st.expander("Show Total Nutritional Information"):
        total_calories = sum(m["nutrition"]["calories"] for m in meals_today)
        total_protein = sum(m["nutrition"]["protein"] for m in meals_today)
        total_fat = sum(m["nutrition"]["fat"] for m in meals_today)
        total_carbs = sum(m["nutrition"]["carbohydrates"] for m in meals_today)

        st.write("### Total Nutritional Information:")
        st.write(f"- **Total Calories**: {total_calories:.2f} kcal")
        st.write(f"- **Total Protein**: {total_protein:.2f} g")
        st.write(f"- **Total Fat**: {total_fat:.2f} g")
        st.write(f"- **Total Carbohydrates**: {total_carbs:.2f} g")

        # Grafico barre
        nutrients = ['Carbohydrates', 'Proteins', 'Fats']
        values = [total_carbs, total_protein, total_fat]
        max_values = [240, 96, 64]
        colors = ["#4caf50", "#2196f3", "#ff9800"]

        for nutrient, value, max_value, color in zip(nutrients, values, max_values, colors):
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

    # Pulsante per eliminare i pasti del giorno
    if st.button("🗑️ Elimina tutti i pasti della colazione per questa data"):
        st.session_state.saved_meals = [
            m for m in st.session_state.saved_meals
            if not (m["selected_date"] == date_key and m["meal_category"] == "Breakfast")
        ]
        save_calendar_recipes(st.session_state.saved_meals)
        st.success("Pasti eliminati!")

        # Simula un aggiornamento della pagina
        st.query_params.clear()
else:
    st.info("No meals saved for this date.")

