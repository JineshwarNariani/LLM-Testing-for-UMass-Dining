def clean_dish_name(dish):
    """Extract the dish name before any description."""
    return dish.split(' - ')[0].strip()

def verify_suggestions_location(suggestions, dining_df, expected_location):
    """
    Verify that the suggestions provided by GPT belong to the expected dining hall.

    Parameters:
    - suggestions: String of meal suggestions from GPT.
    - dining_df: DataFrame containing dining information.
    - expected_location: The expected dining hall location.

    Returns:
    - float: Percentage of suggestions that belong to the expected location.
    """
    # Clean the suggestions by removing asterisks
    suggestions = suggestions.replace('**', '').strip()
    
    # Split the suggestions string into individual lines
    lines = suggestions.split('\n')
    
    # Extract only the lines that start with a number (indicating dish suggestions)
    suggested_dishes = [line.strip() for line in lines if line.strip() and line[0].isdigit()]

    correct_count = 0

    # Check if all suggested dishes are in the dining DataFrame with the expected location
    for dish in suggested_dishes:
        dish_name = clean_dish_name(dish.split('. ', 1)[1] if '. ' in dish else dish)
        
        # Check if the dish exists in the dining DataFrame
        matching_rows = dining_df[(dining_df['Dish Name'] == dish_name) & (dining_df['Location'] == expected_location)]
        
        if not matching_rows.empty:
            correct_count += 1

    total_suggestions = len(suggested_dishes)
    accuracy_percentage = (correct_count / total_suggestions) * 100 if total_suggestions > 0 else 0

    return accuracy_percentage

def verify_suggestions_meal_type(suggestions, dining_df, expected_meal_type):
    """
    Verify that the suggestions provided by GPT belong to the expected meal type.
    """
    # Clean the suggestions by removing asterisks
    suggestions = suggestions.replace('**', '').strip()
    
    # Split the suggestions string into individual lines
    lines = suggestions.split('\n')
    
    # Extract only the lines that start with a number (indicating dish suggestions)
    suggested_dishes = [line.strip() for line in lines if line.strip() and line[0].isdigit()]

    correct_count = 0

    # Check if all suggested dishes are in the dining DataFrame with the expected meal type
    for dish in suggested_dishes:
        dish_name = clean_dish_name(dish.split('. ', 1)[1] if '. ' in dish else dish)
        
        # Check if the dish exists in the dining DataFrame
        matching_rows = dining_df[(dining_df['Dish Name'] == dish_name) & (dining_df['Meal'] == expected_meal_type)]
        
        if not matching_rows.empty:
            correct_count += 1

    total_suggestions = len(suggested_dishes)
    accuracy_percentage = (correct_count / total_suggestions) * 100 if total_suggestions > 0 else 0

    return accuracy_percentage

def verify_suggestions_allergens(suggestions, dining_df, expected_allergens):
    """
    Verify that the suggestions provided by GPT belong to the expected dining hall.
    """
    # Clean the suggestions by removing asterisks
    suggestions = suggestions.replace('**', '').strip()
    # Split the suggestions string into individual lines
    lines = suggestions.split('\n')
    
    # Extract only the lines that start with a number (indicating dish suggestions)
    suggested_dishes = [line.strip() for line in lines if line.strip() and line[0].isdigit()]

    # print("Suggested Dishes:", suggested_dishes)  # Debugging line

    correct_count = 0

    # Check if all suggested dishes are in the dining DataFrame with the expected location
    for dish in suggested_dishes:
        dish_name = clean_dish_name(dish.split('. ', 1)[1] if '. ' in dish else dish)
        
        # Check if the dish exists in the dining DataFrame
        matching_rows = dining_df[(dining_df['Dish Name'] == dish_name) & (dining_df['Allergens'].str.contains(expected_allergens, case=False, na=False))]
        print(f"Checking dish: {dish_name}, Matches found: {len(matching_rows)}")  # Debugging line
        
        # If allergens are found, do not count this suggestion as correct
        if not matching_rows.empty:
            correct_count += 1

    total_suggestions = len(suggested_dishes)
    accuracy_percentage = (100 - ((correct_count / total_suggestions) * 100))if total_suggestions > 0 else 0

    return accuracy_percentage

def verify_suggestions_foodtype(suggestions, dining_df, expected_diet):
    """
    Verify that the suggestions provided by GPT belong to the expected dining hall.
    """
    # Clean the suggestions by removing asterisks
    suggestions = suggestions.replace('**', '').strip()
    # Split the suggestions string into individual lines
    lines = suggestions.split('\n')
    
    # Extract only the lines that start with a number (indicating dish suggestions)
    suggested_dishes = [line.strip() for line in lines if line.strip() and line[0].isdigit()]

    correct_count = 0

    for dish in suggested_dishes:
        dish_name = clean_dish_name(dish.split('. ', 1)[1] if '. ' in dish else dish)
        
        # Check if the dish exists in the dining DataFrame
        matching_rows = dining_df[(dining_df['Dish Name'] == dish_name) & (dining_df['Diets'].str.contains(expected_diet, case=False, na=False))]
        # print(f"Checking dish: {dish_name}, Matches found: {len(matching_rows)}")  # Debugging line
        
        if not matching_rows.empty:
            correct_count += 1
    total_suggestions = len(suggested_dishes)
    accuracy_percentage = (correct_count / total_suggestions) * 100 if total_suggestions > 0 else 0

    return accuracy_percentage
