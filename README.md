# Nutri-Mentor

Nutri-Mentor is a comprehensive nutritional tracking application designed to help users manage their dietary habits, track their caloric intake, and achieve their health goals. The app provides an intuitive interface for logging meals, viewing nutritional information, and analyzing progress toward personalized goals.

## Features

### 1. **Profile Management**
   - Users can create and manage their profiles through `profilepage.py`.
   - Profiles store essential information such as dietary preferences, health goals (e.g., "Build Muscle", "Lose Weight"), and daily caloric targets.
   - This information is used across the app to personalize recommendations and track progress.

### 2. **Meal Tracking**
   - Log meals for **Breakfast**, **Lunch**, **Dinner**, and **Snacks**.
   - Each meal entry includes:
     - Food item name
     - Quantity (grams or milliliters)
     - Automatically calculated nutritional values (calories, protein, fat, carbohydrates).
   - Meals are saved to an internal database (`calendar_recipes.json`) for future reference.

### 3. **Daily Dashboard**
   - The `Calories Tracker.py` page serves as the central dashboard.
   - Users can:
     - View total nutritional intake for a selected date.
     - Analyze progress toward their health goals using bar charts and circular progress indicators.
     - Navigate between meal categories (Breakfast, Lunch, Dinner, Snack) to view detailed entries.

### 4. **Calendar Integration**
   - A visual calendar allows users to select specific dates and view or edit meal entries for that day.
   - Clicking on a date updates the dashboard and displays meals recipes and single manually entries logged for that day.

### 5. **Nutritional Analysis**
   - Nutritional values are displayed in an easy-to-read format, including:
     - Total calories
     - Macronutrient breakdown (protein, fat, carbohydrates).
   - Bar charts dynamically adjust to user-defined goals, showing progress toward daily targets.

### 6. **Goal-Based Recommendations**
   - The app supports three primary health goals:
     - **Build Muscle**: Higher caloric and protein targets.
     - **Lose Weight**: Lower caloric intake with balanced macronutrients.
     - **Just Eat Healthier**: Moderate caloric intake with balanced macronutrients.
   - Goals are loaded from `profile_data.json` and used to set maximum values for charts and progress tracking.

### 7. **Data Persistence**
   - All user data, including profiles and meal entries, is stored in JSON files:
     - `profile_data.json`: Stores user profile and goal information.
     - `calendar_recipes.json`: Stores meal entries categorized by date and meal type.

## File Structure

- **`profilepage.py`**: Handles user profile creation and management.
- **`Calories Tracker.py`**: Main dashboard for viewing and managing daily nutritional intake.
- **`Calories Tracker - Breakfast.py`**: Page for logging and viewing breakfast entries.
- **`Calories Tracker - Lunch.py`**: Page for logging and viewing lunch entries.
- **`Calories Tracker - Dinner.py`**: Page for logging and viewing dinner entries.
- **`Calories Tracker - Snack.py`**: Page for logging and viewing snack entries.
- **`ressources/profile_data.json`**: Stores user profile and goal information.
- **`ressources/calendar_recipes.json`**: Stores meal entries categorized by date and meal type.
- **`ressources/styles.css`**: Custom CSS for styling the app.

## How to Use

0. **Run the application with 'streamlit run app.py'**
    - The application will launch in your default web browser.
    ### Generate Your Own API Keys

    To enable advanced features like automatic food data retrieval, you need to generate your own API keys for the following services:

     **USDA FoodData Central**:
        - Visit the [USDA FoodData Central API](https://fdc.nal.usda.gov/api-key-signup.html) page.
        - Sign up for an account and generate your API key.
        - Copy the key and save it securely.

     **Spoonacular**:
        - Go to the [Spoonacular API](https://spoonacular.com/food-api) website.
        - Create an account and navigate to the API section.
        - Generate your API key and store it in a safe location.

    Once you have your API keys, update the application's configuration file or environment variables to integrate these services seamlessly.


    1. **Run the application with**
        - Lunch the application with **streamlit run `app.py`**
        - The application will launch in your default web browser.

    2. **Set Up Your Profile**:
        - Start by creating your profile in `profilepage.py`.
        - Define your health goal and dietary preferences.

    3. **Generate Recipes**:  
        - Use the Recipes Generator Pages to explore meal ideas tailored to your dietary preferences and health goals.  
        - Recipes are generated based on the nutritional targets defined in your profile.  
        - Save generated recipes directly to your meal log for easy tracking.

    4. **Log Your Meals**: 
        - Navigate to the respective meal pages (Breakfast, Lunch, Dinner, Snack) to log your meals.
        - Enter the food item and quantity to calculate nutritional values automatically.

    5. **Track Your Progress**:
        - Use the `Calories Tracker.py` dashboard to view your daily totals and analyze progress toward your goals.
        - Select a date from the calendar to view or edit past entries.

    6. **Analyze Nutritional Data**:
        - View detailed nutritional breakdowns and progress charts to stay on track with your health goals. - View detailed nutritional breakdowns and progress charts to stay on track with your health goals.

## Technologies Used

- **Streamlit**: For building the interactive web application.
- **Python**: Backend logic for data processing and calculations.
- **JSON**: For data storage and persistence.
- **Matplotlib**: For generating bar charts and visualizations.
- **CSS**: For custom styling of the app.

## Future Enhancements

- Integration with external APIs for automatic food data retrieval.
- Advanced analytics for long-term progress tracking.
- Multi-user support for shared meal planning.
- Mobile-friendly design for on-the-go tracking.

## Contributors

- **Laurent**: Internal database and profile management.
- **Dionis**: Meal tracking and nutritional analysis.
- **Daniel**: Calories Tracker Pages
- **Valentina**: Recipes Generator Pages

---

## Installed Packages

To run Nutri-Mentor, ensure the following Python packages are installed:

- **streamlit**: For building the interactive web application.
- **pandas**: For data manipulation and analysis.
- **numpy**: For numerical computations.
- **matplotlib**: For creating visualizations and charts.
- **json**: For handling data storage and retrieval.
- **requests**: For making API calls to external services.
- **datetime**: For managing date and time operations.

You can install these packages using the following command:

```bash
pip install streamlit pandas numpy matplotlib requests
pip install streamlit-extras


Start your journey toward better health with Nutri-Mentor today!