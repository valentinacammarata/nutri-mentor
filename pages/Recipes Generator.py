import streamlit as st
import requests # for API calls
from dotenv import load_dotenv # for loading environment variables
import os
import time # for the spinner effect
import datetime
import json
import uuid # for generating unique IDs so that each recipe has a unique identifier and no conflicts occurr

# -------------------- Initialize session state for recipes and calendar ----------------------
if "recipes" not in st.session_state:
    st.session_state["recipes"] = []

if "calendar_recipes" not in st.session_state:
    st.session_state["calendar_recipes"] = []

# -------------------- Load environment variables from .env file ------------------------------
load_dotenv() 

# --------------------- API keys and URLs ----------------------------------------------------
API_KEY_SPOONACULAR = os.getenv("API_KEY_SPOONACULAR")

# -------------------- Load user preferences from profile data (JSON file) --------------------
def load_user_preferences():
    try:
        with open('ressources/profile_data.json', 'r') as f:
            data = json.load(f)
            goals = data.get("goals", [])
            goal = goals[0] if goals else "None"
            diet = data.get("diet", "No Preference")
            return {"goal": goal, "diet": diet}
    except FileNotFoundError:
        return {"goal": "None", "diet": "No Preference"}

# -------------------- Define the user preferences ---------------------------------------------
user_prefs = load_user_preferences()
diet = user_prefs.get("diet", "None")
goal = user_prefs.get("goal", "None")

# -------------------- Handle API error responses ---------------------------------------------
def handle_api_error(response):

    if response.status_code == 200:
        return True  # Successful response
    elif response.status_code == 401:
        st.error("Unauthorized access. Please check your API key.")
    elif response.status_code == 402:
        st.error("Payment required. Your API key may have exceeded its usage limits or requires a paid plan.")
    elif response.status_code == 403:
        st.error("Access forbidden. Your API key might have been restricted.")
    elif response.status_code == 404:
        st.error("Resource not found. Please check the API endpoint.")
    elif response.status_code == 429:
        st.error("Rate limit exceeded. Please wait and try again later.")
    elif response.status_code >= 500:
        st.error("Server error. The API service might be down. Try again later.")
    else:
        st.error(f"Unexpected error occurred. Status code: {response.status_code}")
    
    return False  # If any error occurs, return False

# -------------------- Sidebar for test mode --------------------------------------------------
test_mode = st.sidebar.checkbox("⚙️ Use Test Mode (Load Local JSON Data)", value=True)

# -------------------- Load the custom CSS for styling the app --------------------------------
with open("ressources/styles.css") as f:       
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ------------------- Display the title and welcome message -----------------------------------
st.markdown('<p class="title">Discover Recipes Based on Your Preferences</p>', unsafe_allow_html=True)

# ------------------- Load user's profile data for personalized welcome message ---------------
try:      
    with open('ressources/profile_data.json', 'r') as f:
        profile_data = json.load(f)
        user_name = profile_data.get("name", "Guest")
except FileNotFoundError:
    user_name = "Guest"

st.markdown(f'<div class="description">Welcome, {user_name}! Discover delicious recipes tailored to your dietary goals, preferences, and cuisine choices. Get cooking today!</p>', unsafe_allow_html=True)
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) 

# ------------------ Display user preferences ------------------------------------------------
st.markdown(f"<div class='subtitle'>Here are your Preferences</div>", unsafe_allow_html=True) 
st.markdown(f"<p style='font-size: 20px; margin-left: 50px;'><b>🎯 Goal:</b> {goal}</p>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size: 20px; margin-left: 50px;'><b>🥗 Diet:</b> {diet}</p>", unsafe_allow_html=True)

# ------------------ Recipe fetching functions -------------------------------------------------
def get_recipes(diet, goal, cuisine, dish_type, test_mode=False):
    if test_mode:  # Use local JSON file in test mode
        try:
            with open('ressources/sample_recipes.json', 'r') as f:
                data = json.load(f)
                return data.get("results", [])  # Return the list of recipes from the test data
        except FileNotFoundError:
            st.error("Test data file not found. Please ensure 'sample_recipes.json' exists in the 'ressources' folder.")
            return []
        except json.JSONDecodeError:
            st.error("Test data file is not properly formatted. Please check 'sample_recipes.json'.")
            return []
    else:
        # API call for live mode
        calorie_ranges = {
            "just eat Healthier :)": "",
            "Lose Weight": "maxCalories=500",
            "Build Muscle": "minCalories=600&maxCalories=1000",
            "None": "minCalories=0&maxCalories=10000"
        }
        goal_calories = calorie_ranges.get(goal, "calories=2000")  # Default to 2000 kcal

        url = f"https://api.spoonacular.com/recipes/complexSearch?diet={diet}&{goal_calories}&cuisine={cuisine}&type={dish_type}&sort=healthiness&number=5&addRecipeInformation=true&apiKey={API_KEY_SPOONACULAR}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            st.error(f"Failed to fetch recipes. Error: {response.status_code}")
            return []

# ------------------ Recipe details functions -------------------------------------------------
def get_recipe_details(recipe_id, test_mode=False):
    if test_mode:  # Use local JSON file in test mode
        try:
            with open('ressources/sample_recipe_details.json', 'r') as f:
                data = json.load(f)  # Parse JSON file
                #st.write("Loaded test data:", data)  # Debug: Log the loaded test data
                if isinstance(data, list):  # Ensure data is a list
                    # Simulate fetching details for a specific recipe ID
                    recipe_details = next((recipe for recipe in data if recipe["id"] == recipe_id), None)
                    if recipe_details:
                        #st.write("Recipe details found:", recipe_details)  # Debug: Log the recipe details
                        return recipe_details
                    else:
                        st.warning(f"No recipe found with ID {recipe_id} in test data.")
                        return {}
                else:
                    st.error("Test data is not in the expected format (list of recipes).")
                    return {}
        except FileNotFoundError:
            st.error("Test data file not found.")
            return {}
        except json.JSONDecodeError:
            st.error("Test data file is not properly formatted. Please check 'sample_recipe_details.json'.")
            return {}
    else:
        url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=true&apiKey={API_KEY_SPOONACULAR}"
        response = requests.get(url)
        if handle_api_error(response):
            return response.json()
        else:
            return {}

# ------------------ Display recipe details functions -----------------------------------------
def display_recipe_details(details):
    with st.expander("📋 Recipe Details"):
        # Extract diet tags from the details
        diet_tags = details.get("dietTags", [])
        active_diets = diet_tags if diet_tags else []

        display_recipe_attributes(details, active_diets)
        display_nutrition_information(details)
        display_ingredients_and_instructions(details)

# ------------------ Display recipe attributes functions -------------------------------------
def display_recipe_attributes(details, active_diets):
    attributes = [
        ("Ready in", f"{details.get('readyInMinutes', 'N/A')} min"),  # Use .get() with a default value
        ("Servings", details.get('servings', 'N/A')),
        ("Health Score", f"{int(details.get('healthinessScore', 0))} / 100"),  # Corrected key
        ("Diet Tags", ', '.join(active_diets) if active_diets else 'None')
    ]
    
    for label, value in attributes:
        st.markdown(f"<p style='margin: 0;'><b>{label}:</b> {value}</p>", unsafe_allow_html=True)
        
# ------------------ Display nutrition information functions ---------------------------------
def display_nutrition_information(details):
    if "nutrition" in details and details["nutrition"].get("nutrients"):
        nutrients = details.get("nutrition", {}).get("nutrients", [])
        calories = next((n for n in nutrients if n["name"] == "Calories"), {}).get("amount")
        carbs = next((n for n in nutrients if n["name"] == "Carbohydrates"), {}).get("amount")
        fat = next((n for n in nutrients if n["name"] == "Fat"), {}).get("amount")
        protein = next((n for n in nutrients if n["name"] == "Protein"), {}).get("amount")

        with st.container():
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Nutrition Information", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"<p style='margin: 5px 0;'><b>Calories:</b> {calories} kcal</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='margin: 5px 0;'><b>Fat:</b> {fat} g</p>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"<p style='margin: 5px 0;'><b>Carbohydrates:</b> {carbs} g</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='margin: 5px 0;'><b>Protein:</b> {protein} g</p>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Nutrition information not available.")      

# ------------------ Display ingredients and instructions functions ---------------------------
def display_ingredients_and_instructions(details):
    st.markdown("### Ingredients")
    ingredients = details.get("ingredients", [])
    st.write("\n".join([f"- {ing}" for ing in ingredients]))

    st.markdown("### Instructions")
    instructions = details.get("instructions", [])
    if instructions:
        steps = [f"{i + 1}. {step}" for i, step in enumerate(instructions)]
        st.write("\n".join(steps))
    else:
        st.info("No instructions available.")

# ------------------ Wine pairing functions ---------------------------------------------------
def get_wine_pairing_for_food(food_name): 
    url = f"https://api.spoonacular.com/food/wine/pairing?food={food_name}&apiKey={API_KEY_SPOONACULAR}" 
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {}  # fallback if the request fails
    
# ------------------ API parameters mapping functions ----------------------------------------
def get_api_params(diet, goal, cuisine, dish_type):
    if not diet:
        diet = ""
    else:
        diet = diet.lower()

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
    
    return diet, goal, cuisine, dish_type

# ------------------ Filter recipes by goal functions --------------------------------------
def filter_recipes_by_goal(recipes, goal):
    if goal == "just eat Healthier :)":
        recipes = [r for r in recipes if r.get("healthScore", 0) >= 60]
    elif goal.lower() == "build muscle":
        recipes = [
            r for r in recipes
            if float(next((n for n in r.get("nutrition", {}).get("nutrients", []) if n["name"] == "Protein"), {}).get("amount", 0)) >= 5
        ]
    return recipes

# ------------------ Display recipe functions ------------------------------------------------
def display_recipe(recipe, index):
    with st.container():
        st.write(f"### {recipe['title']}")
        st.image(recipe['image'], width=150)

        # Fetch and display recipe details
        details = get_recipe_details(recipe["id"], test_mode=test_mode)
        if details:
            display_recipe_details(details)
        else:
            st.warning(f"Details not found for recipe ID {recipe['id']}.")

        # Form to save recipe to calendar
        unique_key = f"calendar_form_{recipe['id']}_{index}_{uuid.uuid4()}"  # uuid.uuid4() generates a unique ID, this ensures that each form has a unique key
        with st.form(unique_key):  # unique_key is used to ensure that each form has a unique key
            selected_date = st.date_input(f"📅 Add to calendar for {recipe['title']}", min_value=datetime.date.today())
            meal_category = st.selectbox("Choose the meal category:", ["Breakfast", "Lunch", "Dinner", "Snack"])
            submitted = st.form_submit_button(f"Save {recipe['title']} to Calendar")

            if submitted:
                save_recipe_to_calendar(recipe, selected_date, meal_category, details)

# ------------------ Display wine pairing functions ----------------------------------------
def display_wine_pairing(recipe, details):
    main_food = extract_food_from_recipe(recipe, details)
    wine_data = get_wine_pairing_for_food(main_food)
    
    wines = wine_data.get("pairedWines", [])
    note = wine_data.get("pairingText", "")
    
    if wines:
        st.markdown(f"<p style='margin: 0;'><b>Suggested Wines:</b> {', '.join(wines)}</p>", unsafe_allow_html=True)
        if note:
            st.markdown(f"<p style='margin: 0;'>{note}</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='margin: 0;'><b>Wine Pairing:</b> Not available</p>", unsafe_allow_html=True)

# ------------------ Extract food from recipe functions -----------------------------------
def extract_food_from_recipe(recipe, details):
    dish_types = details.get("dishTypes", [])
    if dish_types:
        return dish_types[0]
    else:
        words = recipe.get("title", "").lower().split()
        keywords = ["chicken", "beef", "salmon", "pasta", "cheese", "steak", "shrimp", "lamb", "pork", "vegetable", "salad", "soup", "pizza", "taco", "burger", "tuna", "mushroom"]
        return next((word for word in words if word in keywords), "food")

# ------------------ Save recipe to calendar functions -----------------------------------
def save_recipe_to_calendar(recipe, selected_date, meal_category, details):
    # Extract nutrition information
    nutrients = details.get("nutrition", {}).get("nutrients", [])
    calories = next((n["amount"] for n in nutrients if n["name"] == "Calories"), None)
    carbs = next((n["amount"] for n in nutrients if n["name"] == "Carbohydrates"), None)
    fat = next((n["amount"] for n in nutrients if n["name"] == "Fat"), None)
    protein = next((n["amount"] for n in nutrients if n["name"] == "Protein"), None)

    # Save recipe with nutrition info to session state
    st.session_state["calendar_recipes"].append({
        "recipe_id": recipe["id"],
        "recipe_title": recipe["title"],
        "selected_date": selected_date,
        "meal_category": meal_category,
        "nutrition": {
            "calories": calories,
            "carbohydrates": carbs,
            "fat": fat,
            "protein": protein
        }
    })
    st.success(f"{recipe['title']} added to your calendar with nutrition info!")

# ------------------ Display calendar recipes functions -----------------------------------
def display_calendar_recipes():
    if "calendar_recipes" in st.session_state and st.session_state["calendar_recipes"]:
        st.subheader("Your Selected Recipes")
        for entry in st.session_state["calendar_recipes"]:
            st.write(f"{entry['recipe_title']} on {entry['selected_date']} as {entry['meal_category']}")
    else:
        pass

# ------------------- Save and load recipes functions --------------------------------------
def save_to_file():
    if "calendar_recipes" in st.session_state:
        recipes = st.session_state["calendar_recipes"]
        
        if recipes:
            
            with open('ressources/calendar_recipes.json', 'w') as f:
                data_to_save = []
                for entry in recipes:
                    entry_copy = entry.copy()
                    if isinstance(entry_copy["selected_date"], datetime.date):
                        entry_copy["selected_date"] = entry_copy["selected_date"].isoformat()
                    data_to_save.append(entry_copy)
                
                json.dump(data_to_save, f, indent=4)
                
            st.success("Recipes have been saved to the calendar.")
        else:
            st.warning("No recipes to save.")
    else:
        st.warning("No recipes to save. Please add recipes to your calendar first.")   

# ------------------- Load recipes from file functions ------------------------------------
def load_from_file():
    try:
        # Load from the file
        with open('ressources/calendar_recipes.json', 'r') as f:
            content = f.read()
            
            if content.strip():
                return json.loads(content)
            else:
                return []  # Return empty list if file is empty
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Return empty list if the file is not found or is malformed

# -------------------- Reset calendar functions ------------------------------------------
def reset_calendar():
    with open('ressources/calendar_recipes.json', 'w') as f:
        json.dump([], f)  # Clear the JSON file

    st.session_state["calendar_recipes"] = []  # Clear the session state
    st.success("✅ Calendar has been reset successfully!")

# ------------------ User input for recipe search------------------------------------------
st.markdown('<p class="subtitle">Customize Your Recipe Search!</p>', unsafe_allow_html=True)   
cuisine = st.selectbox("🥙 Choose a cuisine:", ["Any", "American", "Italian", "Mexican", "Mediterranean", "French", "Indian", "Asian"])
dish_type = st.selectbox("🥘 Choose a dish type:", ["Any", "Appetizer", "Side Dish", "Lunch", "Dinner", "Snack", "Dessert"])

# ------------------ Checkbox with the option to add wine pairing suggestions ----------------
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) 
st.markdown('<p class="subtitle">Would you like to have a tasty wine paired to match your meals?</p>', unsafe_allow_html=True) 
get_wine_pairing = st.checkbox("🍷 Include wine pairing suggestions") 

#   ----------------- Main button logic to fetch and display recipes -------------------------
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) 
st.markdown('<p class="subtitle">All set! Just press the button to get your recipes!</p>', unsafe_allow_html=True)


# Main button logic to fetch and display recipes
if st.button("🧑🏼‍🍳 Serve the Recipes!"):
    # Get parameters from the user preferences
    diet, goal, cuisine, dish_type = get_api_params(user_prefs["diet"], user_prefs["goal"], cuisine, dish_type)
    
    with st.spinner("Fetching recipes... 🍽️"):
        time.sleep(2)  # Simulate API request delay
        recipes = get_recipes(diet, goal, cuisine, dish_type, test_mode=test_mode)  # Pass test_mode flag
        st.session_state["recipes"] = recipes  # Store recipes in session state

# Check if recipes are already in session state and display them
if "recipes" in st.session_state and st.session_state["recipes"]:
    st.subheader("Here are some recipes based on your preferences:")
    for index, recipe in enumerate(st.session_state["recipes"]):  # Use enumerate to get the index
        display_recipe(recipe, index)  # Pass the index to the function
else:
    st.warning("No recipes found. Please adjust your filters.")

# Display the calendar with selected recipes
display_calendar_recipes()

# ------------------ Save and load recipes to/from file -----------------------------------

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Press the button below to save these recipes to your calendar!</p>', unsafe_allow_html=True)

if st.button("✅ Save my Recipes!"):
    save_to_file()

if st.button("🗑️ Reset Calendar"):
    reset_calendar()

# Load calendar recipes from session state or file, if necessary
calendar_recipes = st.session_state.get("calendar_recipes", [])

# ------------------ Buttons to navigate to other pages -----------------------------------
st.markdown('<p class="subtitle">Navigate to other sections:</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Go to Calories Tracker"):
        st.switch_page("pages/Calories Tracker.py")

with col2:
    if st.button("👤 Go to Your Profile Dashboard"):
        st.switch_page("pages/profile_view.py")