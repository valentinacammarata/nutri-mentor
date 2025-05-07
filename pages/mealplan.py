import streamlit as st
import requests # for API calls
from dotenv import load_dotenv # for loading environment variables
import os
import time # for the spinner effect
import datetime
import json

load_dotenv()  # This loads everything from the .env file

def load_user_preferences():    # this function loads the user preferences from the JSON file (from the login page)
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

diet = user_prefs.get("diet", "None")   # this loads the diet preference from the JSON file
goal = user_prefs.get("goal", "None")   # this loads the goal preference from the JSON file 

with open("styles.css") as f:       # this loads the CSS file that contains the styles for the app 
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

API_KEY_SPOONACULAR = os.getenv("API_KEY_SPOONACULAR")  # This grabs the spoonacular key from the .env file

test_mode = st.sidebar.checkbox("⚙️ Use Test Mode (Load Local JSON Data)", value=True)

# This sets the title, description and separator according to the styles defined in the CSS file
st.markdown('<p class="title">Discover Recipes Based on Your Preferences</p>', unsafe_allow_html=True) # this is the title of the app: displays the title with custom CSS applied (through the class="title") and defined in the CSS file -> <p> is a paragraph tag and is used for inline text elements
try:        # this loads the user's name from the JSON file (from the login page) so that it can be displayed in the welcome message
    with open('profile_data.json', 'r') as f:
        profile_data = json.load(f)
        user_name = profile_data.get("name", "Guest")  # Load the user's name from the JSON file, default to "Guest" if not found
except FileNotFoundError:
    user_name = "Guest"

st.markdown(f'<div class="description">Welcome, {user_name}! Discover delicious recipes tailored to your dietary goals, preferences, and cuisine choices. Get cooking today!</p>', unsafe_allow_html=True)
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this adds a line separator

# This writes down the user preferences according to the input from the login page (the JSON file)
st.markdown(f"<div class='subtitle'>Here are your Preferences</div>", unsafe_allow_html=True) 
st.markdown(f"<p style='font-size: 20px; margin-left: 50px;'><b>🎯 Goal:</b> {goal}</p>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size: 20px; margin-left: 50px;'><b>🥗 Diet:</b> {diet}</p>", unsafe_allow_html=True)

def get_recipes(diet, goal, cuisine, dish_type, test_mode=False):    # this function fetches recipes based on the user's dietary preference and goal
    if test_mode:       # this is a test mode that uses a local JSON file with fictious recipes instead of the API, for when I reach the limit of the API key
        with open('sample_recipes.json', 'r') as f:
            data = json.load(f)
        return data.get("results", [])
    
    calorie_ranges = {                              # this is a dictionary that contains the filters for each goal
        "just eat Healthier :)": "",       
        "Lose Weight": "maxCalories=500",
        "Build Muscle": "minCalories=600&maxCalories=1000",
        "None": "minCalories=0&maxCalories=10000"
    }

    goal_calories = calorie_ranges.get(goal, "calories=2000")  # Default to 2000 kcal, so if the user selects "None", the goal_calories is automatically set to 2000 kcal 

    url = f"https://api.spoonacular.com/recipes/complexSearch?diet={diet}&{goal_calories}&cuisine={cuisine}&type={dish_type}&sort=healthiness&number=20&addRecipeInformation=true&apiKey={API_KEY_SPOONACULAR}"
    
    st.text(f"📡 Requesting: {url}")

    response = requests.get(url)        # this sends a GET request to the Spoonacular API, based on the url created above (and with the details of the user's preferences)
    if response.status_code == 200:
        return response.json().get("results", [])  # Request successful, return the results
    elif response.status_code == 401:
        st.error("Unauthorized access. Please check your API key.")
        return []
    elif response.status_code == 403:
        st.error("Access forbidden. Your API key might have been restricted.")
        return []
    elif response.status_code == 404:
        st.error("Resource not found. Please check the API endpoint.")
        return []
    elif response.status_code == 429:
        st.error("Rate limit exceeded. Please wait and try again later.")
        return []
    elif response.status_code >= 500:
        st.error("Server error. The API service might be down. Try again later.")
        return []
    else:
        st.error(f"Unexpected error occurred. Status code: {response.status_code}")
        return []

def get_recipe_details(recipe_id, test_mode=False):      # this function fetches the details of a specific recipe based on its ID
    if test_mode:   # this is a test mode that uses a local JSON file instead of the API, for when I reached the limit of the API key
        with open('sample_recipe_details.json', 'r') as f:
            return json.load(f)
        
    # this is the API call that fetches the details of a specific recipe based on its ID    
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=true&apiKey={API_KEY_SPOONACULAR}" 
    response = requests.get(url)
    if response.status_code == 200:      # this checks if the request was successful
        return response.json()           # here the function returns the details of the recipe
    else:
        st.error("Failed to fetch recipe details.")
        return {}

def display_recipe_details(details):

    diet_flags = {                                      # this is a dictionary that contains the diet flags for the recipe
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

    attributes = [                      # this is the first list of attributes that will be displayed for each recipe   
        ("Ready in", f"{details['readyInMinutes']} min"),
        ("Servings", details['servings']),
        ("Health Score", f"{int(details['healthScore'])} / 100"),
        ("Diet Tags", ', '.join(active_diets) if active_diets else 'None')
    ]
    
    for label, value in attributes:  # Display attributes with a certain style
        st.markdown(f"<p style='margin: 0;'><b>{label}:</b> {value}</p>", unsafe_allow_html=True)

    if "nutrition" in details and details["nutrition"].get("nutrients"):        # this checks if the recipe has nutrition information
        nutrients = details.get("nutrition", {}).get("nutrients", [])  
        calories = next((n for n in nutrients if n["name"] == "Calories"), {}).get("amount")    # this gets the calories from the nutrition information
        carbs = next((n for n in nutrients if n["name"] == "Carbohydrates"), {}).get("amount")  # this gets the carbohydrates from the nutrition information
        fat = next((n for n in nutrients if n["name"] == "Fat"), {}).get("amount")              # this gets the fat from the nutrition information
        protein = next((n for n in nutrients if n["name"] == "Protein"), {}).get("amount")      # this gets the protein from the nutrition information

        with st.container():    # this creates a container for the nutrition information
            st.markdown("<br>", unsafe_allow_html=True)  # br means break, this adds a line break
            st.markdown(
                """
                ### Nutrition Information
                """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)  # this creates two columns for the nutrition information

            with col1:
                st.markdown(f"<p style='margin: 5px 0;'><b>Calories:</b> {calories} kcal</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='margin: 5px 0;'><b>Fat:</b> {fat} g</p>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"<p style='margin: 5px 0;'><b>Carbohydrates:</b> {carbs} g</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='margin: 5px 0;'><b>Protein:</b> {protein} g</p>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("ℹ️  No nutrition information available for this recipe.")
    

def get_wine_pairing_for_food(food_name):   # this function fetches wine pairing suggestions for a specific food item
    url = f"https://api.spoonacular.com/food/wine/pairing?food={food_name}&apiKey={API_KEY_SPOONACULAR}"  # this is the API call that fetches the wine pairing suggestions for a specific food item
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {}  # fallback if the request fails

recipes = [] # this is an empty list that will be used to store the recipes fetched from the API

st.markdown("<br>", unsafe_allow_html=True)  # Add spacing before the checkbox
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this adds a line separator

st.markdown('<p class="subtitle">Customize Your Recipe Search!</p>', unsafe_allow_html=True)    # here the user can customize the recipe search
cuisine = st.selectbox("🥙 Choose a cuisine:", ["Any", "American", "Italian", "Mexican", "Mediterranean", "French", "Indian", "Asian"])
dish_type = st.selectbox("🥘 Choose a dish type:", ["Any", "Appetizer", "Side Dish", "Lunch", "Dinner", "Snack", "Dessert"])

st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this add a line separator
st.markdown('<p class="subtitle">Would you like to have a tasty wine paired to match your meals?</p>', unsafe_allow_html=True) 
get_wine_pairing = st.checkbox("🍷 Include wine pairing suggestions")  # Checkbox for wine pairing suggestions

st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this add a line separator
st.markdown('<p class="subtitle">All set! Just press the button to get your recipes!</p>', unsafe_allow_html=True)
if st.button("🧑🏼‍🍳 Serve the Recipes!"):                                # this button fetches the recipes based on the user's preferences
    
    diet = "" if diet == "None" else diet.lower()
    cuisine = "" if cuisine == "Any" else cuisine.lower()   # this checks if the user selected "Any" for the cuisine, if so, it sets the cuisine to an empty string

    dish_type_map = {               # this is a dictionary that maps the dish type to the API format, as the API uses a different format
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

if recipes:         # this checks if there are any recipes in the list
    
    st.session_state["recipes"] = recipes     # this stores the recipes in the session state, so they can be accessed later
    
else:
    recipes = st.session_state.get("recipes", [])

if recipes:             # this checks if there are any recipes in the list
    st.subheader("Here are some recipes based on your preferences:")
    
    for r in recipes:
        st.text(f"🍽️ {r.get('title')} - Health Score: {r.get('healthScore')}")

    
    if goal == "just eat Healthier :)":     # if the user selected "eat healthier", we filter the recipes based on the health score
        recipes = [r for r in recipes if r.get("healthScore", 0) >= 60]

    if not recipes:
        if goal == "just eat Healthier :)":     
            st.warning("No healthy recipes found with a health score of 60 or more.")
        elif goal.lower() == "build muscle":
            st.warning("No recipes found that meet your muscle-building criteria.")
        else:
            st.warning("No recipes found.")
    
    else:
        shown = 0
        for recipe in recipes:          # this loops through the recipes and displays them
            details = get_recipe_details(recipe["id"], test_mode=test_mode)  # this calls the get_recipe_details function and stores the results in the details variable
            
            if goal == "just eat Healthier :)" and details.get("healthScore", 0) < 60:  # this checks if the recipe has a health score of 60 or more, if not, it skips the recipe
                continue
            
            if goal.lower() == "build muscle":
                protein_raw = next((n for n in details.get("nutrition", {}).get("nutrients", []) if n["name"] == "Protein"), {}).get("amount", 0)

                try:
                    protein = float(protein_raw)
                except (ValueError, TypeError):
                    protein = 0

                if protein < 5:
                    continue

            with st.container():    
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)    # this creates a card for each recipe
                                            
                col1, col2 = st.columns([1, 3])                 # Show title and image upfront, one column for image, one for title
                with col1:
                    st.image(recipe["image"], width=150)
                with col2:
                    st.markdown(f"### {recipe['title']}")
                
                with st.expander("See the ingredients and instructions for this recipe"):   # this creates an expander that shows the ingredients and instructions for the recipe
                    
                    if not details:         # Check if the details are empty (or None)
                        st.error("Could not fetch recipe details for this recipe.")
                        continue 
                    
                    display_recipe_details(details)     # this calls the function that displays the details of the recipe (defined earlier)

                    st.markdown("### Ingredients")      # this shows the ingredients for the recipe
                    ingredients = [f"- {ing['original']}" for ing in details.get("extendedIngredients", [])]    # this gets the ingredients from the recipe details
                    st.write("\n".join(ingredients))    # this displays the ingredients in a list format

                    st.markdown("### Instructions")     # this shows the instructions for the recipe
                    instructions = details.get("analyzedInstructions", [])  # this gets the instructions from the recipe details
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
                                words = recipe.get("title", "").lower().split()     # this splits the title into words and converts it to lowercase
                                keywords = ["chicken", "beef", "salmon", "pasta", "cheese", "steak", "shrimp", "lamb", "pork", "vegetable", "salad", "soup", "pizza", "taco", "burger", "tuna", "mushroom"]
                                main_food = next((word for word in words if word in keywords), "food")  # this checks if any of the words in the title are in the keywords list, if so, it sets the main_food to that word, otherwise it sets it to "food"

                            wine_data = get_wine_pairing_for_food(main_food.lower())    # this calls the function that fetches the wine pairing suggestions for the food item
                            wines = wine_data.get("pairedWines", [])    # this gets the paired wines from the wine data
                            note = wine_data.get("pairingText", "")     # this gets the pairing text from the wine data

                            if wines:
                                st.markdown(
                                    f"<p style='margin: 0;'><b>Suggested Wines:</b> {', '.join(wines)}</p>",
                                    unsafe_allow_html=True
                                )
                                if note:
                                    st.markdown(f"<p style='margin: 0;'>{note}</p>", unsafe_allow_html=True)
                            else:
                                st.markdown("<p style='margin: 0;'><b>Wine Pairing:</b> Not available</p>", unsafe_allow_html=True)

                # this creates a button that allows the user to add the recipe to their calendar 
                with st.form(f"calendar_form_{recipe['id']}"):
                    selected_date = st.date_input(
                        f"📅 Would you like to add this meal to your calendar?",
                        min_value=datetime.date.today()
                    )
                    submitted = st.form_submit_button(f"Save {recipe['title']} to Calendar")

                    if submitted:
                        if "calendar_recipes" not in st.session_state:  # this checks if the calendar_recipes key is in the session state, if not, it creates it
                            st.session_state["calendar_recipes"] = []
                        st.session_state["calendar_recipes"].append({   # this appends the recipe to the calendar_recipes list in the session state
                            "recipe_id": recipe["id"],
                            "recipe_title": recipe["title"],
                            "selected_date": selected_date,
                            "nutrition_info": {                         # this stores the nutrition information for the recipe (used then for the calories page)
                                "calories": details.get("nutrition", {}).get("nutrients", [{}])[0].get("amount"),
                                "carbs": next((n for n in details.get("nutrition", {}).get("nutrients", []) if n["name"] == "Carbohydrates"), {}).get("amount"),
                                "fat": next((n for n in details.get("nutrition", {}).get("nutrients", []) if n["name"] == "Fat"), {}).get("amount"),
                                "protein": next((n for n in details.get("nutrition", {}).get("nutrients", []) if n["name"] == "Protein"), {}).get("amount")
                            }
                        })
                        st.success(f"Recipe {recipe['title']} added to your calendar for {selected_date}")   

                st.markdown('</div>', unsafe_allow_html=True)    # this closes the recipe card div (for the styling) 
            shown += 1

        if shown == 0:
            st.warning("All recipes were filtered out. Try adjusting your filters or checking nutrition info.")
            
else:
    pass

# this is the part that displays the recipes that have been added to the calendar
if "calendar_recipes" in st.session_state and st.session_state["calendar_recipes"]:
    st.subheader("Your Selected Recipes")
    
    # visualize the recipes in the calendar
    for entry in st.session_state["calendar_recipes"]:
        st.write(f"{entry['recipe_title']} on {entry['selected_date']}")
else:
    pass

# this part saves the recipes to a JSON file
def save_to_file():
    if "calendar_recipes" in st.session_state:
        data_to_save = []
        for entry in st.session_state["calendar_recipes"]:
            entry_copy = entry.copy()   # entry.copy() creates a shallow copy of the entry dictionary
            if isinstance(entry_copy["selected_date"], datetime.date):
                entry_copy["selected_date"] = entry_copy["selected_date"].isoformat()  # Convert date to string
            data_to_save.append(entry_copy)

        with open('calendar_recipes.json', 'w') as f:   # this opens the file in write mode
            json.dump(data_to_save, f)      # this saves the recipes to a JSON file

# this part loads the recipes from the JSON file
def load_from_file():
    try:
        with open('calendar_recipes.json', 'r') as f:
            content = f.read()
            if not content.strip():
                return []
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        with open('calendar_recipes.json', 'w') as f:
            json.dump([], f)
        return []  # if the file is empty or not found, return an empty list

def reset_calendar():       # this function resets the calendar by clearing the JSON file and the session state, if the button is pressed
    with open('calendar_recipes.json', 'w') as f:
        json.dump([], f) 

    st.session_state["calendar_recipes"] = []   # this clears the session state

    st.success("✅ Calendar has been reset successfully!")

# add a separator and a title 
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Press the button below to save these recipes to your calendar!</p>', unsafe_allow_html=True)

# this button saves the recipes to a JSON file
if st.button("✅ Save my Recipes!"):
    save_to_file()

# this button resets the calendar by clearing the JSON file and the session state
if st.button("🗑️ Reset Calendar"):
    reset_calendar()

# this part loads the recipes from the JSON file and displays them (so that we can see the recipes that have been saved)
calendar_recipes = load_from_file()

# this part displays the recipes that have been loaded from the JSON file
if calendar_recipes:
    st.subheader("Recipes loaded from the file:")
    for recipe in calendar_recipes:
        st.markdown(f"{recipe['recipe_title']} on {recipe['selected_date']}")

