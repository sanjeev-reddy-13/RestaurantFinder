from flask import Blueprint
from pymongo import MongoClient, errors
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the API blueprint
api_blueprint = Blueprint('api', __name__)

try:
    # Connect to MongoDB with timeout
    client = MongoClient('mongodb://localhost:27017/', 
                        serverSelectionTimeoutMS=5000)
    # Test connection
    client.server_info()
    
    db = client['zomato']
    collection = db['restaurants']
    
    logger.info("MongoDB connection successful")
    
except errors.ServerSelectionTimeoutError:
    logger.error("Could not connect to MongoDB. Is it running?")
    raise
except Exception as e:
    logger.error(f"MongoDB connection error: {e}")
    raise

# Get existing indexes
existing_indexes = collection.list_indexes()
existing_index_names = [idx['name'] for idx in existing_indexes]

# Reset cursor for another use
existing_indexes = collection.list_indexes()

# Check for text index
text_index_exists = any('text' in idx.get('name', '') for idx in existing_indexes)

# Reset cursor again
existing_indexes = collection.list_indexes()

# Check for geo index
geo_index_exists = any('2dsphere' in str(idx.get('key', {})) for idx in existing_indexes)

# Create indexes if they don't exist
if not text_index_exists:
    logger.info("Creating text index...")
    collection.create_index(
        [
            ("Restaurant Name", "text"),
            ("Cuisines", "text"),
            ("Address", "text")
        ],
        name="restaurants_text_index"
    )
    logger.info("Text index created successfully")
else:
    logger.info("Text index already exists")

if not geo_index_exists:
    logger.info("Creating geospatial index...")
    collection.create_index([("location", "2dsphere")])
    logger.info("Geospatial index created successfully")
else:
    logger.info("Geospatial index already exists")

# Import routes after blueprint creation
from . import routes

all = ['api_blueprint', 'collection']