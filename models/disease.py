from database.connection import db
from datetime import datetime

class DiseaseDiagnosis(db.Model):
    __tablename__ = 'disease_diagnoses'
    
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id', ondelete='CASCADE'), nullable=False)
    disease_name = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)      # Percentage (e.g. 95.4)
    severity = db.Column(db.String(20), nullable=False)    # 'Low', 'Medium', 'High'
    description = db.Column(db.Text, nullable=False)
    causes = db.Column(db.Text, nullable=False)
    prevention = db.Column(db.Text, nullable=False)
    recommended_fertilizer = db.Column(db.String(150), nullable=False)
    recommended_fungicide = db.Column(db.String(150), nullable=False)
    recovery_time = db.Column(db.String(50), nullable=False) # e.g. "7-14 Days"
    image_path = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
