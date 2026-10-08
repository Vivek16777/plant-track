import os
import pickle
import warnings

# Suppress sklearn unpickling warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

class SeedSowingModel:
    def __init__(self, models_path=None, values_path=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.models_path = models_path or os.path.join(base_dir, 'agricultural_models.pkl')
        self.values_path = values_path or os.path.join(base_dir, 'unique_values.pkl')
        
        self.seed_size_model = None
        self.sowing_depth_model = None
        self.spacing_model = None
        self.label_encoders = {}
        self.unique_values = {'Crop Name': [], 'Region': [], 'Season': [], 'Soil Type': []}
        self.is_loaded = False
        
        self.load_models()

    def load_models(self):
        """Load pre-trained random forest and encoder models from pickle"""
        if not os.path.exists(self.models_path):
            print(f"Error: {self.models_path} not found. Sowing models will not be available.")
            return
            
        try:
            with open(self.models_path, 'rb') as f:
                models = pickle.load(f)
            self.seed_size_model = models['seed_size_model']
            self.sowing_depth_model = models['sowing_depth_model']
            self.spacing_model = models['spacing_model']
            self.label_encoders = models['label_encoders']
            
            if os.path.exists(self.values_path):
                with open(self.values_path, 'rb') as f:
                    self.unique_values = pickle.load(f)
                    
            self.is_loaded = True
            print("Loaded seed sowing models and unique dropdown values.")
        except Exception as e:
            print(f"Error loading seed models: {e}")

    def predict(self, crop_name, region, season, temperature, moisture, soil_type, soil_ph):
        """Predict seed size, depth, and spacing with input encoding"""
        if not self.is_loaded:
            return None
            
        try:
            # Transform categorical values using label encoders
            crop_encoded = self.label_encoders['Crop Name'].transform([crop_name])[0]
            region_encoded = self.label_encoders['Region'].transform([region])[0]
            season_encoded = self.label_encoders['Season'].transform([season])[0]
            soil_encoded = self.label_encoders['Soil Type'].transform([soil_type])[0]
            
            features = [[crop_encoded, region_encoded, season_encoded,
                         float(temperature), float(moisture), soil_encoded, float(soil_ph)]]
            
            # Predict
            seed_size_encoded = self.seed_size_model.predict(features)[0]
            sowing_depth = self.sowing_depth_model.predict(features)[0]
            spacing = self.spacing_model.predict(features)[0]
            
            # Inverse transform seed size category
            seed_size = self.label_encoders['Seed Size Category'].inverse_transform([seed_size_encoded])[0]
            
            return {
                'seed_size': seed_size,
                'sowing_depth': float(round(sowing_depth, 2)),
                'spacing': float(round(spacing, 2))
            }
        except Exception as e:
            print(f"Error executing seed prediction: {e}")
            return None
            
    def get_dropdown_values(self):
        """Return lists of unique parameters for UI drop-downs"""
        return self.unique_values
