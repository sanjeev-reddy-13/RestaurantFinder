from pymongo import MongoClient, errors

# MongoDB Atlas Connection URI
MONGO_URI = 'mongodb+srv://sanjeevreddy2004:Sanjeev13@cluster0.if1yr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

try:
    # Connect to MongoDB Atlas
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['zomato']
    collection = db['restaurants']
    print("✅ Connected to MongoDB Atlas successfully!")

    # Add the 'location' field to all documents
    update_result = collection.update_many(
        {"Latitude": {"$exists": True}, "Longitude": {"$exists": True}},
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
    print(f"✅ Location field updated in {update_result.modified_count} documents.")

    # Check and create text index
    existing_indexes = collection.index_information()
    text_index_name = "Restaurant_Name_text_Cuisines_text_Address_text"

    if text_index_name not in existing_indexes:
        collection.create_index(
            [("Restaurant Name", "text"), ("Cuisines", "text"), ("Address", "text")],
            name=text_index_name
        )
        print("✅ Text index created successfully.")
    else:
        print("✅ Text index already exists.")

    # Check and create 2dsphere index for geospatial queries
    if 'location_2dsphere' not in existing_indexes:
        collection.create_index([("location", "2dsphere")])
        print("✅ 2dsphere index created successfully.")
    else:
        print("✅ 2dsphere index already exists.")

except errors.ServerSelectionTimeoutError as err:
    print(f"❌ Error: Unable to connect to MongoDB Atlas. Details: {err}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    # Close the connection
    client.close()
    print("🔌 MongoDB connection closed.")
