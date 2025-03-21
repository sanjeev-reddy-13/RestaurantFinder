from flask import jsonify, request
from . import api_blueprint, collection
from bson import ObjectId
from food_classifier import FoodClassifier  # Add this import

# Initialize food classifier at module level
food_classifier = FoodClassifier()

# Get List of Restaurants
@api_blueprint.route('/restaurants', methods=['GET'])
def get_restaurants():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        skip = (page - 1) * per_page
        total = collection.count_documents({})
        restaurants = list(collection.find().skip(skip).limit(per_page))
        
        # Convert ObjectId to string for JSON serialization
        for restaurant in restaurants:
            restaurant['_id'] = str(restaurant['_id'])
        
        return jsonify({
            'restaurants': restaurants,
            'total': total,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        print(f"Error in get_restaurants: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Search Restaurants by Query
@api_blueprint.route('/restaurants/search', methods=['GET'])
def search_restaurants():
    search_term = request.args.get('q', '').strip()
    if not search_term:
        return jsonify([])
    
    try:
        query = {
            "$or": [
                {"Restaurant Name": {"$regex": search_term, "$options": "i"}},
                {"Cuisines": {"$regex": search_term, "$options": "i"}},
                {"Address": {"$regex": search_term, "$options": "i"}}
            ]
        }
        
        restaurants = list(collection.find(query))
        for restaurant in restaurants:
            restaurant['_id'] = str(restaurant['_id'])
        
        print(f"Found {len(restaurants)} restaurants for query: {search_term}")
        return jsonify(restaurants)
    except Exception as e:
        print(f"Error in search_restaurants: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Get Restaurant by ID
@api_blueprint.route('/restaurants/<string:restaurant_id>', methods=['GET'])
def get_restaurant_by_id(restaurant_id):
    print(f"Fetching restaurant with ID: {restaurant_id}")  # Debugging log
    try:
        # Convert string _id to ObjectId for querying
        restaurant = collection.find_one({'_id': ObjectId(restaurant_id)})
        if restaurant:
            print(f"Original _id: {restaurant['_id']}, type: {type(restaurant['_id'])}")  # Debugging log
            restaurant['_id'] = str(restaurant['_id'])
            print(f"Converted _id: {restaurant['_id']}, type: {type(restaurant['_id'])}")  # Debugging log
            return jsonify(restaurant)
        else:
            return jsonify({"error": "Restaurant not found"}), 404
    except Exception as e:
        print(f"Error fetching restaurant: {e}")
        return jsonify({"error": "Invalid ID format"}), 400

# Image Search (Updated)
@api_blueprint.route('/restaurants/image-search', methods=['POST'])
def image_search():
    print("Image search endpoint accessed")
    
    if 'image' not in request.files:
        print("No image file in request")
        return jsonify({"error": "No image file provided"}), 400
    
    try:
        image_file = request.files['image']
        if not image_file.filename:
            return jsonify({"error": "Empty file"}), 400

        # Initialize food classifier
        classifier = FoodClassifier()
        
        # Get predictions
        predictions = classifier.predict_food(image_file)
        if not predictions:
            return jsonify({"error": "Could not identify food in image"}), 400

        # Get the top prediction
        top_food, confidence = predictions[0]
        cuisine_terms = classifier.get_cuisine_terms(top_food)

        print(f"Detected food: {top_food}, confidence: {confidence}")
        print(f"Searching for cuisine terms: {cuisine_terms}")

        # Build query for cuisine search
        query = {
            "$or": [
                {"Cuisines": {"$regex": term, "$options": "i"}} 
                for term in cuisine_terms
            ]
        }

        # Find matching restaurants
        restaurants = list(collection.find(query).limit(20))
        print(f"Found {len(restaurants)} matching restaurants")

        # Convert ObjectId to string for JSON serialization
        for restaurant in restaurants:
            restaurant['_id'] = str(restaurant['_id'])

        return jsonify({
            "prediction": {
                "food_item": top_food.replace('_', ' ').title(),
                "confidence": confidence
            },
            "restaurants": restaurants
        })

    except Exception as e:
        print(f"Error in image search: {e}")
        return jsonify({"error": str(e)}), 500

# Nearby Restaurants
@api_blueprint.route('/restaurants/nearby', methods=['GET'])
def get_nearby_restaurants():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = float(request.args.get('radius', 3000))  # Default radius is 3000 meters
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid latitude, longitude, or radius"}), 400

    try:
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "$maxDistance": radius
                }
            }
        }
        restaurants = list(collection.find(query))
        for restaurant in restaurants:
            restaurant['_id'] = str(restaurant['_id'])  # Convert ObjectId to string
        return jsonify(restaurants)
    except Exception as e:
        print(f"Error in get_nearby_restaurants: {e}")
        return jsonify({"error": "Internal server error"}), 500