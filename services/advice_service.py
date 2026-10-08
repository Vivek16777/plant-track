class AdviceService:
    @staticmethod
    def get_irrigation_recommendation(crop, current_moisture, temperature, rain_prob):
        """Recommend irrigation volume, frequency, and reasons using soil and environment states"""
        # Crop-specific moisture thresholds
        optimal_moisture = {
            'Cotton': 50.0,
            'Wheat': 45.0,
            'Rice': 75.0,
            'Sugarcane': 65.0,
            'Tomato': 60.0
        }
        
        opt = optimal_moisture.get(crop, 55.0)
        
        # Determine quantity and frequency
        if rain_prob >= 70:
            quantity = 0
            frequency = "Postponed"
            method = "None"
            best_time = "N/A"
            reason = f"High precipitation probability ({rain_prob}%) forecasted. Irrigation not required."
        elif current_moisture < opt - 20:
            quantity = 600 if crop == 'Sugarcane' or crop == 'Rice' else 450
            frequency = "Immediate"
            method = "Flood Irrigation" if crop == 'Rice' else "Drip Irrigation"
            best_time = "Early Morning (6:00 AM) or Evening (6:00 PM)"
            reason = f"Soil moisture is extremely low ({current_moisture:.1f}% vs optimal {opt}%). Roots require immediate watering."
        elif current_moisture < opt - 5:
            quantity = 400 if crop == 'Sugarcane' or crop == 'Rice' else 250
            frequency = "Daily"
            method = "Drip Irrigation" if crop != 'Rice' else "Sprinkler"
            best_time = "Morning (7:00 AM)"
            reason = f"Soil moisture is slightly dry ({current_moisture:.1f}% vs optimal {opt}%). Routine irrigation recommended."
        else:
            quantity = 100
            frequency = "As needed"
            method = "Micro-drip / Misting"
            best_time = "Evening (5:00 PM)"
            reason = f"Soil moisture is optimal ({current_moisture:.1f}%). Minor watering to compensate for daily evaporation is sufficient."
            
        # Adjust for heat
        if temperature > 33 and frequency != "Postponed":
            quantity += 100
            reason += " Volume increased due to high ambient temperatures."
            
        return {
            'water_amount_ml': quantity,
            'frequency': frequency,
            'method': method,
            'best_time': best_time,
            'reason': reason
        }

    @staticmethod
    def get_fertilizer_recommendation(crop, n, p, k):
        """Recommend NPK ratios, fertilizer types, quantities, and schedules"""
        optimal_npk = {
            'Cotton': (90.0, 45.0, 45.0),
            'Wheat': (120.0, 60.0, 40.0),
            'Rice': (100.0, 50.0, 50.0),
            'Sugarcane': (250.0, 100.0, 150.0),
            'Tomato': (150.0, 80.0, 100.0)
        }
        
        opt_n, opt_p, opt_k = optimal_npk.get(crop, (100.0, 50.0, 50.0))
        
        deficit_n = max(0.0, opt_n - n)
        deficit_p = max(0.0, opt_p - p)
        deficit_k = max(0.0, opt_k - k)
        
        # Decide fertilizer name
        if deficit_n > deficit_p and deficit_n > deficit_k:
            fert_name = "Urea (46-0-0)"
            npk = "46-0-0"
            org_alt = "Composted manure, blood meal, or alfalfa meal"
            qty = int(deficit_n * 2.2) # conversion ratio
            schedule = "Apply in 2 split doses: at sowing and 30 days after germination."
        elif deficit_p > deficit_k:
            fert_name = "Single Super Phosphate (0-16-0) or DAP"
            npk = "18-46-0"
            org_alt = "Bone meal, rock phosphate, or bat guano"
            qty = int(deficit_p * 2.5)
            schedule = "Apply fully during land preparation as a basal dose."
        elif deficit_k > 0:
            fert_name = "Muriate of Potash (MOP)"
            npk = "0-0-60"
            org_alt = "Kelp meal, greensand, or hardwood wood ash"
            qty = int(deficit_k * 1.6)
            schedule = "Apply in split doses: basal dose and during the flowering stage."
        else:
            fert_name = "Balanced NPK (19-19-19)"
            npk = "19-19-19"
            org_alt = "Fish emulsion, seaweed liquid fertilizer, or vermicompost"
            qty = 150
            schedule = "Apply every 2-3 weeks at low concentrations to maintain nutrient levels."
            
        return {
            'fertilizer_name': fert_name,
            'npk_ratio': npk,
            'organic_alternative': org_alt,
            'quantity_g': qty,
            'schedule': schedule
        }

    @staticmethod
    def get_soil_analysis(soil_type, ph):
        """Analyze soil characteristics, water retention, and assign a health score"""
        # Base stats for soil types
        soil_stats = {
            'Black': {'retention': 'Excellent (High Clay)', 'capacity': 'Very High', 'score': 85},
            'Red': {'retention': 'Moderate (Sandy Clay)', 'capacity': 'Moderate', 'score': 70},
            'Laterite': {'retention': 'Low (Highly Porous)', 'capacity': 'Low to Medium', 'score': 60},
            'Loamy': {'retention': 'Very Good (Balanced)', 'capacity': 'High', 'score': 90},
            'Alluvial': {'retention': 'Excellent (River Sediment)', 'capacity': 'Excellent', 'score': 95},
            'Sandy': {'retention': 'Very Poor (Highly Porous)', 'capacity': 'Poor', 'score': 45}
        }
        
        stats = soil_stats.get(soil_type, {'retention': 'Moderate', 'capacity': 'Moderate', 'score': 70})
        
        # pH Penalty
        ph_dev = abs(ph - 6.5)
        ph_penalty = int(ph_dev * 12)  # lose score for extreme pH
        
        final_score = max(10, stats['score'] - ph_penalty)
        
        if ph < 5.5:
            quality = "Acidic Soil (Requires Lime application to neutralize)"
        elif ph > 7.8:
            quality = "Alkaline / Saline Soil (Requires Gypsum application to neutralize)"
        else:
            quality = "Ideal Soil (Neutral, optimal nutrient absorption)"
            
        # Suitable crops recommendations based on soil type
        soil_crops = {
            'Black': ['Cotton', 'Sugarcane', 'Soybean', 'Wheat', 'Jowar'],
            'Red': ['Groundnut', 'Millets', 'Pulses', 'Tobacco', 'Tomato'],
            'Laterite': ['Cashew', 'Tea', 'Coffee', 'Coconut', 'Rubber'],
            'Loamy': ['Wheat', 'Sugarcane', 'Tomato', 'Vegetables', 'Fruits'],
            'Alluvial': ['Rice', 'Wheat', 'Sugarcane', 'Jute', 'Oilseeds'],
            'Sandy': ['Watermelon', 'Muskmelon', 'Groundnut', 'Carrot', 'Potato']
        }
        
        return {
            'soil_quality': quality,
            'water_retention': stats['retention'],
            'nutrient_capacity': stats['capacity'],
            'soil_health_score': final_score,
            'suitable_crops': soil_crops.get(soil_type, ['Green Gram', 'Millets'])
        }
