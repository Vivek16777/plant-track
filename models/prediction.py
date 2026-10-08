from database.connection import db
from datetime import datetime

class GrowthPrediction(db.Model):
    __tablename__ = 'growth_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id', ondelete='CASCADE'), nullable=False)
    current_stage = db.Column(db.String(50), nullable=False)  # 'Germination', 'Seedling', 'Vegetative', etc.
    predicted_height = db.Column(db.Float, nullable=False)    # in cm
    growth_rate = db.Column(db.Float, nullable=False)          # cm/day
    height_7d = db.Column(db.Float, nullable=False)            # projected height in 7 days
    height_30d = db.Column(db.Float, nullable=False)           # projected height in 30 days
    estimated_harvest = db.Column(db.DateTime, nullable=False) # date of estimated harvest
    health_score = db.Column(db.Float, nullable=False)         # 0 to 100
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
