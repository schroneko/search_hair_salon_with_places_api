import requests
import json
from operator import itemgetter
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PLACES_API_KEY")


def search_nearby_places(api_key, latitude, longitude, radius):
    url = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.rating,places.userRatingCount,places.types",
    }

    data = {
        "includedTypes": ["hair_salon", "barber_shop"],
        "maxResultCount": 20,
        "languageCode": "ja",  # 日本語の結果を優先
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius,
            }
        },
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def log_response(response_data):
    with open("log.txt", "w", encoding="utf-8") as log_file:
        json.dump(response_data, log_file, ensure_ascii=False, indent=2)
    print("Full API response has been logged to log.txt")


def is_hair_salon(place):
    types = set(place.get("types", []))
    name = place.get("displayName", {}).get("text", "").lower()

    # 優先すべきタイプ
    priority_types = {"hair_salon", "barber_shop"}

    # 除外すべきキーワード
    exclude_keywords = [
        "アイブロウ",
        "まつげ",
        "ネイル",
        "エステ",
        "スパ",
        "eyebrow",
        "eyelash",
        "nail",
        "spa",
    ]

    if priority_types & types:
        if not any(keyword in name for keyword in exclude_keywords):
            return True

    return False


def parse_hair_salons(places_data):
    if not places_data or "places" not in places_data:
        print("No places data found in the API response.")
        return []

    salons = places_data.get("places", [])

    top_salons = []
    for salon in salons:
        if is_hair_salon(salon):
            name = salon.get("displayName", {}).get("text")
            rating = salon.get("rating")
            total_ratings = salon.get("userRatingCount")

            if rating and rating >= 4 and total_ratings and total_ratings >= 20:
                top_salons.append(
                    {"name": name, "rating": rating, "total_ratings": total_ratings}
                )

    # Sort by rating (descending) and then by total ratings (descending)
    top_salons.sort(key=itemgetter("rating", "total_ratings"), reverse=True)

    return top_salons[:5]


def display_top_salons(salons):
    if not salons:
        print("No qualifying hair salons found.")
        return

    print("Top 5 Hair Salons near Meguro Station (Rating 4+ and 20+ reviews):")
    print("----------------------------------------------------------------")
    for i, salon in enumerate(salons, 1):
        print(f"{i}. {salon['name']}")
        print(f"   Rating: {salon['rating']}")
        print(f"   Total Reviews: {salon['total_ratings']}")
        print()


# Meguro Station coordinates
latitude = 35.633998
longitude = 139.715828

# Search radius in meters
radius = 500

# Perform the search
places_data = search_nearby_places(api_key, latitude, longitude, radius)

if places_data:
    # Log the full API response
    log_response(places_data)

    # Parse and display top salons
    top_salons = parse_hair_salons(places_data)
    display_top_salons(top_salons)
else:
    print("Failed to retrieve data from the API.")
