from flask import render_template, request, jsonify
from flask_login import current_user, login_required
from models.plant import Plant
from models.sensor import SensorReading
from models.notification import Notification
from database.connection import db
import random
from datetime import datetime

class IotController:
    @staticmethod
    def show_iot_page():
        """Render the IoT live telemetry cockpit"""
        if current_user.role == 'Admin':
            plants = Plant.query.all()
        else:
            plants = Plant.query.filter_by(user_id=current_user.id).all()
            
        latest_readings = {}
        for p in plants:
            reading = SensorReading.query.filter_by(plant_id=p.id).order_by(
                SensorReading.timestamp.desc()
            ).first()
            if reading:
                latest_readings[p.id] = reading
                
        return render_template('iot.html', plants=plants, latest_readings=latest_readings)

    @staticmethod
    def receive_telemetry():
        """Ingest sensor data from ESP32/Wokwi JSON webhook"""
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid payload'}), 400
            
        plant_id = data.get('plant_id')
        if not plant_id:
            # Fallback to the first plant of the system if not specified
            first_plant = Plant.query.first()
            if first_plant:
                plant_id = first_plant.id
            else:
                return jsonify({'status': 'error', 'message': 'No plant registered in system'}), 404
                
        plant = Plant.query.get(plant_id)
        if not plant:
            return jsonify({'status': 'error', 'message': 'Plant not found'}), 404
            
        # Parse telemetry
        temp = float(data.get('temperature', 25.0))
        hum = float(data.get('humidity', 60.0))
        moist = float(data.get('soil_moisture', 50.0))
        ph = float(data.get('soil_ph', 7.0))
        light = float(data.get('light_intensity', 5000.0))
        rain = float(data.get('rain_level', 0.0))
        tank = float(data.get('water_tank_level', 80.0))
        
        # Save reading
        reading = SensorReading(
            plant_id=plant_id,
            temperature=temp,
            humidity=hum,
            soil_moisture=moist,
            soil_ph=ph,
            light_intensity=light,
            rain_level=rain,
            water_tank_level=tank
        )
        
        db.session.add(reading)
        
        # Generate Notifications based on thresholds
        # Low soil moisture alert
        if moist < 35:
            msg = f"Alert: Soil moisture is critical ({moist:.1f}%) for plant '{plant.name}' (ID: {plant.id})! Needs watering."
            IotController._create_alert(plant.user_id, msg, 'danger')
        # Empty water tank alert
        if tank < 20:
            msg = f"Alert: Water reserve tank level is critically low ({tank:.1f}%)! Refill immediately."
            IotController._create_alert(plant.user_id, msg, 'warning')
        # High heat alert
        if temp > 38:
            msg = f"Warning: High temperature spike ({temp:.1f}°C) detected on plant '{plant.name}'."
            IotController._create_alert(plant.user_id, msg, 'danger')
            
        try:
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Telemetry stored successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @staticmethod
    def simulate_telemetry_batch():
        """Batch-generate mock telemetry entries for testing and simulation"""
        if current_user.role == 'Admin':
            plants = Plant.query.all()
        else:
            plants = Plant.query.filter_by(user_id=current_user.id).all()
            
        if not plants:
            return jsonify({'status': 'error', 'message': 'No plants found to simulate'}), 400
            
        for plant in plants:
            # Get latest reading to base simulation on, or default
            prev = SensorReading.query.filter_by(plant_id=plant.id).order_by(
                SensorReading.timestamp.desc()
            ).first()
            
            if prev:
                # Drift slightly from previous values
                temp = max(10.0, min(45.0, prev.temperature + random.uniform(-1.5, 1.5)))
                hum = max(20.0, min(95.0, prev.humidity + random.uniform(-3, 3)))
                moist = max(5.0, min(100.0, prev.soil_moisture + random.uniform(-4, 2.5))) # tend to dry
                ph = max(4.0, min(9.0, prev.soil_ph + random.uniform(-0.1, 0.1)))
                light = max(500, min(12000, prev.light_intensity + random.uniform(-500, 500)))
                tank = max(0.0, min(100.0, prev.water_tank_level + random.uniform(-2, 0.5))) # tend to drain
                rain = max(0.0, min(100.0, prev.rain_level + random.uniform(-5, 5) if random.random() > 0.8 else prev.rain_level))
            else:
                # Standard defaults
                temp = random.uniform(22.0, 32.0)
                hum = random.uniform(50.0, 75.0)
                moist = random.uniform(40.0, 65.0)
                ph = random.uniform(6.0, 7.5)
                light = random.uniform(4000, 8000)
                tank = random.uniform(70.0, 95.0)
                rain = 0.0
                
            reading = SensorReading(
                plant_id=plant.id,
                temperature=temp,
                humidity=hum,
                soil_moisture=moist,
                soil_ph=ph,
                light_intensity=light,
                rain_level=rain,
                water_tank_level=tank,
                timestamp=datetime.utcnow()
            )
            db.session.add(reading)
            
            # Check thresholds
            if moist < 35:
                IotController._create_alert(plant.user_id, f"Soil moisture critically low ({moist:.1f}%) on '{plant.name}'!", 'danger')
            if tank < 20:
                IotController._create_alert(plant.user_id, f"Water reserve tank level is critically low ({tank:.1f}%)!", 'warning')
                
        try:
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Simulated data generated successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @staticmethod
    def get_latest_telemetry(plant_id):
        """Fetch the latest telemetry reading for a specific plant via JSON API"""
        reading = SensorReading.query.filter_by(plant_id=plant_id).order_by(
            SensorReading.timestamp.desc()
        ).first()
        
        if not reading:
            return jsonify({'status': 'error', 'message': 'No readings found'}), 404
            
        return jsonify({
            'status': 'success',
            'data': {
                'id': reading.plant_id,
                'temperature': reading.temperature,
                'humidity': reading.humidity,
                'soil_moisture': reading.soil_moisture,
                'soil_ph': reading.soil_ph,
                'light_intensity': reading.light_intensity,
                'rain_level': reading.rain_level,
                'water_tank_level': reading.water_tank_level
            }
        })

    @staticmethod
    def _create_alert(user_id, message, category):
        """Helper to create and save alerts/notifications"""
        # Avoid duplicate unread alerts with identical messages
        exists = Notification.query.filter_by(
            user_id=user_id, message=message, is_read=False
        ).first()
        if not exists:
            alert = Notification(user_id=user_id, message=message, category=category)
            db.session.add(alert)
