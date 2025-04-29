import streamlit as st
import requests # for API calls
from dotenv import load_dotenv # for loading environment variables
import os
import time # for the spinner effect
import datetime
import json

load_dotenv()  # This loads everything from the .env file

def load_user_preferences():
    try:
        with open('profile_data.json', 'r') as f:
            data = json.load(f)
            return {
                "goal": data.get("goals", ["None"])[0],  # Prende il primo goal dalla lista
                "diet": data.get("diet", "None")
            }
    except FileNotFoundError:
        return {
            "goal": "None",
            "diet": "None"
        }

user_prefs = load_user_preferences()   

diet = user_prefs.get("diet", "None")
goal = user_prefs.get("goal", "None")

with open("styles.css") as f:       # this loads the CSS file that contains the styles for the app 
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

API_KEY_VALE = os.getenv("API_KEY_VALE")  # This grabs the spoonacular key from the .env file

test_mode = st.sidebar.checkbox("⚙️ Use Test Mode (Load Local JSON Data)", value=True)

# This sets the title, description and separator according to the styles defined in the CSS file
st.markdown('<p class="title">Discover Recipes Based on Your Preferences</p>', unsafe_allow_html=True) # this is the title of the app: displays the title with custom CSS applied (through the class="title") and defined in the CSS file -> <p> is a paragraph tag and is used for inline text elements
st.markdown('<div class="description">Welcome! Discover delicious recipes tailored to your dietary goals, preferences, and cuisine choices. Get cooking today!</p>', unsafe_allow_html=True)
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this add a line separator

# Mostra le preferenze salvate dell'utente
st.markdown('<p class="subtitle">Here are your preferences:</p>', unsafe_allow_html=True)
st.markdown(f"<p style='font-size: 20px; margin-left: 50px;'><b>🎯 Goal:</b> {goal}</p>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size: 20px; margin-left: 50px;'><b>🥗 Diet:</b> {diet}</p>", unsafe_allow_html=True)

def get_recipes(diet, goal, cuisine, dish_type, test_mode=False):    # this function fetches recipes based on the user's dietary preference and goal
    if test_mode:       # this is a test mode that uses a local JSON file instead of the API, for when I reached the limit of the API key
        with open('sample_recipes.json', 'r') as f:
            data = json.load(f)
        return data.get("results", [])
    
    calorie_ranges = {                              # this is a dictionary that contains the filters for each goal
        "Eat Healthier": "minHealthScore=80",       # for eat healthier, we take the health score given by the API
        "Lose Weight": "maxCalories=500",
        "Gain Weight": "minCalories=800",
        "None": "minCalories=0&maxCalories=10000"
    }

    goal_calories = calorie_ranges.get(goal, "calories=2000")  # Default to 2000 kcal, so if the user selects "None", the goal_calories is automatically set to 2000 kcal 

    url = f"https://api.spoonacular.com/recipes/complexSearch?diet={diet}&{goal_calories}&cuisine={cuisine}&type={dish_type}&number=5&apiKey={API_KEY_VALE}" # this url fetches recipes from the Spoonacular website based on the user's dietary preference, cuisine and goal

    response = requests.get(url)        # this sends a GET request to the Spoonacular API, based on the url created above (and with the details of the user's preferences)
    if response.status_code == 200:
        return response.json().get("results", [])  # if the code is 200, it means the request was successful and we return the results
    else:
        st.error("Failed to fetch recipes. You have probably reached the limit of your API key, try again tomorrow.")
        return []

def get_recipe_details(recipe_id, test_mode=False):      # this function fetches the details of a specific recipe based on its ID
    if test_mode:   # this is a test mode that uses a local JSON file instead of the API, for when I reached the limit of the API key
        with open('sample_recipe_details.json', 'r') as f:
            return json.load(f)
        
    # this is the real API call that fetches the details of a specific recipe based on its ID    
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=true&apiKey={API_KEY_VALE}" # this url fetches the details of a specific recipe based on its ID
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()           # here the function returns the details of the recipe
    else:
        st.error("Failed to fetch recipe details.")
        return {}

def display_recipe_details(details):
    # Lista delle informazioni dietetiche del piatto
    diet_flags = {
        "Vegetarian": details.get("vegetarian"),
        "Vegan": details.get("vegan"),
        "Gluten-Free": details.get("glutenFree"),
        "Dairy-Free": details.get("dairyFree"),
        "Healthy": details.get("veryHealthy"),
        "Cheap": details.get("cheap"),
        "Sustainable": details.get("sustainable"),
        "Popular": details.get("veryPopular")
    }
    
    active_diets = [key for key, value in diet_flags.items() if value]  # Get the active diet tags

    # Visualizza gli attributi della ricetta
    attributes = [
        ("Ready in", f"{details['readyInMinutes']} min"),
        ("Servings", details['servings']),
        ("Health Score", f"{int(details['healthScore'])} / 100"),
        ("Diet Tags", ', '.join(active_diets) if active_diets else 'None')
    ]
    
    for label, value in attributes:  # Display attributes
        st.markdown(f"<p style='margin: 0;'><b>{label}:</b> {value}</p>", unsafe_allow_html=True)

    if "nutrition" in details and details["nutrition"].get("nutrients"):
        nutrients = details["nutrition"]["nutrients"]
        calories = next((n for n in nutrients if n["name"] == "Calories"), {}).get("amount")
        carbs = next((n for n in nutrients if n["name"] == "Carbohydrates"), {}).get("amount")
        fat = next((n for n in nutrients if n["name"] == "Fat"), {}).get("amount")
        protein = next((n for n in nutrients if n["name"] == "Protein"), {}).get("amount")

        with st.container():
            st.markdown("<br>", unsafe_allow_html=True)  # br means break, this adds a line break
            st.markdown(
                """
                ### Nutrition Information
                """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"<p style='margin: 5px 0;'><b>Calories:</b> {calories} kcal</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='margin: 5px 0;'><b>Fat:</b> {fat} g</p>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"<p style='margin: 5px 0;'><b>Carbohydrates:</b> {carbs} g</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='margin: 5px 0;'><b>Protein:</b> {protein} g</p>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("ℹ️  No nutrition information available for this recipe.")
    

def get_wine_pairing_for_food(food_name):
    url = f"https://api.spoonacular.com/food/wine/pairing?food={food_name}&apiKey={API_KEY_VALE}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {}  # fallback if the request fails

recipes = [] # this is an empty list that will be used to store the recipes fetched from the API

st.markdown("<br>", unsafe_allow_html=True)  # Add spacing before the checkbox
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this add a line separator

st.markdown('<p class="subtitle">Customize Your Recipe Search!</p>', unsafe_allow_html=True)
cuisine = st.selectbox("🥙 Choose a cuisine:", ["Any", "American", "Italian", "Mexican", "Mediterranean", "French", "Indian", "Asian"])
dish_type = st.selectbox("🥘 Choose a dish type:", ["Any", "Appetizer", "Side Dish", "Lunch", "Dinner", "Snack", "Dessert"])

st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this add a line separator
st.markdown('<p class="subtitle">Would you like to have a tasty wine paired to match your meals?</p>', unsafe_allow_html=True) 
get_wine_pairing = st.checkbox("🍷 Include wine pairing suggestions")  # Checkbox for wine pairing suggestions

st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this add a line separator
st.markdown('<p class="subtitle">All set! Just press the button to get your recipes!</p>', unsafe_allow_html=True)
if st.button("🧑🏼‍🍳 Serve the Recipes!"):                                # this button fetches the recipes based on the user's preferences
    diet = "" if diet == "None" else diet.lower()
    cuisine = "" if cuisine == "Any" else cuisine.lower()

    dish_type_map = {
        "Appetizer": "appetizer",
        "Side Dish": "side dish",
        "Lunch": "main course",
        "Dinner": "main course",
        "Snack": "snack",
        "Dessert": "dessert"
    }

    dish_type = "" if dish_type == "Any" else dish_type_map.get(dish_type, "")


    with st.spinner("Cooking up some recipes... 🍽️"):           # this shows a loading spinner while recipies are fetched
        time.sleep(2)  # Simulate a delay for the spinner effect
        recipes = get_recipes(diet, goal, cuisine, dish_type, test_mode=test_mode)
    
    st.session_state["recipes"] = recipes     
    
else:
    recipes = st.session_state.get("recipes", [])

if recipes:                                                 # this checks if there are any recipes in the list
    st.subheader("Here are some recipes based on your preferences:")
    
    if goal.lower() == "eat healthier":
        recipes = [r for r in recipes if r.get("healthScore", 0) >= 80]
    if not recipes:
        st.warning("No healthy recipes found with a health score of 80 or more.")
    else:
        for recipe in recipes:          # this loops through the recipes and displays them
            details = get_recipe_details(recipe["id"], test_mode=test_mode)  # this calls the get_recipe_details function and stores the results in the details variable
            
            if goal.lower() == "eat healthier" and details.get("healthScore", 0) < 80:
                continue

            with st.container():    
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)    # this creates a card for each recipe (for the styling)
                                            
                col1, col2 = st.columns([1, 3])                 # Show title and image upfront
                with col1:
                    st.image(recipe["image"], width=150)
                with col2:
                    st.markdown(f"### {recipe['title']}")

                with st.expander("See the ingredients and instructions for this recipe"):   # this creates an expander that shows the ingredients and instructions for the recipe
                      # Skip this recipe if it's not healthy enough
                    
                    if not details:         # Check if the details are empty (or None)
                        st.error("Could not fetch recipe details for this recipe.")
                        continue 
                    
                    display_recipe_details(details)     # this calls the function that displays the details of the recipe (defined earlier)

                    st.markdown("### Ingredients")      # this shows the ingredients for the recipe
                    ingredients = [f"- {ing['original']}" for ing in details.get("extendedIngredients", [])]
                    st.write("\n".join(ingredients))

                    st.markdown("### Instructions")     # this shows the instructions for the recipe
                    instructions = details.get("analyzedInstructions", [])
                    if instructions:
                        steps = [f"{step['number']}. {step['step']}" for step in instructions[0].get("steps", [])]
                        st.write("\n".join(steps))
                    else:
                        st.info("No instructions available.")

                    # Optional Wine Pairing: if a user selects the checkbox, wine pairing suggestions are loaded and displayed below the recipe
                    if get_wine_pairing:
                            
                            # Step 1: Try to extract a food-type keyword from dishTypes
                            dish_types = details.get("dishTypes", [])
                            if dish_types:
                                main_food = dish_types[0]
                            else:
                            # Step 2: Try to use a more meaningful part of the title 
                                words = recipe.get("title", "").lower().split()
                                keywords = ["chicken", "beef", "salmon", "pasta", "cheese", "steak", "shrimp", "lamb", "pork", "vegetable", "salad", "soup", "pizza", "taco", "burger", "tuna", "mushroom"]
                                main_food = next((word for word in words if word in keywords), "food")  # fallback to "food"

                            wine_data = get_wine_pairing_for_food(main_food.lower())
                            wines = wine_data.get("pairedWines", [])
                            note = wine_data.get("pairingText", "") 

                            if wines:
                                st.markdown(
                                    f"<p style='margin: 0;'><b>Suggested Wines:</b> {', '.join(wines)}</p>",
                                    unsafe_allow_html=True
                                )
                                if note:
                                    st.markdown(f"<p style='margin: 0;'>{note}</p>", unsafe_allow_html=True)
                            else:
                                st.markdown("<p style='margin: 0;'><b>Wine Pairing:</b> Not available</p>", unsafe_allow_html=True)

                # Wrap Date + Save button in a form:
                with st.form(f"calendar_form_{recipe['id']}"):
                    selected_date = st.date_input(
                        f"📅 Would you like to add this meal to your calendar?",
                        min_value=datetime.date.today()
                    )
                    submitted = st.form_submit_button(f"Save {recipe['title']} to Calendar")

                    if submitted:
                        if "calendar_recipes" not in st.session_state:
                            st.session_state["calendar_recipes"] = []
                        st.session_state["calendar_recipes"].append({
                            "recipe_id": recipe["id"],
                            "recipe_title": recipe["title"],
                            "selected_date": selected_date,
                            "nutrition_info": {
                                "calories": details.get("nutrition", {}).get("nutrients", [{}])[0].get("amount"),
                                "carbs": next((n for n in details.get("nutrition", {}).get("nutrients", []) if n["name"] == "Carbohydrates"), {}).get("amount"),
                                "fat": next((n for n in details.get("nutrition", {}).get("nutrients", []) if n["name"] == "Fat"), {}).get("amount"),
                                "protein": next((n for n in details.get("nutrition", {}).get("nutrients", []) if n["name"] == "Protein"), {}).get("amount")
                            }
                        })
                        st.success(f"Recipe {recipe['title']} added to your calendar for {selected_date}")   
                
                st.markdown('</div>', unsafe_allow_html=True)    # this closes the recipe card div (for the styling) 
                   
else:
    st.empty ()  # this shows an empty space if there are no recipes in the list

if "calendar_recipes" in st.session_state and st.session_state["calendar_recipes"]:
    st.subheader("Your Selected Recipes")
    
    # Visualizza le ricette programmate
    for entry in st.session_state["calendar_recipes"]:
        st.write(f"{entry['recipe_title']} on {entry['selected_date']}")
else:
    pass

# Salvataggio nel file JSON
def save_to_file():
    if "calendar_recipes" in st.session_state:
        # Convert dates to string before saving
        data_to_save = []
        for entry in st.session_state["calendar_recipes"]:
            entry_copy = entry.copy()
            if isinstance(entry_copy["selected_date"], datetime.date):
                entry_copy["selected_date"] = entry_copy["selected_date"].isoformat()  # Convert date to string
            data_to_save.append(entry_copy)

        with open('calendar_recipes.json', 'w') as f:
            json.dump(data_to_save, f)

# Caricamento dal file JSON
def load_from_file():
    try:
        with open('calendar_recipes.json', 'r') as f:
            content = f.read()
            if not content.strip():
                return []
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fix: create an empty JSON file
        with open('calendar_recipes.json', 'w') as f:
            json.dump([], f)
        return []  # Se il file non esiste, restituisce una lista vuotas

def reset_calendar():
    # Clear the calendar_recipes.json file
    with open('calendar_recipes.json', 'w') as f:
        json.dump([], f)

    # Also reset the session state in the app
    st.session_state["calendar_recipes"] = []

    st.success("✅ Calendar has been reset successfully!")

# Aggiungi un separatore e un titolo
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Press the button below to save these recipes to your calendar!</p>', unsafe_allow_html=True)

# Pulsante per salvare le ricette nel file JSON
if st.button("✅ Save my Recipes!"):
    save_to_file()

# Pulsante per cancellare le ricette dal file JSON
if st.button("🗑️ Reset Calendar"):
    reset_calendar()

# Carica le ricette dal file JSON quando l'app si avvia
calendar_recipes = load_from_file()

# Visualizza le ricette caricate dal file
if calendar_recipes:
    st.subheader("Recipes loaded from the file:")
    for recipe in calendar_recipes:
        st.markdown(f"### {recipe['recipe_title']} on {recipe['selected_date']}")

