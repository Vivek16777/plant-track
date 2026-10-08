from database.connection import db
from datetime import datetime

class IrrigationRecord(db.Model):
    __tablename__ = 'irrigation_records'
    
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id', ondelete='CASCADE'), nullable=False)
    water_amount_ml = db.Column(db.Float, nullable=False)  # in ml
    method = db.Column(db.String(50), nullable=False)        # 'Drip', 'Sprinkler', 'Manual', etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class FertilizerRecord(db.Model):
    __tablename__ = 'fertilizer_records'
    
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id', ondelete='CASCADE'), nullable=False)
    fertilizer_name = db.Column(db.String(100), nullable=False)
    NPK = db.Column(db.String(20), nullable=True)             # e.g. "10-10-10"
    quantity_g = db.Column(db.Float, nullable=False)         # in grams
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
