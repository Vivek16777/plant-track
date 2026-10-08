from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from models.plant import Plant
from models.sensor import SensorReading
from models.disease import DiseaseDiagnosis
from models.prediction import GrowthPrediction
from models.records import IrrigationRecord, FertilizerRecord
from database.connection import db
from ml.growth_model import GrowthPredictor
from ml.disease_classifier import DiseaseClassifier
from services.advice_service import AdviceService
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# Initialize predictor engines
growth_predictor = GrowthPredictor()
disease_classifier = DiseaseClassifier()

class PlantController:
    @staticmethod
    def show_plant_list():
        """Render list of plants for the authenticated user"""
        if current_user.role == 'Admin':
            plants = Plant.query.all()
        else:
            plants = Plant.query.filter_by(user_id=current_user.id).all()
        return render_template('plant_list.html', plants=plants)

    @staticmethod
    def add_plant():
        """Add a new crop profile to the database"""
        if request.method == 'POST':
            name = request.form.get('name')
            crop_type = request.form.get('crop_type')
            soil_type = request.form.get('soil_type')
            height = float(request.form.get('height_cm', 1.0))
            sowing_date_str = request.form.get('sowing_date')
            
            if sowing_date_str:
                sowing_date = datetime.strptime(sowing_date_str, '%Y-%m-%d')
            else:
                sowing_date = datetime.utcnow()
                
            plant = Plant(
                name=name,
                crop_type=crop_type,
                soil_type=soil_type,
                height_cm=height,
                sowing_date=sowing_date,
                user_id=current_user.id
            )
            
            db.session.add(plant)
            
            # Add a default sensor reading to prevent blank stats
            default_reading = SensorReading(
                plant=plant,
                temperature=25.0,
                humidity=60.0,
                soil_moisture=50.0,
                soil_ph=6.5,
                light_intensity=5000.0,
                rain_level=0.0,
                water_tank_level=80.0
            )
            db.session.add(default_reading)
            
            try:
                db.session.commit()
                flash(f"Crop '{name}' added successfully!", "success")
                return redirect(url_for('plant.list_plants'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error saving plant: {e}", "danger")
                
        return render_template('add_plant.html')

    @staticmethod
    def delete_plant(plant_id):
        """Delete an active crop profile and its cascade relationships"""
        plant = Plant.query.get_or_404(plant_id)
        # Auth check
        if current_user.role != 'Admin' and plant.user_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for('plant.list_plants'))
            
        try:
            db.session.delete(plant)
            db.session.commit()
            flash("Crop profile deleted successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting plant: {e}", "danger")
            
        return redirect(url_for('plant.list_plants'))

    @staticmethod
    def show_plant_detail(plant_id):
        """Render full telemetry, diagnosis logs, and growth predictions for a single crop"""
        plant = Plant.query.get_or_404(plant_id)
        if current_user.role != 'Admin' and plant.user_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for('plant.list_plants'))
            
        # Get historical logs
        readings = SensorReading.query.filter_by(plant_id=plant.id).order_by(
            SensorReading.timestamp.desc()
        ).limit(10).all()
        
        diagnoses = DiseaseDiagnosis.query.filter_by(plant_id=plant.id).order_by(
            DiseaseDiagnosis.timestamp.desc()
        ).all()
        
        predictions = GrowthPrediction.query.filter_by(plant_id=plant.id).order_by(
            GrowthPrediction.timestamp.desc()
        ).all()
        
        latest_reading = readings[0] if readings else None
        latest_pred = predictions[0] if predictions else None
        
        # Calculate dynamic recommendations using advice services
        irrigation_advice = None
        fertilizer_advice = None
        if latest_reading:
            irrigation_advice = AdviceService.get_irrigation_recommendation(
                plant.crop_type, 
                latest_reading.soil_moisture, 
                latest_reading.temperature, 
                latest_reading.rain_level
            )
            # Default NPK lookup (simulating lab/sensor readings)
            # We can mock NPK centered around crop requirement
            fertilizer_advice = AdviceService.get_fertilizer_recommendation(
                plant.crop_type,
                n=random_npk(plant.crop_type, 0),
                p=random_npk(plant.crop_type, 1),
                k=random_npk(plant.crop_type, 2)
            )
            
        soil_analysis = AdviceService.get_soil_analysis(
            plant.soil_type, 
            latest_reading.soil_ph if latest_reading else 6.5
        )
        
        # Chart.js inputs: reverse logs to read chronologically (left to right)
        chart_readings = list(reversed(readings))
        dates = [r.timestamp.strftime('%H:%M') for r in chart_readings]
        moisture_vals = [r.soil_moisture for r in chart_readings]
        temp_vals = [r.temperature for r in chart_readings]
        humidity_vals = [r.humidity for r in chart_readings]
        
        return render_template(
            'plant_detail.html',
            plant=plant,
            readings=readings,
            diagnoses=diagnoses,
            predictions=predictions,
            latest_reading=latest_reading,
            latest_pred=latest_pred,
            irrigation_advice=irrigation_advice,
            fertilizer_advice=fertilizer_advice,
            soil_analysis=soil_analysis,
            dates=dates,
            moisture_vals=moisture_vals,
            temp_vals=temp_vals,
            humidity_vals=humidity_vals
        )

    @staticmethod
    def run_prediction(plant_id):
        """Run ML growth prediction and save target predictions to the database"""
        plant = Plant.query.get_or_404(plant_id)
        latest_reading = SensorReading.query.filter_by(plant_id=plant.id).order_by(
            SensorReading.timestamp.desc()
        ).first()
        
        if not latest_reading:
            return jsonify({'status': 'error', 'message': 'No sensor readings found to compute growth'}), 400
            
        # Simulating random NPK values matching current soil type health
        n = random_npk(plant.crop_type, 0)
        p = random_npk(plant.crop_type, 1)
        k = random_npk(plant.crop_type, 2)
        
        # ML Growth Predictor Call
        pred = growth_predictor.predict(
            crop=plant.crop_type,
            age=plant.current_age,
            temp=latest_reading.temperature,
            humidity=latest_reading.humidity,
            moisture=latest_reading.soil_moisture,
            soil_ph=latest_reading.soil_ph,
            soil_type=plant.soil_type,
            n=n, p=p, k=k,
            light=latest_reading.light_intensity
        )
        
        # Update plant height in main profile
        plant.height_cm = pred['predicted_height']
        
        # Save prediction
        prediction_record = GrowthPrediction(
            plant_id=plant.id,
            current_stage=pred['current_stage'],
            predicted_height=pred['predicted_height'],
            growth_rate=pred['growth_rate'],
            height_7d=pred['height_7d'],
            height_30d=pred['height_30d'],
            estimated_harvest=pred['estimated_harvest'],
            health_score=pred['health_score']
        )
        db.session.add(prediction_record)
        
        try:
            db.session.commit()
            return jsonify({
                'status': 'success', 
                'data': {
                    'current_stage': pred['current_stage'],
                    'predicted_height': pred['predicted_height'],
                    'growth_rate': pred['growth_rate'],
                    'height_7d': pred['height_7d'],
                    'height_30d': pred['height_30d'],
                    'health_score': pred['health_score'],
                    'estimated_harvest': pred['estimated_harvest'].strftime('%Y-%m-%d')
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @staticmethod
    def diagnose_disease(plant_id):
        """Diagnose disease from uploaded leaf photo using Hugging Face model and save to DB"""
        plant = Plant.query.get_or_404(plant_id)
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
            
        # Secure filename and save
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(current_user.application.config['UPLOAD_FOLDER']) if hasattr(current_user, 'application') else os.path.join('static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Run ML Classification
        res = disease_classifier.predict(filepath)
        if not res.get('success', False):
            return jsonify({'status': 'error', 'message': res.get('error', 'Prediction failed')}), 500
            
        # Log to database
        diagnosis = DiseaseDiagnosis(
            plant_id=plant.id,
            disease_name=res['disease_name'],
            confidence=res['confidence'],
            severity=res['severity'],
            description=res['description'],
            causes=res['causes'],
            prevention=res['prevention'],
            recommended_fertilizer=res['recommended_fertilizer'],
            recommended_fungicide=res['recommended_fungicide'],
            recovery_time=res['recovery_time'],
            image_path=f'/static/uploads/{filename}'
        )
        
        # Update plant profile status
        plant.status = 'Diseased' if not res['is_healthy'] else 'Healthy'
        db.session.add(diagnosis)
        
        try:
            db.session.commit()
            return jsonify({
                'status': 'success',
                'data': {
                    'disease_name': res['disease_name'],
                    'species_name': res.get('species_name', 'Unknown'),
                    'confidence': res['confidence'],
                    'severity': res['severity'],
                    'description': res['description'],
                    'causes': res['causes'],
                    'prevention': res['prevention'],
                    'recommended_fertilizer': res['recommended_fertilizer'],
                    'recommended_fungicide': res['recommended_fungicide'],
                    'recovery_time': res['recovery_time'],
                    'image_path': f'/static/uploads/{filename}',
                    'is_healthy': res['is_healthy']
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

# Helper function to generate mock NPK values
def random_npk(crop, index):
    import random
    optimal_npk = {
        'Cotton': (90, 45, 45),
        'Wheat': (120, 60, 40),
        'Rice': (100, 50, 50),
        'Sugarcane': (250, 100, 150),
        'Tomato': (150, 80, 100)
    }
    opt = optimal_npk.get(crop, (100, 50, 50))[index]
    # Drift slightly (within 20% deviation)
    return max(5, int(opt + random.uniform(-opt * 0.15, opt * 0.1)))
