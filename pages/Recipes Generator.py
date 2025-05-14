import streamlit as st
import requests # for API calls
from dotenv import load_dotenv # for loading environment variables
import os
import time # for the spinner effect
import datetime
import json
import uuid # for generating unique IDs so that each recipe has a unique identifier and no conflicts occurr
from streamlit_extras.switch_page_button import switch_page # for switching between pages

# -------------------- Initialize session state for recipes and calendar ----------------------
if "recipes" not in st.session_state:
    st.session_state["recipes"] = []    # if the session state does not exist, create it

if "calendar_recipes" not in st.session_state:
    st.session_state["calendar_recipes"] = []   # if the session state does not exist, create it

# -------------------- Load environment variables from .env file ------------------------------
load_dotenv() 

# --------------------- API keys and URLs ----------------------------------------------------
API_KEY_SPOONACULAR = os.getenv("API_KEY_SPOONACULAR")

# -------------------- Load user preferences from profile data (JSON file) --------------------
def load_user_preferences():
    try:
        with open('ressources/profile_data.json', 'r') as f:  # Load the user preferences from the profile data
            data = json.load(f)
            goal = data.get("goal")  # Get the goal exactly as it is in the file
            diet = data.get("diet")  # Get the diet exactly as it is in the file
            return {"goal": goal, "diet": diet}
    except FileNotFoundError:
        return {"goal": None, "diet": None}  # Return None if the file is not found

# -------------------- Define the user preferences ---------------------------------------------
user_prefs = load_user_preferences()    # load the user preferences from the profile data
diet = user_prefs.get("diet", "None")   # assign diet and goal from the user preferences
goal = user_prefs.get("goal", "None")

# -------------------- Handle API error responses ---------------------------------------------
def handle_api_error(response):     

    if response.status_code == 200:     # Successful response
        return True
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
# This checkbox allows the user to toggle between test mode and live mode. In test mode, local JSON files are used 
# for testing purposes, while in live mode, API calls are made to fetch real data.
test_mode = st.sidebar.checkbox("⚙️ Use Test Mode (Load Local JSON Data)", value=True)  

# -------------------- Load the custom CSS for styling the app --------------------------------
with open("ressources/styles.css") as f:     
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ------------------- Navigation buttons for different sections ------------------------------
active_page = "Recipes"  # Set the active page to "Recipes", which is used for styling the navigation buttons

st.markdown('<div class="nav-container">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])       # create 4 columns for the navigation buttons between the pages

with col1:
    st.markdown('<div class="active-button">', unsafe_allow_html=True)
    if st.button("👤 Profile"):
        st.switch_page("pages/profile_view.py")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="active-button">', unsafe_allow_html=True)
    if st.button("📊 Visual Data"):
        st.switch_page("pages/data_visualization.py")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown('<div class="active-button">', unsafe_allow_html=True)
    if st.button("🥗 Recipes"):
        st.switch_page("pages/Recipes Generator.py")
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown('<div class="active-button">', unsafe_allow_html=True)
    if st.button("📒 Calories"):
        st.switch_page("pages/Calories Tracker.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)   # close the navigation container

# ------------------- Display the title -------------------------------------------------------
st.markdown('<p class="title">Discover Recipes Based on Your Preferences</p>', unsafe_allow_html=True)

# ------------------- Load user's profile data for personalized welcome message ---------------
try:      
    with open('ressources/profile_data.json', 'r') as f:
        profile_data = json.load(f)
        user_name = profile_data.get("name", "Guest")   # get the user name from the profile data
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
    if test_mode:  # Use local JSON file if in test mode
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
    else:           # live mode: make an API call to fetch recipes
        calorie_ranges = {          # define calorie ranges based on the user's goal
            "just eat Healthier :)": "",    # no calorie restriction because the filter is based on recipes' health score (which is filtered later)
            "Lose Weight": "maxCalories=500",
            "Build Muscle": "minCalories=600&maxCalories=1000",
            "None": "minCalories=0&maxCalories=10000"
        }
        goal_calories = calorie_ranges.get(goal, "calories=2000")  # Default to 2000 kcal

        url = f"https://api.spoonacular.com/recipes/complexSearch?diet={diet}&{goal_calories}&cuisine={cuisine}&type={dish_type}&sort=healthiness&number=15&addRecipeInformation=true&apiKey={API_KEY_SPOONACULAR}"
        response = requests.get(url)
        if handle_api_error(response):
            return response.json().get("results", [])
        else:
            return []

# ------------------ Recipe details functions -------------------------------------------------
def get_recipe_details(recipe_id, test_mode=False):
    if test_mode:   # Use local JSON file if in test mode
        try:
            with open('ressources/sample_recipe_details.json', 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    recipe_details = next((recipe for recipe in data if recipe["id"] == recipe_id), None)
                    return recipe_details
                else:
                    st.error("Test data is not in the expected format (list of recipes).")
                    return {}
        except FileNotFoundError:
            st.error("Test data file not found.")
            return {}
        except json.JSONDecodeError:
            st.error("Test data file is not properly formatted. Please check 'sample_recipe_details.json'.")
            return {}
    else:         # live mode: make an API call to fetch recipe details
        url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=true&apiKey={API_KEY_SPOONACULAR}"
        response = requests.get(url)
        if handle_api_error(response):
            data = response.json()
            return data
        else:
            return {}

# ------------------ Display recipe details functions -----------------------------------------
def display_recipe_details(details):
    with st.expander("📋 Recipe Details"):  
        diet_tags = details.get("diets", [])    # get the diet tags from the recipe details
        active_diets = diet_tags if diet_tags else []

        display_recipe_attributes(details, active_diets)
        display_nutrition_information(details)
        display_ingredients_and_instructions(details)

# ------------------ Display recipe attributes functions -------------------------------------
def display_recipe_attributes(details, active_diets):   
    attributes = [
        ("Ready in", f"{details.get('readyInMinutes', 'N/A')} min"),
        ("Servings", details.get('servings', 'N/A')),
        ("Health Score", f"{int(details.get('healthScore', 0))} / 100" if details.get('healthScore') is not None else "N/A"),
        ("Diet Tags", ', '.join(active_diets) if active_diets else 'None')
    ]
    
    for label, value in attributes:
        st.markdown(f"<p style='margin: 0;'><b>{label}:</b> {value}</p>", unsafe_allow_html=True)

# ------------------ Display nutrition information functions ---------------------------------
def display_nutrition_information(details):
    if "nutrition" in details and details["nutrition"].get("nutrients"):
        nutrients = details.get("nutrition", {}).get("nutrients", [])
        calories = next((n["amount"] for n in nutrients if n["name"] == "Calories"), None)
        carbs = next((n["amount"] for n in nutrients if n["name"] == "Carbohydrates"), None)
        fat = next((n["amount"] for n in nutrients if n["name"] == "Fat"), None)
        protein = next((n["amount"] for n in nutrients if n["name"] == "Protein"), None)

        with st.container():
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Nutrition Information", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)  # create 2 columns for the nutrition information
            
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
    ingredients = details.get("extendedIngredients", [])
    if ingredients:
        st.markdown("\n".join([f"- {ing['original']}" for ing in ingredients]))
    else:
        st.info("No ingredients available.")

    st.markdown("### Instructions")
    instructions = details.get("analyzedInstructions", [])
    if instructions:
        steps = []
        for instruction in instructions:
            steps.extend([f"{i + 1}. {step['step']}" for i, step in enumerate(instruction.get("steps", []))])
        st.markdown("\n".join(steps))
    else:
        st.info("No instructions available.")

# ------------------ API parameters mapping functions ----------------------------------------
def get_api_params(diet, goal, cuisine, dish_type):
    if not diet:    
        diet = ""   # if diet is None, set it to empty string
    else:
        diet = diet.lower()    # convert diet to lowercase, so that it matches the API requirements

    cuisine = "" if cuisine == "Any" else cuisine.lower()   # if cuisine is "Any", set it to empty string

    dish_type_map = {               # map dish types to API requirements
        "Appetizer": "appetizer",   
        "Side Dish": "side dish",
        "Lunch": "main course",
        "Dinner": "main course",
        "Snack": "snack",
        "Dessert": "dessert"
    }
    
    dish_type = "" if dish_type == "Any" else dish_type_map.get(dish_type, "")  # if dish type is "Any", set it to empty string
    
    return diet, goal, cuisine, dish_type

# ------------------ Filter recipes by goal functions --------------------------------------
def filter_recipes_by_goal(recipes, goal):
    if goal == "just eat Healthier :)":     # filter recipes by health score
        recipes = [r for r in recipes if r.get("healthScore", 0) >= 60]
    elif goal.lower() == "build muscle":    # filter recipes by protein content
        recipes = [
            r for r in recipes
            if float(next((n for n in r.get("nutrition", {}).get("nutrients", []) if n["name"] == "Protein"), {}).get("amount", 0)) >= 5
        ]
    return recipes

# ------------------ Display recipe functions ------------------------------------------------
def display_recipe(recipe, index):
    with st.container():
        st.write(f"### {recipe['title']}")
        
        # Use a placeholder image if no image is available
        image_url = recipe.get('image', 'https://via.placeholder.com/150')  # Placeholder image
        st.image(image_url, width=150)

        # Fetch and display recipe details
        details = get_recipe_details(recipe["id"], test_mode=test_mode)
        if details:
            display_recipe_details(details)
        else:
            st.warning(f"Details not found for recipe ID {recipe['id']}.")

        # Form to save recipe to calendar
        unique_key = f"calendar_form_{recipe['id']}_{index}"  # Use a consistent key

        with st.form(unique_key):
            selected_date = st.date_input(f"📅 Add to calendar for {recipe['title']}", min_value=datetime.date.today())
            meal_category = st.selectbox("Choose the meal category:", ["Breakfast", "Lunch", "Dinner", "Snack"])
            submitted = st.form_submit_button(f"Save {recipe['title']} to Calendar")

            if submitted:
                save_recipe_to_calendar(recipe, selected_date, meal_category, details)

# ------------------ Save recipe to calendar functions -----------------------------------
def save_recipe_to_calendar(recipe, selected_date, meal_category, details):
    nutrients = details.get("nutrition", {}).get("nutrients", [])   # get the nutrients from the recipe details
    calories = next((n["amount"] for n in nutrients if n["name"] == "Calories"), None)
    carbs = next((n["amount"] for n in nutrients if n["name"] == "Carbohydrates"), None)
    fat = next((n["amount"] for n in nutrients if n["name"] == "Fat"), None)
    protein = next((n["amount"] for n in nutrients if n["name"] == "Protein"), None)

    recipe_entry = {        # this is the format of the recipe entry that will be saved to the calendar (calentar_recipes.json)
        "recipe_title": recipe["title"],
        "selected_date": selected_date.isoformat(),
        "meal_category": meal_category,
        "nutrition": {
            "calories": calories,
            "carbohydrates": carbs,
            "fat": fat,
            "protein": protein
        }
    }

    if "calendar_recipes" not in st.session_state:
        st.session_state["calendar_recipes"] = []   # create the calendar_recipes session state if it does not exist

    st.session_state["calendar_recipes"].append(recipe_entry)
    st.success(f"{recipe['title']} added to your calendar!")

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
        recipes = st.session_state["calendar_recipes"]      # get the recipes from the session state
        
        if recipes:
            with open('ressources/calendar_recipes.json', 'w') as f:    # open the file in write mode
                data_to_save = []
                for entry in recipes:       # iterate through the recipes
                    entry_copy = entry.copy()       # create a copy of the entry
                    if isinstance(entry_copy["selected_date"], datetime.date):      # check if the selected date is a date object
                        entry_copy["selected_date"] = entry_copy["selected_date"].isoformat()
                    data_to_save.append(entry_copy)     # append the entry to the data_to_save list
                
                json.dump(data_to_save, f, indent=4)    # save the recipes to the file
                
            st.success("Recipes have been saved to the calendar.")
        else:
            st.warning("No recipes to save.")
    else:
        st.warning("No recipes to save. Please add recipes to your calendar first.")   

# ------------------- Load recipes from file functions ------------------------------------
def load_from_file():
    try:
        with open('ressources/calendar_recipes.json', 'r') as f:
            content = f.read()      # read the content of the file
            
            if content.strip():     # check if the file is not empty
                return json.loads(content)
            else:
                return []  # Return empty list if file is empty
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Return empty list if the file is not found or is malformed

# -------------------- Reset calendar functions ------------------------------------------
def reset_calendar():
    with open('ressources/calendar_recipes.json', 'w') as f:
        json.dump([], f)    # reset the calendar_recipes.json file to an empty list

    st.session_state["calendar_recipes"] = []   # reset the session state to an empty list
    st.success("✅ Calendar has been reset successfully!")

# ------------------ User input for recipe search------------------------------------------
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) 
st.markdown('<p class="subtitle">Customize Your Recipe Search!</p>', unsafe_allow_html=True)   
cuisine = st.selectbox("🥙 Choose a cuisine:", ["Any", "American", "Italian", "Mexican", "Mediterranean", "French", "Indian", "Asian"])
dish_type = st.selectbox("🥘 Choose a dish type:", ["Any", "Appetizer", "Side Dish", "Lunch", "Dinner", "Snack", "Dessert"])

#   ----------------- Main button logic to fetch and display recipes -------------------------
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) 
st.markdown('<p class="subtitle">All set! Just press the button to get your recipes!</p>', unsafe_allow_html=True)

if st.button("🧑🏼‍🍳 Serve the Recipes!"):
    diet, goal, cuisine, dish_type = get_api_params(user_prefs["diet"], user_prefs["goal"], cuisine, dish_type) # get the API parameters from the user preferences
    
    with st.spinner("Fetching recipes... 🍽️"):
        time.sleep(2)
        recipes = get_recipes(diet, goal, cuisine, dish_type, test_mode=test_mode)      # fetch the recipes from the API
        st.session_state["recipes"] = recipes       # save the recipes to the session state

if "recipes" in st.session_state and st.session_state["recipes"]:
    st.subheader("Here are some recipes based on your preferences:")
    for index, recipe in enumerate(st.session_state["recipes"]):    # iterate through the recipes
        display_recipe(recipe, index)          
else:
    st.warning("No recipes found. Please adjust your filters.")

display_calendar_recipes()      

# ------------------ Save recipes to calendar functions -----------------------------------
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Press the button below to save these recipes to your calendar!</p>', unsafe_allow_html=True)

st.markdown('<div class="active-button">', unsafe_allow_html=True)
if st.button("✅ Save my Recipes!"):    # save the recipes to the calendar with this button
    save_to_file()
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="active-button">', unsafe_allow_html=True)
if st.button("🗑️ Reset Calendar"):      # reset the calendar with this butto   
    reset_calendar()
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="active-button">', unsafe_allow_html=True)
if st.button("📂 View Saved Recipes"):   # view the saved recipes (that are in the json file) with this button
    try:
        with open('ressources/calendar_recipes.json', 'r') as f:
            saved_recipes = json.load(f)   
            if saved_recipes:
                st.markdown("### Saved Recipes")
                for recipe in saved_recipes:        # display these information of the saved recipes
                    st.markdown(f"**Recipe Title:** {recipe['recipe_title']}")
                    st.markdown(f"- **Date:** {recipe['selected_date']}")
                    st.markdown(f"- **Meal Category:** {recipe['meal_category']}")
                    st.markdown("---")
            else:
                st.info("No saved recipes found.")
    except FileNotFoundError:
        st.warning("No saved recipes found.")
    except json.JSONDecodeError:
        st.error("Error reading the saved recipes file.")
st.markdown("</div>", unsafe_allow_html=True)

# ------------------ Navigation button to Calories Tracker -----------------------------------
st.markdown('<p class="subtitle">Go to Calories Tracker to manage your daily nutrition based on your goal!</p>', unsafe_allow_html=True)

st.markdown('<div class="active-button">', unsafe_allow_html=True)
if st.button("📊 Go to Calories Tracker"):      # option to go to calories tracker page
    st.switch_page("pages/Calories Tracker.py")

# Code developed with the help of ChatGPT and Copilot.