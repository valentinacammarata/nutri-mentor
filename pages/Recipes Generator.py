import streamlit as st
import requests # for API calls
from dotenv import load_dotenv # for loading environment variables
import os
import time # for the spinner effect
import datetime
import json

load_dotenv()  #Load everything from the .env file

API_KEY_SPOONACULAR = os.getenv("API_KEY_SPOONACULAR")

# -------------------- Load user preferences from profile data (JSON file) --------------------
def load_user_preferences():
    try:
        with open('ressources/profile_data.json', 'r') as f:
            data = json.load(f)
            print("Profile data loaded:", data)  # Debug print to see the loaded data
            
            # Ensure 'goals' is not empty before accessing the first element
            goals = data.get("goals", [])
            goal = goals[0] if goals else "None"  # If 'goals' is empty, default to "None"
            
            # Set the diet preference, return "No Preference" if the user has chosen it
            diet = data.get("diet", "No Preference")
            if diet == "No Preference":
                diet = "No Preference"  # Ensure that "No Preference" is explicitly set
            
            return {
                "goal": goal,
                "diet": diet
            }
    except FileNotFoundError:
        return {
            "goal": "None",
            "diet": "No Preference"  # Default diet to "No Preference" if the file is not found
        }

# -------------------- Handle API error responses ---------------------------------------------
def handle_api_error(response):

    if response.status_code == 200:
        return True  # Successful response
    elif response.status_code == 401:
        st.error("Unauthorized access. Please check your API key.")
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

# -------------------- Load the user's preferences (goal and diet) ----------------------------
user_prefs = load_user_preferences()   
diet = user_prefs.get("diet", "None")  
goal = user_prefs.get("goal", "None")  
print("User diet preference:", diet)

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
    if test_mode:       # this is a test mode that uses a local JSON file with fictious recipes instead of the API
        with open('ressources/sample_recipes.json', 'r') as f:
            data = json.load(f)
        return data.get("results", [])
    
    calorie_ranges = {                              # this is a dictionary that contains the filters for each goal
        "just eat Healthier :)": "",       
        "Lose Weight": "maxCalories=500",
        "Build Muscle": "minCalories=600&maxCalories=1000",
        "None": "minCalories=0&maxCalories=10000"
    }

    goal_calories = calorie_ranges.get(goal, "calories=2000")  # Default to 2000 kcal

    url = f"https://api.spoonacular.com/recipes/complexSearch?diet={diet}&{goal_calories}&cuisine={cuisine}&type={dish_type}&sort=healthiness&number=20&addRecipeInformation=true&apiKey={API_KEY_SPOONACULAR}"
    # st.text(f"📡 Requesting: {url}")  # uncomment for debugging

    response = requests.get(url)
    if handle_api_error(response):
        return response.json().get("results", [])  # Request successful, return the results
    else:
        return []   # Request failed, return an empty list

# ------------------ Recipe details functions -------------------------------------------------
def get_recipe_details(recipe_id, test_mode=False):      
    if test_mode:   # this is a test mode that uses a local JSON file instead of the API
        with open('ressources/sample_recipe_details.json', 'r') as f:
            return json.load(f)
        
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=true&apiKey={API_KEY_SPOONACULAR}" 
    
    response = requests.get(url)
    if handle_api_error(response):
        return response.json()  # Request successful, return the recipe details
    else:
        return {}  # Return an empty dictionary if there was an error

# ------------------ Display recipe details functions -----------------------------------------
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

    display_recipe_attributes(details, active_diets)
    display_nutrition_information(details)  
    display_ingredients_and_instructions(details)

# ------------------ Display recipe attributes functions -------------------------------------
def display_recipe_attributes(details, active_diets):
    attributes = [
        ("Ready in", f"{details['readyInMinutes']} min"),
        ("Servings", details['servings']),
        ("Health Score", f"{int(details['healthScore'])} / 100"),
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
    ingredients = [f"- {ing['original']}" for ing in details.get("extendedIngredients", [])]
    st.write("\n".join(ingredients))

    st.markdown("### Instructions")
    instructions = details.get("analyzedInstructions", [])
    if instructions:
        steps = [f"{step['number']}. {step['step']}" for step in instructions[0].get("steps", [])]
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
    print("Diet preference before processing:", diet)  # Debug the incoming diet

    # Only add diet to the request if it's not empty (no preference)
    if not diet:  # If diet is empty (""), we exclude it from the request
        print("No diet preference set. Removing diet filter.")  # Debug message
        diet = ""  # Don't include the diet filter in the request
    else:
        diet = diet.lower()  # Otherwise, use the specified diet
        print("Using diet filter:", diet)  # Debug message

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
        recipes = [r for r in recipes if float(next((n for n in r.get("nutrition", {}).get("nutrients", []) if n["name"] == "Protein"), {}).get("amount", 0)) >= 5]
    return recipes

# ------------------ Display recipe functions ------------------------------------------------
def display_recipe(recipe, details, get_wine_pairing):
    with st.container():
        st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])  # Show image and title
        with col1:
            st.image(recipe["image"], width=150)
        with col2:
            st.markdown(f"### {recipe['title']}")
        
        # Expander to show ingredients and instructions
        with st.expander("See the ingredients and instructions for this recipe"):
            if not details:
                st.error("Could not fetch recipe details for this recipe.")
            else:
                display_recipe_details(details)  # Assuming this function is already defined elsewhere
                
                # Display wine pairing if selected
                if get_wine_pairing:
                    display_wine_pairing(recipe, details)

        # Calendar form to add the recipe to a calendar
        with st.form(f"calendar_form_{recipe['id']}"):
            selected_date = st.date_input(f"📅 Add to calendar?", min_value=datetime.date.today())
            meal_category = st.selectbox(
                "Choose the meal category:",
                ["Breakfast", "Lunch", "Dinner", "Snack"]
            )

            submitted = st.form_submit_button(f"Save {recipe['title']} to Calendar")
    
            if submitted:
                st.write("Form submitted!")  # Debug message to ensure the form submit is triggered
                save_recipe_to_calendar(recipe, details, selected_date, meal_category)  # Call function to save recipe
                st.success(f"{recipe['title']} saved to your calendar!")  # Confirmation message after saving

        st.markdown('</div>', unsafe_allow_html=True)

# ------------------ Display wine pairing functions ----------------------------------------
def display_wine_pairing(recipe, details):
    # Try to extract main food for wine pairing
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
def save_recipe_to_calendar(recipe, details, selected_date, meal_category):
    # Ensure the session state exists for calendar_recipes
    if "calendar_recipes" not in st.session_state:
        st.session_state["calendar_recipes"] = []  # Initialize if not already done
    
    # Debugging: Output session state before adding to calendar
    st.write(f"Session state before adding to calendar: {st.session_state['calendar_recipes']}")  # Debugging
    
    # Add the selected recipe to the calendar
    st.session_state["calendar_recipes"].append({
        "recipe_id": recipe["id"],
        "recipe_title": recipe["title"],
        "selected_date": selected_date,
        "meal_category": meal_category,
        "nutrition_info": {
            "calories": details.get("nutrition", {}).get("nutrients", [{}])[0].get("amount"),
            "carbs": next((n for n in details.get("nutrition", {}).get("nutrients", []) if n["name"] == "Carbohydrates"), {}).get("amount"),
            "fat": next((n for n in details.get("nutrition", {}).get("nutrients", []) if n["name"] == "Fat"), {}).get("amount"),
            "protein": next((n for n in details.get("nutrition", {}).get("nutrients", []) if n["name"] == "Protein"), {}).get("amount")
        }
    })
    
    # Debugging: Output session state after adding to calendar
    st.write(f"Session state after adding to calendar: {st.session_state['calendar_recipes']}")  # Debugging

# ------------------ Display calendar recipes functions -----------------------------------
def display_calendar_recipes():
    if "calendar_recipes" in st.session_state and st.session_state["calendar_recipes"]:
        st.subheader("Your Selected Recipes")
        for entry in st.session_state["calendar_recipes"]:
            st.write(f"{entry['recipe_title']} on {entry['selected_date']}")
    else:
        st.info("No recipes added to the calendar.")

# ------------------- Save and load recipes functions --------------------------------------
def save_to_file():
    if "calendar_recipes" in st.session_state:
        recipes = st.session_state["calendar_recipes"]
        
        if recipes:
            # Debugging: Show what is being saved
            st.write(f"Saving the following recipes to the file: {recipes}")
            
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
            
            # Debug: Print file content
            print("Loaded from file:", content)  # Check what’s being loaded
            
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

if "recipes" not in st.session_state:
    st.session_state["recipes"] = []  # Initialize the recipes state

if "calendar_recipes" not in st.session_state:
    st.session_state["calendar_recipes"] = []  # Initialize the calendar state

if st.button("🧑🏼‍🍳 Serve the Recipes!"):
    st.write("Button pressed!")  # Debug message to check if the button press is detected
    
    # Ensure session state is initialized
    st.write(f"Session state before serving recipes: {st.session_state}")  # Output session state

    diet, goal, cuisine, dish_type = get_api_params(diet, goal, cuisine, dish_type)
    with st.spinner("Cooking up some recipes... 🍽️"):
        time.sleep(2)  # Simulate API request delay
        recipes = get_recipes(diet, goal, cuisine, dish_type, test_mode=test_mode)

    st.write(f"Recipes fetched: {len(recipes)}")  # Output number of recipes fetched

    if recipes:
        st.session_state["recipes"] = recipes
    else:
        recipes = st.session_state.get("recipes", [])
        st.write(f"Recipes in session_state: {len(recipes)}")

    if recipes:
        st.subheader("Here are some recipes based on your preferences:")
        for recipe in recipes:
            details = get_recipe_details(recipe["id"], test_mode=test_mode)
            display_recipe(recipe, details, get_wine_pairing)
    else:
        st.warning("No recipes found. Please adjust your filters.")

# ------------------ Display selected recipes in the calendar -----------------------------
if "calendar_recipes" in st.session_state and st.session_state["calendar_recipes"]:
    st.subheader("Your Selected Recipes")
    for entry in st.session_state["calendar_recipes"]:
        st.write(f"{entry['recipe_title']} on {entry['selected_date']} as {entry['meal_category']}")
else:
    st.info("No recipes added to your calendar yet.")

# ------------------ Save and load recipes to/from file -----------------------------------

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Press the button below to save these recipes to your calendar!</p>', unsafe_allow_html=True)

if st.button("✅ Save my Recipes!"):
    save_to_file()

if st.button("🗑️ Reset Calendar"):
    reset_calendar()

# Load calendar recipes from session state or file, if necessary
calendar_recipes = st.session_state.get("calendar_recipes", [])
if calendar_recipes:
    st.subheader("Your Selected Recipes")
    for entry in calendar_recipes:
        st.write(f"{entry['recipe_title']} on {entry['selected_date']}")
else:
    st.info("No recipes found in the file.")

# ------------------ Button to navigate to the Calories Tracker page ----------------------
st.markdown('<p class="subtitle">Press the button below to track the calories of your meals!</p>', unsafe_allow_html=True)
if st.button("📊 Go to Calories Tracker"):
        st.switch_page("pages/Calories Tracker.py")