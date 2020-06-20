import re
import copy
from store_in_Notes import store_in_notes
from categories import grocery_layout, categories

# Constants and mappers
dimensions = {"st", "gram", "dl", "maträtter", "tsk", "krm", "port", "stycken", "msk", "burk"}
dimension_converter = {"g": "gram", "st": "stycken"}


class Ingredient:
    def __init__(self, name, dimension= None):
        self.name = name
        self.amount = 0
        self.dimension = dimension
        self.category = "Other"

    def add_amount(self, amount):
        self.amount += amount

    def set_amount(self, amount):
        self.amount = amount

    def set_dimension(self, dimension):
        self.dimension = dimension

    def set_category(self, category):
        self.category = category

    def print_ingredient(self, file):
        if self.dimension is not None:
             print(str(self.amount) + " " + self.dimension + " " + self.name, file=file)
        else:
            print(str(self.amount) + " " + self.name, file=file)


class Recipe:
    def __init__(self,):
        self.ingredients = []
        self.title = "No title"
        self.url = "No URL"

    def set_title(self, title):
        self.title = title

    def set_url(self, url):
        self.url = url

    def set_portions(self, portions):
        self.portions = int(portions)

    def add_ingredient(self, ingredient):
        self.ingredients.append(ingredient)

    def calculate_amount(self, portions):
        factor = portions / self.portions
        for ingredient in self.ingredients:
            ingredient.set_amount(round(ingredient.amount * factor, 1))
        self.portions = portions

    def print_recipe(self, file):
        print(self.title + " " + str(self.portions) + " portioner", file=file)
        print(self.url, file=file)
        for ingredient in self.ingredients:
            ingredient.print_ingredient(file)

def extract_ingredient(line):
    local_dimension = None
    amount = None

    # Extract amount
    words = line.split(" ")
    for index, word in enumerate(words):
        if len(re.findall(r'\b\d+\b', word)) > 0:
            amount = int(round(float(word)))
            line = line.replace(str(word), "")


    # Extract dimensions (st, gram, etc) - start with converting
    words = line.split(" ")
    for index, word in enumerate(words):
        if word in dimension_converter:
            new_word = dimension_converter[word]
            words[index] = new_word

    line = " ".join(words)

    for dimension in dimensions:
        for word in line.split(" "):
            if word == dimension:
                local_dimension = dimension
                line = line.replace(dimension, "")

    # Extract ingredient name
    words = line.split(" ")
    ingredient_name = []
    for word in words:
        if word is not "":
            ingredient_name.append(word)

    ingredient_name = " ".join(ingredient_name)
    return ingredient_name, amount, local_dimension

def get_order(ingredient):
    return grocery_layout[ingredient.category]


def sort_ingridients(purchase_list):
    # Set ingredient category
    for purchased_ingredient in purchase_list:
        for category, ingredients in categories.items():
            for ingredient in ingredients:
                if purchased_ingredient.name.__contains__(ingredient):
                    purchased_ingredient.set_category(category)

    # Sort ingredient based on category
    purchase_list.sort(key=get_order)

    return purchase_list


def create_file(recipes, purchase_list, file_name):
    file = open(file_name, "w", encoding="utf8")

    for recipe in recipes:
        recipe.print_recipe(file)
        print("\n", file=file)

    print("----------Purchase list---------", file=file)
    for ingredient in purchase_list:
        ingredient.print_ingredient(file=file)

def create_purchase_list(recipes):
    purchase_list = []

    for recipe in recipes:
        for ingredient in recipe.ingredients:
            ingredient_exists = False
            for stored_ingredient in purchase_list:
                if stored_ingredient.name == ingredient.name:
                    stored_ingredient.add_amount(ingredient.amount)
                    ingredient_exists = True
                    break
            if not ingredient_exists:
                purchase_list.append(copy.copy(ingredient))

    return purchase_list


recipes_dir = "./recipes.txt"
recipes = []
data = open(recipes_dir, "r")
lines = iter(data.readlines())
for line in lines:
    # Remove unecessary ingredients
    if line == "\n":
        # New recipe
        recipe = Recipe()
        title = next(lines)
        title = title.replace("\n", "")
        recipe.set_title(title)
        recipes.append(recipe)
        continue

    # Lower case all input and remove \n
    line = str.lower(line)
    line = line.replace("\n", "")

    # Create ingredient
    if line.startswith("http") or line.startswith("wwww"):
        # Add url to recipe
        recipe.url = line
        continue

    if line.__contains__("portioner"):
        portions = "".join(re.findall(r'\b\d+\b', line))
        recipe.set_portions(portions)
        continue

    ingredient_name, amount, dimension = extract_ingredient(line)

    new_ingredient = Ingredient(ingredient_name)

    if amount is not None:
        new_ingredient.add_amount(amount)
    if dimension is not None:
        new_ingredient.set_dimension(dimension)

    recipe.add_ingredient(new_ingredient)

print("\nRecept")
for index, recipe in enumerate(recipes):
    print(str(index) + " " + recipe.title)
print("\n")

choices = input("Välj de maträtter du vill ha och antalet portioner ").split(" ")


# Extract chosen recipes
chosen_recipes = []
for index in range(0, len(choices), 2):
    recipe_number = int(choices[index])
    portions = int(choices[index+1])
    recipes[recipe_number].calculate_amount(portions)

    chosen_recipes.append(recipes[recipe_number])

file_name = "Purchase_list"

purchase_list = create_purchase_list(chosen_recipes)
sort_ingridients(purchase_list)
create_file(chosen_recipes, purchase_list, file_name)
store_in_notes(file_name)
