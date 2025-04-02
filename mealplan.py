import streamlit as st
import requests # for API calls

st.title("Meal Plan and Recipes Generator") # this is the title of the web app

API_KEY = "my personal key"                   # this is my personal API key (Spoonacular)

# Function to fetch recipes based on diet and goal
def get_recipes(diet, goal, cuisine):        # this function fetches recipes based on the user's dietary preference and goal

    calorie_ranges = {                       # this is a dictionary that contains the calorie ranges for each goal
        "Eat Healthier": "minCalories=300&maxCalories=700",
        "Lose Weight": "maxCalories=500",
        "Gain Weight": "minCalories=800",
        "None": "minCalories=0&maxCalories=10000"
    }

    goal_calories = calorie_ranges.get(goal, "calories=2000")  # Default to 2000 kcal, so if the user selects "None", the goal_calories is automatically set to 2000 kcal 

    url = f"https://api.spoonacular.com/recipes/complexSearch?diet={diet}&{goal_calories}&cuisine={cuisine}&number=5&apiKey={API_KEY}" # this url fetches recipes from the Spoonacular website based on the user's dietary preference, cuisine and goal

    response = requests.get(url)        # this sends a GET request to the Spoonacular API, based on the url created above (and with the details of the user's preferences)
    if response.status_code == 200:
        return response.json().get("results", [])  # if the code is 200, it means the request was successful and we return the results
    else:
        st.error("Failed to fetch recipes. Check your API key or try again later. You probably have reached the limit of your API key.")
        return []


def get_recipe_details(recipe_id):       # this function fetches the details of a specific recipe based on its ID
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()           # here the function returns the details of the recipe
    else:
        st.error("Failed to fetch recipe details.")
        return {}


st.sidebar.title("Meal Plan and Recipes Generator")  # this is the title of the sidebar (the same as the title of this page in the app)
st.write("Select your dietary preference and goal to get personalized recipes!") 


goal = st.selectbox("Choose your goal:", ["None", "Eat Healthier", "Lose Weight", "Gain Weight"])  # this is the first dropdown menu where the user can select their goal (can only select one option)
diet = st.selectbox("Choose your diet preference:", ["None", "Vegan", "Vegetarian", "Gluten Free", "Diary Free"]) # this is the second dropdown menu where the user can select their dietary preference (can only select one option)
cuisine = st.selectbox("Choose a cuisine:", ["Any", "American", "Italian", "Mexican", "Mediterranean", "French", "Indian", "Asian"]) # this is the third dropdown menu where the user can select their preferred cuisine (can only select one option)

if st.button("Get Recipes"):                                # this is the button that the user clicks to get recipes based on their preferences 
    diet = "" if diet == "None" else diet.lower()           # since there are none and else options, we set the diet to an empty string if the user selects "None"
    goal = "" if goal == "None" else goal.lower()           # same for the goal
    cuisine = "" if cuisine == "Any" else cuisine.lower()   # same for the cuisine
    
    recipes = get_recipes(diet, goal, cuisine)              # this calls the get_recipes function with the user's preferences and stores the results in the recipes variable
    
    if recipes:                                             # this checks if there are any recipes returned from the API
        st.subheader("Here are some recipes for you!")      # if there are, we display this message
        for recipe in recipes:                              # this loops through each recipe in the recipes list and displays the details
            st.subheader(recipe["title"])
            st.image(recipe["image"], width=100)

            recipe_details = get_recipe_details(recipe['id'])   # this calls the get_recipe_details function with the recipe ID and stores the details in the recipe_details variable
            if recipe_details:
                st.write("Ingredients")                         # this displays the ingredients of the recipe
                for ingredient in recipe_details['extendedIngredients']:
                    st.write(f"- {ingredient['original']}")

                st.write("Instructions")                        # this displays the instructions of the recipe 
                for step in recipe_details['analyzedInstructions'][0]['steps']:
                    st.write(f"{step['number']}. {step['step']}")

                st.write("Nutrition")                           # this displays the nutrition facts of the recipe (i haven't found any recipies with nutrition facts yet, so this part could be removed)
                if "nutrition" in recipe_details and "nutrients" in recipe_details["nutrition"]:
                    st.write("Nutrition Facts")
                    for nutrient in recipe_details["nutrition"]["nutrients"]:
                        st.write(f"**{nutrient['name']}**: {nutrient['amount']} {nutrient['unit']}")
                else:
                    st.warning("No nutrition data available for this recipe.")

            else:
                st.warning("Recipe details not found!")     # this appears if the recipe details were not found
    else:                                                     
        st.warning("No recipes found! Try a different combination.")  # this appears if there are no recipes returned from the API

