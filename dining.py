import requests
import urllib.parse
import pandas as pd
from bs4 import BeautifulSoup

def fetch_location_data():
    """Fetch location data from the UMass Dining API."""
    url = 'https://www.umassdining.com/uapp/get_infov2'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch data from the Dining API.")

def parse_ingredients(ingredients):
    """Parse the ingredients list to handle nested parentheses and split into a list."""
    if not ingredients:
        return []
    result = []
    buffer = ''
    nested = 0
    for char in ingredients:
        if char == ',' and nested == 0:
            result.append(buffer.strip())
            buffer = ''
        else:
            buffer += char
            if char == '(':
                nested += 1
            elif char == ')':
                nested -= 1
    if buffer:
        result.append(buffer.strip())
    return result

def parse_menu_html(html_string, meal):
    """Parse the menu HTML string and extract relevant dish information."""
    default_costs = {'breakfast': 12.00, 'lunch': 16.25, 'dinner': 19.25}
    soup = BeautifulSoup(html_string, 'html.parser')
    items = soup.find_all('a', href='#inline')
    dishes = []
    for item in items:
        cost = item.get('data-price')
        cost = float(cost) if cost and cost != 'N/A' else default_costs.get(meal, 'N/A')
        dish = {
            'name': item.text.strip(),
            'meal': meal,
            'diets': item.get('data-clean-diet-str', '').split(', ') if item.get('data-clean-diet-str') else [],
            'allergens': parse_ingredients(item.get('data-allergens', '')),
            'cost': cost,
            'calories': int(item.get('data-calories')),
            'protein': float(item.get('data-protein', '0').replace('g', '')) if item.get('data-protein') else 0,
            'fiber': float(item.get('data-dietary-fiber', '0').replace('g', '')) if item.get('data-dietary-fiber') else None,
            'sugar': float(item.get('data-sugars', '0').replace('g', '')) if item.get('data-sugars') else None,
            'saturated_fat': float(item.get('data-sat-fat', '0').replace('g', '')) if item.get('data-sat-fat') else None,
            'sodium': float(item.get('data-sodium', '0').replace('mg', '')) if item.get('data-sodium') else None  
        }
        dishes.append(dish)
    return dishes

def fetch_menu(location_id):
    """Fetch the menu for a given location."""
    base_url = 'https://umassdining.com/foodpro-menu-ajax'
    params = {'tid': location_id}
    request_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    try:
        response = requests.get(request_url)
        response.raise_for_status()
        menu_data = response.json()
        # print(menu_data)
        menu_by_meal = {}
        for meal, categories in menu_data.items():
            dishes = []
            for category_html in categories.values():
                dishes.extend(parse_menu_html(category_html, meal))
            menu_by_meal[meal] = dishes
        return menu_by_meal
    except Exception:
        return {}

def get_dining_info():
    """Main function to fetch and organize dining information."""
    locations_data = fetch_location_data()
    dining_info = []
    for location in locations_data:
        if location['opening_hours'] == 'Closed' or location['closing_hours'] == 'Closed':
            continue
        location_info = {'name': location['location_title'], 'menu': fetch_menu(location['location_id'])}
        dining_info.append(location_info)
    return dining_info

def print_dining_info(dining_info):
    """Print the formatted dining information."""
    for location in dining_info:
        print(f"Location: {location['name']}")
        for meal, dishes in location['menu'].items():
            print(f"  {meal.capitalize()}:")
            for dish in dishes:
                print(f"    - {dish['name']}")
                if dish['calories'] is not None:
                    print(f"      Calories: {dish['calories']} kcal")
                if dish['cost'] != 'N/A':
                    print(f"      Cost: ${dish['cost']:.2f}")
                if dish['diets']:
                    print(f"      Diets: {', '.join(dish['diets'])}")
                if dish['allergens']:
                    print(f"      Allergens: {', '.join(dish['allergens'])}")
        print("\n")


def create_dining_dataframe(dining_info):
    """Create a pandas DataFrame from the dining information."""
    data = []
    for location in dining_info:
        location_name = location['name']
        for meal, dishes in location['menu'].items():
            for dish in dishes:
                # Add a dictionary for each dish
                data.append({
                    'Location': location_name,
                    'Meal': meal.capitalize(),
                    'Dish Name': dish['name'],
                    'Cost ($)': dish['cost'] if dish['cost'] != 'N/A' else None,
                    'Calories (kcal)': dish['calories'],
                    'Diets': ', '.join(dish['diets']) if dish['diets'] else None,
                    'Allergens': ', '.join(dish['allergens']) if dish['allergens'] else None,
                    'Protein (g)': dish['protein'] if dish['protein'] else 0.0,
                    'Dietary Fiber (g)': dish['fiber'] if dish['fiber'] else 0.0,
                    'Sugars (g)': dish['sugar'] if dish['sugar'] else 0.0,
                    'Saturated Fat (g)': dish['saturated_fat'] if dish['saturated_fat'] else 0.0,
                    'Sodium (mg)': dish['sodium'] if dish['sodium'] else 0.0
                    
                })
    # Create a pandas DataFrame
    return pd.DataFrame(data)

def calculate_nutrient_score(row):
    """
    Calculate a nutrient score for a given row of dish data. This is a basic idea of the score generation wher protein, dietary fiber is
    considered positive  and sugar, high calories, high sodium and saturated fat is considered as negative weights 
    """
    # Nutrient weights
    protein_weight = 2
    fiber_weight = 3
    sat_fat_weight = -1
    sugar_weight = -1
    sodium_weight = -0.01  # Scale down for mg
    calorie_weight = -0.1

    # Extract nutrients
    protein = row['Protein (g)'] or 0
    fiber = row['Dietary Fiber (g)'] or 0
    sat_fat = row['Saturated Fat (g)'] or 0
    sugar = row['Sugars (g)'] or 0
    sodium = row['Sodium (mg)'] or 0
    calories = row['Calories (kcal)'] or 0

    # Compute nutrient score
    score = (
        protein_weight * protein +
        fiber_weight * fiber +
        sat_fat_weight * sat_fat +
        sugar_weight * sugar +
        sodium_weight * sodium +
        calorie_weight * calories
    )
    return score

def add_nutrient_scores_to_dataframe(df):
    """Add nutrient scores to the DataFrame."""
    df['Nutrient Score'] = df.apply(calculate_nutrient_score, axis=1)
    return df


if __name__ == "__main__":
    try:
        dining_info = get_dining_info()
        dining_df = create_dining_dataframe(dining_info)
        dining_df = add_nutrient_scores_to_dataframe(dining_df)
        print("Dataset saved as 'dining_info_scores.csv'")
        dining_df.to_csv('dining_info_scores.csv', index=False)

        # print(dining_df)
        dining_df.sort_values(by='Nutrient Score', ascending=False,inplace=True)
        print(dining_df)

    # print_dining_info(dining_info)
    except Exception as e:
        print(f"Error: {e}")
