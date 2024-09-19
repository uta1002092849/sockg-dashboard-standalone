import os
import json

def save_ratings(query, rating, user_id):
    # Ensure the directory exists
    os.makedirs('collected_datas', exist_ok=True)

    try:
        with open('collected_datas/ratings.json', 'r') as file:
            ratings = json.load(file)
    except FileNotFoundError:
        ratings = {}

    # If the query doesn't exist, create a new list for it
    if query not in ratings:
        ratings[query] = []

    # Append the new rating and user_id as a tuple
    ratings[query].append((rating, user_id))

    # Save the updated ratings
    with open('collected_datas/ratings.json', 'w') as file:
        json.dump(ratings, file, indent=2)

def load_ratings():
    try:
        with open('collected_datas/ratings.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

