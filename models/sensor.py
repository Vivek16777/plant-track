from database.connection import db
from datetime import datetime

class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id', ondelete='CASCADE'), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    soil_moisture = db.Column(db.Float, nullable=False)  # 0 to 100%
    soil_ph = db.Column(db.Float, nullable=False)         # 0 to 14
    light_intensity = db.Column(db.Float, nullable=False)  # Lux
    rain_level = db.Column(db.Float, nullable=False)       # 0 (dry) to 100 (heavy rain)
    water_tank_level = db.Column(db.Float, nullable=False) # 0 to 100%
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
