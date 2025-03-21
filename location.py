from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['zomato']
collection = db['restaurants']

# Add the location field to all documents
collection.update_many(
    {},
    [
        {
            "$set": {
                "location": {
                    "type": "Point",
                    "coordinates": ["$Longitude", "$Latitude"]
                }
            }
        }
    ]
)
print("Location field added to all documents.")

# Check if text index exists
existing_indexes = collection.index_information()
text_index_name = "Restaurant_Name_text_Cuisines_text_Address_text"
if text_index_name not in existing_indexes:
    collection.create_index(
        [("Restaurant Name", "text"), ("Cuisines", "text"), ("Address", "text")],
        name=text_index_name
    )
    print("Text index created.")
else:
    print("Text index already exists.")

# Check if 2dsphere index exists
if 'location_2dsphere' not in existing_indexes:
    collection.create_index([("location", "2dsphere")])
    print("2dsphere index created.")
else:
    print("2dsphere index already exists.")