from flask import Flask, render_template, request
import pandas as pd
import random

app = Flask(__name__)

csv_file_path = "data/recipe.csv"
data = pd.read_csv(csv_file_path)
redundant_words = ["loaf", "roughly", "freshly", "packed", "pack", "cloves", "optional", "extra", "one", "mix", "if", "in", "use", "serving", "on", "slices", "fl", "jar", "at", 'freshly', 'finishing', 'ounce', 'can', 'like', 'into', 'dals', 'for', 'piece', 'dal', 'fresh', 'of', 'hot', 'or', 'and', 'cut', 'to', 'pieces', 'cups', 'cup', 'more', 'about', 'such', 'as', 'divided', 'the', 'a', 'total', 'new', 'diameter', 'finely', 'pound', 'inch', 'teaspoons', 'teaspoon', 'tsp.', 'tsp', 'tablespoon', 'tbsp', 'tbsp.', 'tablespoons', 'tablespoon', 'ounces', 'oz.', 'pounds', 'lbs.', 'lb', 'grams', 'g', 'kilograms', 'kg', 'liters', 'litres', 'l', 'milliliters', 'millilitres', 'ml', 'oz', 'quarts', 'qts.', 'cups', 'c.', 'pints', 'pts.', 'fl. oz.', 'fluid ounces', 'ml', 'numbers', 'small', 'medium', 'large', 'chopped', 'minced', 'sliced', 'diced', 'peeled', 'grated', 'shredded', 'crushed', 'crumbled', 'halved', 'quartered', 'sliced', 'cooked', 'raw', 'sauce', 'dressing', 'seasoning', 'whole', 'plus', 'thinly', 'in']

def helper_function(words):
    new_string = ""
    for i in words:
        if i.isalpha():
            new_string += i.lower()
    if new_string == "":
        return None
    return new_string

def word_preprocess(recipe_lists):
    cleaned_items = []
    new_list = recipe_lists.split(",")
    for item in new_list:
        word_list = item.split(" ")
        for word in word_list:
            new_word = helper_function(word)
            if new_word is not None and new_word not in redundant_words:
                cleaned_items.append(new_word)
    return(cleaned_items)


# preload data into memory at startup and create an index based on ingredients
recipes = data.to_dict(orient='records')
ingredient_index = {}

for recipe in recipes:
    cleaned_ingredients = word_preprocess(recipe['Ingredients'])
    for ingredient in cleaned_ingredients:
        if ingredient not in ingredient_index:
            ingredient_index[ingredient] = []
        ingredient_index[ingredient].append(recipe)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return handle_post_request()
    else:
        print("yes")
        return render_template('index.html', data=data)

def handle_post_request():
    user_input = request.form['ingredientsInput']
    user_ingredients = word_preprocess(user_input)
    matched_recipes = find_matched_recipes(user_ingredients)

    if matched_recipes:
        recommended_recipes = list(matched_recipes.values())
        if len(recommended_recipes) > 10:
            recommended_recipes = recommended_recipes[:10]
        return render_template('index.html', data=data, recommended_recipes=recommended_recipes, user_input=user_input)
    else:
        return render_template('index.html', data=data, user_input=user_input, message="No matching recipes found. Try different ingredients.")
    
def find_matched_recipes(user_ingredients):
    matched_recipes = {}
    for ingredient in user_ingredients:
        if ingredient in ingredient_index:
            recipes_with_ingredient = ingredient_index[ingredient]
            for recipe in recipes_with_ingredient:
                if recipe['Title'] not in matched_recipes:
                    matched_recipes[recipe['Title']] = recipe
    return matched_recipes

def sort_recipes_by_matches(matched_recipes):
    sorted_recipes = sorted(
        matched_recipes.items(), key=lambda x: x[1], reverse=True)
    return sorted_recipes


@app.route('/recipe/<recipe_title>')
def recipe(recipe_title):
    recipe_data = next(
        recipe for recipe in recipes if recipe['Title'] == recipe_title)
    return render_template('recipe.html', recipe_data=recipe_data)

if __name__ == '__main__':
    app.run(debug=True)
