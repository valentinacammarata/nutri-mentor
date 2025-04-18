import streamlit as st
import requests # for API calls
from dotenv import load_dotenv # for loading environment variables
import os

load_dotenv()  # This loads everything from the .env file

with open("styles.css") as f:       # this loads the CSS file that contains the styles for the app 
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

API_KEY = os.getenv("API_KEY")  # This grabs the key from the .env file

# This sets the title, description and separator according to the styles defined in the CSS file
st.markdown('<p class="title">Discover Recipies Based on Your Preferences</p>', unsafe_allow_html=True) # this is the title of the app: displays the title with custom CSS applied (through the class="title") and defined in the CSS file -> <p> is a paragraph tag and is used for inline text elements
st.markdown('<div class="description">Welcome! Discover delicious recipes tailored to your dietary goals, preferences, and cuisine choices. Get cooking today!</p>', unsafe_allow_html=True)
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this add a line separator

def get_recipes(diet, goal, cuisine, dish_type):    # this function fetches recipes based on the user's dietary preference and goal

    calorie_ranges = {                              # this is a dictionary that contains the filters for each goal
        "Eat Healthier": "minHealthScore=80",       # for eat healthier, we take the healht score given by the API
        "Lose Weight": "maxCalories=500",
        "Gain Weight": "minCalories=800",
        "None": "minCalories=0&maxCalories=10000"
    }

    goal_calories = calorie_ranges.get(goal, "calories=2000")  # Default to 2000 kcal, so if the user selects "None", the goal_calories is automatically set to 2000 kcal 

    url = f"https://api.spoonacular.com/recipes/complexSearch?diet={diet}&{goal_calories}&cuisine={cuisine}&type={dish_type}&number=5&apiKey={API_KEY}" # this url fetches recipes from the Spoonacular website based on the user's dietary preference, cuisine and goal

    response = requests.get(url)        # this sends a GET request to the Spoonacular API, based on the url created above (and with the details of the user's preferences)
    if response.status_code == 200:
        return response.json().get("results", [])  # if the code is 200, it means the request was successful and we return the results
    else:
        st.error("Failed to fetch recipes. You have probably reached the limit of your API key, try again tomorrow.")
        return []


def get_recipe_details(recipe_id):      # this function fetches the details of a specific recipe based on its ID
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}" # this url fetches the details of a specific recipe based on its ID
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()           # here the function returns the details of the recipe
    else:
        st.error("Failed to fetch recipe details.")
        return {}

def display_recipe_details(details):            # this function displays the details of a specific recipe, this replaces a lot of the code in the main function
    attributes = [
        ("Ready in", f"{details['readyInMinutes']} min"),
        ("Servings", details['servings']),
        ("Health Score", f"{int(details['healthScore'])} / 100"),
        ("Price per serving", f"{details['pricePerServing'] / 100:.2f} €"),
        ("Dish Type", ', '.join(details.get('dishTypes', [])))
    ]
    
    for label, value in attributes:     # this loops through the attributes of the recipe and displays them
        st.markdown(f"<p style='margin: 0;'><b>{label}:</b> {value}</p>", unsafe_allow_html=True)

recipes = [] # this is an empty list that will be used to store the recipes fetched from the API

st.markdown('<p class="subtitle">Your Preferences</p>', unsafe_allow_html=True) 
st.markdown("<br>", unsafe_allow_html=True)  # Add spacing before the checkbox
st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this add a line separator

st.markdown('<p class="subtitle">Customize Your Recipe Search!</p>', unsafe_allow_html=True)
goal = st.selectbox("🎯 Choose your goal:", ["None", "Eat Healthier", "Lose Weight", "Gain Weight"]) 
diet = st.selectbox("🥗 Choose your diet preference:", ["None", "Vegan", "Vegetarian", "Gluten Free", "Diary Free"])
cuisine = st.selectbox("🥙 Choose a cuisine:", ["Any", "American", "Italian", "Mexican", "Mediterranean", "French", "Indian", "Asian"])
dish_type = st.selectbox("🥘 Choose a dish type:", ["Any", "Appetizer", "Side Dish", "Lunch", "Dinner", "Snack", "Dessert"])

st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this add a line separator
st.markdown('<p class="subtitle">Would you like to have a tasty wine paired to match your meals?</p>', unsafe_allow_html=True) 
get_wine_pairing = st.checkbox("🍷 Include wine pairing suggestions")  # Checkbox for wine pairing suggestions

st.markdown('<div class="separator"></div>', unsafe_allow_html=True) # this add a line separator
st.markdown('<p class="subtitle">All set! Just press the button to get your recipies!</p>', unsafe_allow_html=True)
if st.button("🧑🏼‍🍳 Serve the Recipies!"):                                # this button fetches the recipes based on the user's preferences
    diet = "" if diet == "None" else diet.lower()
    goal = "" if goal == "None" else goal.lower()
    cuisine = "" if cuisine == "Any" else cuisine.lower()
    dish_type = "" if dish_type == "Any" else dish_type.lower()

    with st.spinner("Cooking up some recipes... 🍽️"):           # this shows a loading spinner while recipies are fetched
        recipes = get_recipes(diet, goal, cuisine, dish_type)   # this calls the get_recipes function and stores the results in the recipes list
    
    st.session_state["recipes"] = recipes     
    
else:
    recipes = st.session_state.get("recipes", [])

if recipes:                                                 # this checks if there are any recipes in the list
    st.subheader("Here are some recipes based on your preferences:")
    for recipe in recipes:                                  # this loops through the recipes and displays them
        with st.container():    
            st.markdown('<div class="recipe-card">', unsafe_allow_html=True)    # this creates a card for each recipe (for the styling)
                                            
            col1, col2 = st.columns([1, 3])                 # Show title and image upfront
            with col1:
                st.image(recipe["image"], width=150)
            with col2:
                st.markdown(f"### {recipe['title']}")

            with st.expander("See the ingredients and instructions for this recipe"):   # this creates an expander that shows the ingredients and instructions for the recipe
                details = get_recipe_details(recipe["id"])

                if details:         # this includes the details (ingredients and instructions) of the recipe
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

                    diet_flags = {                  # this creates a dictionary that contains the diet flags for the recipe
                        "Vegetarian": details.get("vegetarian"),
                        "Vegan": details.get("vegan"),
                        "Gluten-Free": details.get("glutenFree"),
                        "Dairy-Free": details.get("dairyFree"),
                        "Healthy": details.get("veryHealthy"),
                        "Cheap": details.get("cheap"),
                        "Sustainable": details.get("sustainable"),
                        "Popular": details.get("veryPopular")
                    }

                    active_diets = [key for key, value in diet_flags.items() if value]     # this creates a list of the active diet flags for the recipe

                    st.markdown(                    # this shows the active diet flags for the recipe
                        f"<p style='margin: 0;'><b>Tags:</b> {', '.join(active_diets) if active_diets else 'None'}</p>",
                        unsafe_allow_html=True
                    )

                    # Optional Wine Pairing: if a user selects the checkbox, wine pairing suggestions are loaded and displayed below the recipe
                    if get_wine_pairing:
                        wine_info = details.get("winePairing", {})
                        wines = wine_info.get("pairedWines", [])
                        note = wine_info.get("pairingText", "")     # note: this is the text that describes the wine pairing

                        if wines:
                            st.markdown(
                                f"<p style='margin: 0;'><b>Suggested Wines:</b> {', '.join(wines)}</p>",
                                unsafe_allow_html=True
                            )
                            if note:        # if there is text that describes the wine pairing, it is displayed below the suggested wines
                                st.markdown(f"<p style='margin: 0;'>{note}</p>", unsafe_allow_html=True)
                        else:
                            st.markdown("<p style='margin: 0;'><b>Wine Pairing:</b> Not available</p>", unsafe_allow_html=True)    
                else:
                    st.error("Could not load recipe details.")
                
            st.markdown('</div>', unsafe_allow_html=True)    # this closes the recipe card div (for the styling)
else:
    st.empty ()  # this shows an empty space if there are no recipes in the list