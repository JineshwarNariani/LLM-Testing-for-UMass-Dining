import openai
import pandas as pd
import os
import subprocess
from datetime import datetime
from verification import (
    verify_suggestions_location,
    verify_suggestions_meal_type,
    verify_suggestions_allergens,
    verify_suggestions_foodtype
)
# run the other file while running this
subprocess.run(["python3", "dining.py"])
openai.api_key = os.getenv("OPENAI_KEY")

# //run the api key as an env variable


def filter_meals(df, location ):
    """
    Filter meals based on user preferences.
    """
    filtered_df = df[
        df['Location'].str.contains(location,case=False,na=False)  ]
    return filtered_df

def generate_suggestionsprompt1(filtered_meals, diet, location, allergens, time=0):
    """
    Use ChatGPT to generate meal suggestions.
    """
    # Prepare data for the prompt
    meals_list1 = filtered_meals[['Dish Name', 'Location', 'Meal']].to_dict(orient="records")

    # Construct the prompt
    if time == 0:
        prompt = (
            f"Based on the following meal data and the current time in Amherst, MA, USA:\n{meals_list1}\n"
            f"Suggest 5 meals suitable for a {diet} diet available at {location}, avoiding {allergens} allergens for the current suitable meal category according to the current time in Amherst, MA, USA."
        )
    else:
        prompt = (
            f"Based on the following meal data and the current time: {time} in Amherst, MA, USA:\n{meals_list1}\n"
            f"Suggest 5 meals suitable for a {diet} diet available at {location}, avoiding {allergens} allergens for the current suitable meal category according to the current time in Amherst, MA, USA."
        )

    # Call OpenAI API
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.7
    )

    # Return the response, stripping the asterisks
    return response.choices[0].message.content.strip('* ')

def generate_suggestionsprompt2(dining_inf, diet, location, allergens, time):
    """
    Ask GPT to identify the nearest dining hall based on user's location.
    """
    # Extract the list of unique dining hall locations
    unique_locations = dining_inf['Location'].unique().tolist()
    
    # Construct the prompt for GPT to find the nearest dining hall
    prompt = (
        f"I am currently at {location} in Amherst, MA. Based on the following dining hall locations:\n"
        f"{unique_locations}\n"
        f"Please identify the nearest dining hall to my location and name only one dining hall just the name no other sentence."
    )

    # Call OpenAI API to get the response
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that helps users locate dining halls."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,
        temperature=0.3
    )
    
    # Extract the location name from GPT's response
    nearest_location = response.choices[0].message.content.strip()
    return generate_suggestionsprompt1(dining_inf, diet, nearest_location, allergens, time)
    
if __name__ == "__main__":
    # Collect user inputs
    #Prompt 1 - we are checking for time awareness - removing the locationf sactor
    #Prompt 2 - all of dining halls only of dinner - is it giving us right locaiton specific meals
    #Prompts 3- accurate information - time awareness and halal diet
    dining_df = pd.read_csv("dining_info_scores.csv")

    # creating a dining hall of only DCs
    locations_to_keep = [
        "Hampshire Dining Commons",
        "Berkshire Dining Commons",
        "Franklin Dining Commons",
        "Worcester Commons"
    ]

    # Filter the DataFrame- to only keep Dcs
    diningdc_df = dining_df[dining_df['Location'].isin(locations_to_keep)]

    location_accuracy = 0  # Initialize accuracy to a default value
    meal_type_accuracy = 0
    allergen_accuracy = 0
    food_type_accuracy = 0

    user_diet = input("What food type do you want? (e.g., Vegan): ").strip()
    user_location = input("Which is your location: ").strip()
    user_allergens = input("Do you have any allergens? (e.g., Gluten): ").strip()
    
    #Start of Prompt 1 filter meals with one specific dining hall
    # Filter meals - chedcks if we can filter the json of all dining dcs to one dining dc
    filtered_meals = filter_meals(diningdc_df, user_location)

    if filtered_meals.empty:
        print("\nNo meals found for your location. Finding the nearest dining hall...")
        suggestions2 = generate_suggestionsprompt2(diningdc_df, user_diet, user_location, user_allergens, datetime.now().time())

        print("\nMeal Suggestions:\n")
        print(suggestions2)
        expected_allergens = user_allergens
        expected_diet = user_diet
        allergen_accuracy = verify_suggestions_allergens(suggestions2, diningdc_df, expected_allergens)
        food_type_accuracy = verify_suggestions_foodtype(suggestions2, diningdc_df, expected_diet)
    else:
        # only 1 dining Hall 
        # Generate meal suggestions using ChatGPT
        suggestions = generate_suggestionsprompt1(filtered_meals, user_diet, user_location, user_allergens, datetime.now().time())
        print("\nMeal Suggestions:\n")
        print(suggestions)

        # Assuming 'suggestions' is the output from generate_suggestions
        expected_location = "Franklin Dining Commons"  # e.g., "Franklin Dining Hall"
        expected_meal_type = "Dinner"
        expected_allergens = user_allergens
        expected_diet = user_diet


        location_accuracy = verify_suggestions_location(suggestions, diningdc_df, expected_location)
        meal_type_accuracy = verify_suggestions_meal_type(suggestions, diningdc_df, expected_meal_type)
        allergen_accuracy = verify_suggestions_allergens(suggestions, diningdc_df, expected_allergens)
        food_type_accuracy = verify_suggestions_foodtype(suggestions, diningdc_df, expected_diet)
        
    print(f"Location Accuracy: {location_accuracy:.2f}%")
    print(f"Meal Type Accuracy: {meal_type_accuracy:.2f}%")
    print(f"Allergen Accuracy: {allergen_accuracy:.2f}%")
    print(f"Food Type Accuracy: {food_type_accuracy:.2f}%")
