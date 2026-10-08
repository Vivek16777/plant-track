import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

class GrowthPredictor:
    def __init__(self, model_path=None, values_path=None):
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), 'plant_growth_model.pkl')
        self.crop_encoder = LabelEncoder()
        self.soil_encoder = LabelEncoder()
        self.model = None
        self.is_loaded = False
        
        # Crop specifications for synthetic data generation
        self.crop_specs = {
            'Cotton': {'max_h': 120.0, 'half_age': 60, 'growth_k': 0.07, 'opt_temp': 28.0, 'opt_moist': 50.0, 'opt_ph': 6.5, 'opt_light': 8000, 'opt_npk': (90, 45, 45), 'maturity': 150},
            'Wheat': {'max_h': 90.0, 'half_age': 50, 'growth_k': 0.08, 'opt_temp': 18.0, 'opt_moist': 45.0, 'opt_ph': 7.0, 'opt_light': 6000, 'opt_npk': (120, 60, 40), 'maturity': 120},
            'Rice': {'max_h': 100.0, 'half_age': 55, 'growth_k': 0.075, 'opt_temp': 25.0, 'opt_moist': 75.0, 'opt_ph': 6.0, 'opt_light': 7000, 'opt_npk': (100, 50, 50), 'maturity': 130},
            'Sugarcane': {'max_h': 300.0, 'half_age': 180, 'growth_k': 0.025, 'opt_temp': 30.0, 'opt_moist': 65.0, 'opt_ph': 6.5, 'opt_light': 9000, 'opt_npk': (250, 100, 150), 'maturity': 365},
            'Tomato': {'max_h': 150.0, 'half_age': 45, 'growth_k': 0.09, 'opt_temp': 22.0, 'opt_moist': 60.0, 'opt_ph': 6.2, 'opt_light': 7500, 'opt_npk': (150, 80, 100), 'maturity': 90}
        }
        self.crops = list(self.crop_specs.keys())
        self.soils = ['Black', 'Red', 'Laterite', 'Loamy', 'Alluvial', 'Sandy']
        
        self.initialize_model()

    def generate_synthetic_data(self, n_samples=2000):
        """Generate high-quality synthetic dataset modeling crop growth dynamics"""
        np.random.seed(42)
        
        data = []
        for _ in range(n_samples):
            crop = np.random.choice(self.crops)
            specs = self.crop_specs[crop]
            
            # Feature inputs
            age = np.random.randint(1, specs['maturity'] + 15) # age in days
            temp = np.random.uniform(specs['opt_temp'] - 10, specs['opt_temp'] + 10)
            humidity = np.random.uniform(40.0, 95.0)
            moisture = np.random.uniform(specs['opt_moist'] - 25, specs['opt_moist'] + 25)
            moisture = np.clip(moisture, 10, 100)
            soil_ph = np.random.uniform(4.5, 8.5)
            soil_type = np.random.choice(self.soils)
            light = np.random.uniform(2000, 12000)
            
            # NPK inputs centered around the crop's optimal requirements
            n_val = np.random.normal(specs['opt_npk'][0], specs['opt_npk'][0] * 0.2)
            p_val = np.random.normal(specs['opt_npk'][1], specs['opt_npk'][1] * 0.2)
            k_val = np.random.normal(specs['opt_npk'][2], specs['opt_npk'][2] * 0.2)
            
            # Growth calculations (Logistic Growth Curve)
            k = specs['growth_k']
            half = specs['half_age']
            max_h = specs['max_h']
            
            # Calculate theoretical height and future heights
            h_raw = max_h / (1.0 + np.exp(-k * (age - half)))
            h_7_raw = max_h / (1.0 + np.exp(-k * ((age + 7) - half)))
            h_30_raw = max_h / (1.0 + np.exp(-k * ((age + 30) - half)))
            
            # Penalize growth based on environmental conditions
            temp_penalty = 1.0 - (abs(temp - specs['opt_temp']) / 15.0)
            moist_penalty = 1.0 - (abs(moisture - specs['opt_moist']) / 40.0)
            ph_penalty = 1.0 - (abs(soil_ph - specs['opt_ph']) / 2.5)
            npk_penalty = 1.0 - (abs(n_val - specs['opt_npk'][0])/specs['opt_npk'][0] + 
                                 abs(p_val - specs['opt_npk'][1])/specs['opt_npk'][1] + 
                                 abs(k_val - specs['opt_npk'][2])/specs['opt_npk'][2]) / 6.0
            
            penalty = np.clip(temp_penalty * moist_penalty * ph_penalty * npk_penalty, 0.2, 1.0)
            
            height = h_raw * penalty
            height_7d = h_7_raw * penalty
            height_30d = h_30_raw * penalty
            
            # Health Score
            health_score = penalty * 100.0 + np.random.normal(0, 2)
            health_score = np.clip(health_score, 10, 100)
            
            # Growth Rate (cm/day)
            rate_raw = k * h_raw * (1.0 - h_raw / max_h)
            growth_rate = max(0.01, rate_raw * penalty)
            
            data.append({
                'crop': crop, 'age': age, 'temp': temp, 'humidity': humidity, 
                'moisture': moisture, 'soil_ph': soil_ph, 'soil_type': soil_type,
                'N': n_val, 'P': p_val, 'K': k_val, 'light': light,
                'height': height, 'growth_rate': growth_rate, 
                'height_7d': height_7d, 'height_30d': height_30d, 
                'health_score': health_score
            })
            
        df = pd.DataFrame(data)
        return df

    def train_model(self):
        """Train and serialize the Random Forest model"""
        print("Training plant growth prediction model...")
        df = self.generate_synthetic_data()
        
        # Fit Label Encoders
        self.crop_encoder.fit(self.crops)
        self.soil_encoder.fit(self.soils)
        
        # Prepare inputs
        X = df[['crop', 'age', 'temp', 'humidity', 'moisture', 'soil_ph', 'soil_type', 'N', 'P', 'K', 'light']].copy()
        X['crop'] = self.crop_encoder.transform(X['crop'])
        X['soil_type'] = self.soil_encoder.transform(X['soil_type'])
        
        # Prepare outputs
        y = df[['height', 'growth_rate', 'height_7d', 'height_30d', 'health_score']]
        
        # Train Multi-Output Random Forest Regressor
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # Save model and encoders
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'crop_encoder': self.crop_encoder,
                'soil_encoder': self.soil_encoder
            }, f)
        self.is_loaded = True
        print("Model trained and saved successfully.")

    def initialize_model(self):
        """Load pre-trained model or trigger training if file is missing"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                self.model = data['model']
                self.crop_encoder = data['crop_encoder']
                self.soil_encoder = data['soil_encoder']
                self.is_loaded = True
                print("Loaded pre-trained plant growth model.")
            except Exception as e:
                print(f"Error loading growth model: {e}. Re-training model...")
                self.train_model()
        else:
            self.train_model()

    def predict(self, crop, age, temp, humidity, moisture, soil_ph, soil_type, n, p, k, light):
        """Predict growth stage, height, growth rate, future heights, and health index"""
        if not self.is_loaded:
            self.initialize_model()
            
        # Encode inputs (with safety checks for unseen categories)
        try:
            crop_enc = self.crop_encoder.transform([crop])[0]
        except Exception:
            crop_enc = self.crop_encoder.transform([self.crops[0]])[0]
            
        try:
            soil_enc = self.soil_encoder.transform([soil_type])[0]
        except Exception:
            soil_enc = self.soil_encoder.transform([self.soils[0]])[0]
            
        features = [[crop_enc, age, temp, humidity, moisture, soil_ph, soil_enc, n, p, k, light]]
        
        predictions = self.model.predict(features)[0]
        height, growth_rate, height_7d, height_30d, health_score = predictions
        
        # Determine Growth Stage
        specs = self.crop_specs.get(crop, {'maturity': 100})
        mat = specs['maturity']
        
        if age <= max(3, int(mat * 0.05)):
            stage = "Germination"
        elif age <= max(10, int(mat * 0.15)):
            stage = "Seedling"
        elif age <= max(45, int(mat * 0.50)):
            stage = "Vegetative"
        elif age <= max(75, int(mat * 0.75)):
            stage = "Flowering"
        elif age <= max(90, int(mat * 0.90)):
            stage = "Fruiting / Heading"
        else:
            stage = "Mature / Harvesting"
            
        # Harvest date calculation
        days_to_harvest = max(1, mat - age)
        estimated_harvest = datetime.utcnow() + timedelta(days=days_to_harvest)
        
        return {
            'current_stage': stage,
            'predicted_height': float(round(height, 2)),
            'growth_rate': float(round(growth_rate, 3)),
            'height_7d': float(round(height_7d, 2)),
            'height_30d': float(round(height_30d, 2)),
            'estimated_harvest': estimated_harvest,
            'health_score': float(round(health_score, 1))
        }
