import os
import torch
from PIL import Image
from transformers import pipeline, AutoImageProcessor, AutoModelForImageClassification

class DiseaseClassifier:
    def __init__(self):
        self.pipe = None
        self.is_loaded = False
        
        # Details database for common crop diseases
        self.disease_details = {
            'Apple___Apple_scab': {
                'description': 'A fungal disease affecting Apple trees, causing dark olive-green spots on leaves and fruit.',
                'causes': 'Venturia inaequalis fungus, favored by cool, wet spring weather.',
                'prevention': 'Prune trees to improve air circulation, clean up fallen leaves in autumn, and plant resistant varieties.',
                'recommended_fertilizer': 'Low-nitrogen, balanced organic compost to avoid excessive soft growth.',
                'recommended_fungicide': 'Captan, Myclobutanil, or Copper-based fungicides.',
                'severity': 'Medium',
                'recovery_time': '14-21 Days'
            },
            'Apple___Black_rot': {
                'description': 'A fungal disease that causes leaf spots (frog-eye), cankers on limbs, and rotting fruit.',
                'causes': 'Botryosphaeria obtusa fungus, overwintering in dead wood and mummified fruit.',
                'prevention': 'Prune dead wood, remove mummified fruit, and destroy infected limbs.',
                'recommended_fertilizer': 'Calcium-rich organic fertilizer to strengthen cell walls.',
                'recommended_fungicide': 'Sulfur or Copper fungicides, Thiophanate-methyl.',
                'severity': 'High',
                'recovery_time': '21-30 Days'
            },
            'Corn_(maize)___Common_rust_': {
                'description': 'A fungal rust causing reddish-brown pustules on both upper and lower leaf surfaces.',
                'causes': 'Puccinia sorghi fungus, carried by wind from southern regions.',
                'prevention': 'Plant resistant hybrids, rotate crops, and manage residue.',
                'recommended_fertilizer': 'Balanced NPK (e.g. 10-10-10) to support structural vigor.',
                'recommended_fungicide': 'Pyraclostrobin or Azoxystrobin (only needed in severe cases).',
                'severity': 'Low',
                'recovery_time': '10-14 Days'
            },
            'Potato___Early_blight': {
                'description': 'A common potato disease causing dark spots with concentric rings ("target board" pattern) on older leaves.',
                'causes': 'Alternaria solani fungus, thriving in warm temperatures and frequent leaf wetness.',
                'prevention': 'Rotate crops, avoid overhead watering, and ensure adequate spacing.',
                'recommended_fertilizer': 'High-potash fertilizer to improve disease resistance.',
                'recommended_fungicide': 'Chlorothalonil, Mancozeb, or Copper soap.',
                'severity': 'Medium',
                'recovery_time': '10-15 Days'
            },
            'Potato___Late_blight': {
                'description': 'A devastating disease causing dark, water-soaked leaf spots with white fungal growth underneath in humid conditions.',
                'causes': 'Phytophthora infestans (water mold), spread rapidly by wind and moisture.',
                'prevention': 'Plant certified disease-free tubers, destroy volunteer plants, and avoid wet foliage.',
                'recommended_fertilizer': 'Phosphorus-rich fertilizer to help strengthen roots.',
                'recommended_fungicide': 'Mefenoxam, Chlorothalonil, or Copper sprays.',
                'severity': 'High',
                'recovery_time': '14-28 Days'
            },
            'Tomato___Early_blight': {
                'description': 'Fungal disease causing dark brown spots with target-like concentric rings, leading to leaf yellowing and drop.',
                'causes': 'Alternaria solani fungus, surviving in soil and crop debris.',
                'prevention': 'Mulch around plants, prune lower leaves, rotate crops, and avoid overhead watering.',
                'recommended_fertilizer': 'Nitrogen-rich organic feed (e.g. fish emulsion) to replace lost leaf energy.',
                'recommended_fungicide': 'Copper fungicide or Chlorothalonil.',
                'severity': 'Medium',
                'recovery_time': '10-14 Days'
            },
            'Tomato___Late_blight': {
                'description': 'An aggressive disease causing large, dark green-black water-soaked spots on leaves and fruit, rotting them rapidly.',
                'causes': 'Phytophthora infestans, spreading quickly during wet, cool weather.',
                'prevention': 'Remove and destroy infected plants immediately. Ensure good ventilation.',
                'recommended_fertilizer': 'Balanced, slow-release organic fertilizer to keep the plant strong.',
                'recommended_fungicide': 'Copper-based fungicides applied immediately upon first notice.',
                'severity': 'High',
                'recovery_time': '14-21 Days (If caught early; otherwise plant must be destroyed)'
            },
            'Tomato___Target_Spot': {
                'description': 'Fungal disease causing small, pinpoint spots with yellow halos, expanding into target-like lesions.',
                'causes': 'Corynespora cassiicola fungus, favored by warm, humid environments.',
                'prevention': 'Increase plant spacing, avoid excessive overhead watering, and keep foliage dry.',
                'recommended_fertilizer': 'Potassium-heavy organic fertilizer.',
                'recommended_fungicide': 'Chlorothalonil, Mancozeb, or Copper sprays.',
                'severity': 'Medium',
                'recovery_time': '12-18 Days'
            }
        }

    def load_model(self):
        """Initialize the model pipeline lazily"""
        if self.is_loaded:
            return
        
        print("Initializing Hugging Face disease classification pipeline...")
        try:
            image_processor = AutoImageProcessor.from_pretrained("google/mobilenet_v2_1.0_224")
            model = AutoModelForImageClassification.from_pretrained("linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification")
            self.pipe = pipeline("image-classification", model=model, image_processor=image_processor)
            self.is_loaded = True
            print("Disease classifier loaded successfully.")
        except Exception as e:
            print(f"Error loading disease classification model: {e}")
            self.pipe = None

    def predict(self, filepath):
        """Predict disease from image file path and return detailed agronomic solutions"""
        if not self.is_loaded:
            self.load_model()
            
        if self.pipe is None:
            return {
                'success': False,
                'error': 'Model failed to load. Please check console logs.'
            }
            
        try:
            image = Image.open(filepath)
            predictions = self.pipe(image)
            
            # Extract top prediction
            top = predictions[0]
            raw_label = top['label']
            score = top['score']
            
            # Format raw label (e.g. Tomato___Target_Spot -> Tomato - Target Spot)
            clean_label = raw_label.replace('___', ' - ').replace('_', ' ')
            
            # Extract species name
            species_name = raw_label.split('___')[0].replace('_', ' ') if '___' in raw_label else clean_label.split(' ')[0]
            
            # Check if healthy
            is_healthy = 'healthy' in raw_label.lower()
            
            # Query details database or generate defaults
            if is_healthy:
                details = {
                    'description': 'The plant leaf exhibits normal, healthy characteristics without signs of pathogens.',
                    'causes': 'N/A (Optimal growth condition)',
                    'prevention': 'Maintain regular watering, nutrient balance, and sunlight conditions.',
                    'recommended_fertilizer': 'Standard NPK fertilizer as per crop specification.',
                    'recommended_fungicide': 'N/A (No treatment required)',
                    'severity': 'Healthy',
                    'recovery_time': 'N/A'
                }
            else:
                details = self.disease_details.get(raw_label, {
                    'description': f'A plant disease affecting leaves of {species_name} crops.',
                    'causes': 'Pathogenic infection, often aggravated by high humidity and poor air circulation.',
                    'prevention': 'Ensure proper spacing, rotate crop fields, and prune infected leaves.',
                    'recommended_fertilizer': 'Balanced fertilizer to recover vigor.',
                    'recommended_fungicide': 'Copper-based fungicide sprays.',
                    'severity': 'Medium',
                    'recovery_time': '10-20 Days'
                })
                
            return {
                'success': True,
                'raw_label': raw_label,
                'disease_name': clean_label,
                'species_name': species_name,
                'confidence': float(round(score * 100, 2)),
                'is_healthy': is_healthy,
                **details
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
