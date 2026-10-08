from database.connection import db
from datetime import datetime

class Plant(db.Model):
    __tablename__ = 'plants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    crop_type = db.Column(db.String(50), nullable=False)
    sowing_date = db.Column(db.DateTime, default=datetime.utcnow)
    age_days = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='Healthy')  # 'Healthy' or 'Diseased'
    height_cm = db.Column(db.Float, default=1.0)
    soil_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sensor_readings = db.relationship('SensorReading', backref='plant', lazy=True, cascade="all, delete-orphan")
    disease_diagnoses = db.relationship('DiseaseDiagnosis', backref='plant', lazy=True, cascade="all, delete-orphan")
    growth_predictions = db.relationship('GrowthPrediction', backref='plant', lazy=True, cascade="all, delete-orphan")
    irrigation_records = db.relationship('IrrigationRecord', backref='plant', lazy=True, cascade="all, delete-orphan")
    fertilizer_records = db.relationship('FertilizerRecord', backref='plant', lazy=True, cascade="all, delete-orphan")
    
    @property
    def current_age(self):
        """Dynamically compute plant age in days from sowing date"""
        delta = datetime.utcnow() - self.sowing_date
        return max(1, delta.days)
