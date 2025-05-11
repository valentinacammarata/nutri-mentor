# Nutri Mentor

Nutri Mentor is a comprehensive nutritional tracking application designed to help users manage their dietary habits, track their caloric intake, and achieve their health goals. The app provides an intuitive interface for logging meals, viewing nutritional information, and analyzing progress toward personalized goals.

---

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
- Clicking on a date updates the dashboard and displays meals recipes and single manually entered logs for that day.

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

### 8. **Recipes Generator**
- Users can generate meal recipes tailored to their dietary preferences and health goals.
- Recipes are created using external APIs like Spoonacular and USDA FoodData Central.
- Features include:
   - Filtering recipes by ingredients, cuisine, or dietary restrictions.
   - Viewing detailed nutritional information for each recipe.
   - Saving generated recipes directly to the meal log for easy tracking.
- Recipes are accessible through dedicated pages for each meal type (Breakfast, Lunch, Dinner, Snack).

### 9. **Machine Learning Integration**
- Nutri Mentor leverages machine learning to provide personalized insights and recommendations:
   - **Meal Suggestions**: Based on user preferences, past meal logs, and health goals, the app suggests meals that align with dietary targets.
   - **Nutritional Predictions**: Predicts potential deficiencies or excesses in the user's diet based on historical data.
   - **Goal Optimization**: Continuously adjusts recommendations to help users achieve their health goals more effectively.
- Machine learning models are trained using user data stored in JSON files and external datasets from APIs like Spoonacular and USDA FoodData Central.
- The integration is implemented using Python libraries such as `scikit-learn` and `pandas` for data preprocessing and model training.

---

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

---

## How to Use

### 1. **Run the Application**
- Launch the application with:
   ```bash
   streamlit run app.py
   ```
- The application will open in your default web browser.

### 2. **Generate Your Own API Keys**
To enable advanced features like automatic food data retrieval, generate API keys for the following services:

- **USDA FoodData Central**:
   - Visit the [USDA FoodData Central API](https://fdc.nal.usda.gov/api-key-signup.html) page.
   - Sign up for an account and generate your API key.
   - Copy the key and save it securely.

- **Spoonacular**:
   - Go to the [Spoonacular API](https://spoonacular.com/food-api) website.
   - Create an account and navigate to the API section.
   - Generate your API key and store it in a safe location.

Update the application's configuration file or environment variables with these keys.

### 3. **Set Up Your Profile**
- Start by creating your profile in `profilepage.py`.
- Define your health goal and dietary preferences.

### 4. **Generate Recipes**
- Use the Recipes Generator Pages to explore meal ideas tailored to your dietary preferences and health goals.
- Save generated recipes directly to your meal log for easy tracking.

### 5. **Log Your Meals**
- Navigate to the respective meal pages (Breakfast, Lunch, Dinner, Snack) to log your meals.
- Enter the food item and quantity to calculate nutritional values automatically.

### 6. **Track Your Progress**
- Use the `Calories Tracker.py` dashboard to view your daily totals and analyze progress toward your goals.
- Select a date from the calendar to view or edit past entries.

### 7. **Analyze Nutritional Data**
- View detailed nutritional breakdowns and progress charts to stay on track with your health goals.

---

## How to Use the Machine Learning Features

### 1. **Enable Machine Learning**
- Ensure the required Python libraries (`scikit-learn`, `pandas`, `numpy`) are installed:
   ```bash
   pip install scikit-learn pandas numpy
   ```

### 2. **Train the Models**
- Retrain the models by running the `ml_training.py` script:
   ```bash
   python ml_training.py
   ```

### 3. **Access Meal Suggestions**
- Navigate to the **Meal Suggestions** section in the app to receive personalized meal recommendations.

### 4. **View Nutritional Predictions**
- Go to the **Nutritional Predictions** page to see insights about potential deficiencies or excesses in your diet.

### 5. **Optimize Your Goals**
- Use the **Goal Optimization** feature to receive personalized recommendations for adjusting your diet.

---

## Technologies Used

- **Streamlit**: For building the interactive web application.
- **Python**: Backend logic for data processing and calculations.
- **JSON**: For data storage and persistence.
- **Matplotlib**: For generating bar charts and visualizations.
- **CSS**: For custom styling of the app.

---

## Future Enhancements

- Integration with external APIs for automatic food data retrieval.
- Advanced analytics for long-term progress tracking.
- Multi-user support for shared meal planning.
- Mobile-friendly design for on-the-go tracking.

---

## Contributors

- **Laurent**: Internal database and profile management.
- **Dionis**: Meal tracking and nutritional analysis.
- **Daniel**: Calories Tracker Pages.
- **Valentina**: Recipes Generator Pages.

---

## Installed Packages

To run Nutri Mentor, ensure the following Python packages are installed:

- **streamlit**
- **pandas**
- **numpy**
- **matplotlib**
- **requests**
- **datetime**
- **streamlit-multipage**: For switching between different pages in the app.
- **scikit-learn**: For implementing machine learning models.

Install them using:
```bash
pip install streamlit pandas numpy matplotlib requests streamlit-extras
```

Start your journey toward better health with Nutri Mentor today!
