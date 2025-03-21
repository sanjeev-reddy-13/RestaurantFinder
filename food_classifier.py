from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import torch

class FoodClassifier:
    def __init__(self):  # Fixed from _init to __init__
        try:
            print("Initializing food classifier...")
            self.model_name = "nateraw/food"
            self.extractor = AutoFeatureExtractor.from_pretrained(self.model_name)
            self.model = AutoModelForImageClassification.from_pretrained(self.model_name)
            print("Food classifier initialized successfully")
        except Exception as e:
            print(f"Error initializing food classifier: {e}")
            raise
        
        # Cuisine mappings for better restaurant matching
        self.cuisine_mappings = {
            'pizza': ['italian', 'pizza'],
            'pasta': ['italian'],
            'burger': ['american', 'burger'],
            'sushi': ['japanese', 'sushi'],
            'curry': ['indian', 'curry'],
            'noodles': ['chinese', 'asian'],
            'rice': ['indian', 'chinese', 'asian'],
            'sandwich': ['cafe', 'fast food'],
            'dessert': ['dessert', 'cafe']
        }

    def predict_food(self, image_file):
        try:
            print("Processing image...")
            image = Image.open(image_file).convert('RGB')
            inputs = self.extractor(images=image, return_tensors="pt")
            
            print("Making prediction...")
            outputs = self.model(**inputs)
            probs = outputs.logits.softmax(1)
            
            # Get top 3 predictions
            top_3 = torch.topk(probs, 3)
            predictions = []
            for i in range(3):
                label = self.model.config.id2label[top_3.indices[0][i].item()]
                score = top_3.values[0][i].item()
                predictions.append((label, score))
            
            print("Predictions:", predictions)
            return predictions
        except Exception as e:
            print(f"Error in food prediction: {e}")
            return []

    def get_cuisine_terms(self, food_label):
        """Convert food label to cuisine search terms"""
        food_label = food_label.lower().replace('_', ' ')
        # Try direct mapping first
        for key, terms in self.cuisine_mappings.items():
            if key in food_label:
                return terms
        # If no direct mapping, use the food label itself
        return [food_label]