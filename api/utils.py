from flask import jsonify, request
from . import api_blueprint, collection
from bson import ObjectId

# Get List of Restaurants
@api_blueprint.route('/restaurants', methods=['GET'])
def get_restaurants():
    print("get_restaurants route accessed")  # Debugging log
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    skip = (page - 1) * per_page
    total = collection.count_documents({})
    restaurants = list(collection.find().skip(skip).limit(per_page))
    
    # Convert ObjectId to string for JSON serialization
    for restaurant in restaurants:
        print(f"Original _id: {restaurant['_id']}, type: {type(restaurant['_id'])}")  # Debugging log
        restaurant['_id'] = str(restaurant['_id'])
        print(f"Converted _id: {restaurant['_id']}, type: {type(restaurant['_id'])}")  # Debugging log
    
    return jsonify({
        'restaurants': restaurants,
        'total': total,
        'page': page,
        'per_page': per_page
    })

# Search Restaurants by Query
@api_blueprint.route('/restaurants/search', methods=['GET'])
def search_restaurants():
    query = request.args.get('query', '')
    print(f"Search query received: {query}")
    search_query = {"$text": {"$search": query}}
    print(f"Search query: {search_query}")
    try:
        restaurants = list(collection.find(search_query))
        print(f"Number of restaurants found: {len(restaurants)}")
        
        # Convert ObjectId to string for JSON serialization
        for restaurant in restaurants:
            print(f"Original _id: {restaurant['_id']}, type: {type(restaurant['_id'])}")  # Debugging log
            restaurant['_id'] = str(restaurant['_id'])
            print(f"Converted _id: {restaurant['_id']}, type: {type(restaurant['_id'])}")  # Debugging log
        
        print(f"Restaurants: {restaurants}")
        return jsonify(restaurants)
    except Exception as e:
        print(f"Error during search: {e}")
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"error": str(e)}), 500

# Image Search (Placeholder)
@api_blueprint.route('/restaurants/image-search', methods=['POST'])
def image_search():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    # Placeholder - actual image recognition would need ML
    restaurants = list(collection.find().limit(10))
    
    # Convert ObjectId to string for JSON serialization
    for restaurant in restaurants:
        print(f"Original _id: {restaurant['_id']}, type: {type(restaurant['_id'])}")  # Debugging log
        restaurant['_id'] = str(restaurant['_id'])
        print(f"Converted _id: {restaurant['_id']}, type: {type(restaurant['_id'])}")  # Debugging log
    
    return jsonify(restaurants)