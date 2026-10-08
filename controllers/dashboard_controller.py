from flask import render_template
from flask_login import current_user, login_required
from models.plant import Plant
from models.sensor import SensorReading
from models.records import IrrigationRecord
from models.prediction import GrowthPrediction
from models.notification import Notification
from database.connection import db
from sqlalchemy import func

class DashboardController:
    @staticmethod
    def get_dashboard_data():
        """Aggregate stats and trends to render the user home dashboard"""
        # Role-based plant filtering
        if current_user.role == 'Admin':
            plants_query = Plant.query
        else:
            plants_query = Plant.query.filter_by(user_id=current_user.id)
            
        plants = plants_query.all()
        total_plants = len(plants)
        
        healthy_plants = sum(1 for p in plants if p.status == 'Healthy')
        diseased_plants = sum(1 for p in plants if p.status == 'Diseased')
        
        # Calculate averages of recent sensor readings
        plant_ids = [p.id for p in plants]
        
        avg_moisture = 0.0
        avg_temp = 0.0
        avg_humidity = 0.0
        
        if plant_ids:
            # Query average values of the latest readings
            subq = db.session.query(
                SensorReading.plant_id,
                func.max(SensorReading.timestamp).label('max_ts')
            ).filter(SensorReading.plant_id.in_(plant_ids)).group_by(SensorReading.plant_id).subquery()
            
            latest_readings = SensorReading.query.join(
                subq,
                (SensorReading.plant_id == subq.c.plant_id) & (SensorReading.timestamp == subq.c.max_ts)
            ).all()
            
            if latest_readings:
                avg_moisture = sum(r.soil_moisture for r in latest_readings) / len(latest_readings)
                avg_temp = sum(r.temperature for r in latest_readings) / len(latest_readings)
                avg_humidity = sum(r.humidity for r in latest_readings) / len(latest_readings)
                
        # Average predicted growth % (based on health score of latest growth predictions)
        avg_health = 0.0
        if plant_ids:
            subq_p = db.session.query(
                GrowthPrediction.plant_id,
                func.max(GrowthPrediction.timestamp).label('max_ts')
            ).filter(GrowthPrediction.plant_id.in_(plant_ids)).group_by(GrowthPrediction.plant_id).subquery()
            
            latest_preds = GrowthPrediction.query.join(
                subq_p,
                (GrowthPrediction.plant_id == subq_p.c.plant_id) & (GrowthPrediction.timestamp == subq_p.c.max_ts)
            ).all()
            
            if latest_preds:
                avg_health = sum(p.health_score for p in latest_preds) / len(latest_preds)
                
        # Water usage: sum of irrigation records in the last 7 days
        water_used = 0.0
        if plant_ids:
            total_water = db.session.query(func.sum(IrrigationRecord.water_amount_ml)).filter(
                IrrigationRecord.plant_id.in_(plant_ids)
            ).scalar()
            if total_water:
                water_used = total_water
                
        # Recent notifications
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
            Notification.timestamp.desc()
        ).limit(5).all()
        
        # Growth Trend data (average height history grouped by date)
        # We can build a simple list of heights for the last few days
        trend_dates = []
        trend_heights = []
        if plant_ids:
            # Query recent growth predictions
            recent_growth = GrowthPrediction.query.filter(
                GrowthPrediction.plant_id.in_(plant_ids)
            ).order_by(GrowthPrediction.timestamp.asc()).limit(30).all()
            
            # Group by date
            grouped = {}
            for rg in recent_growth:
                date_str = rg.timestamp.strftime('%m-%d')
                if date_str not in grouped:
                    grouped[date_str] = []
                grouped[date_str].append(rg.predicted_height)
                
            for d, vals in list(grouped.items())[-7:]: # Last 7 intervals
                trend_dates.append(d)
                trend_heights.append(sum(vals) / len(vals))
                
        # Defaults if no trend data
        if not trend_dates:
            trend_dates = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            trend_heights = [10, 12, 15, 18, 22, 25, 29]
            
        return render_template(
            'dashboard.html',
            total_plants=total_plants,
            healthy_plants=healthy_plants,
            diseased_plants=diseased_plants,
            avg_moisture=round(avg_moisture, 1),
            avg_temp=round(avg_temp, 1),
            avg_humidity=round(avg_humidity, 1),
            avg_health=round(avg_health, 1),
            water_used=round(water_used / 1000.0, 2), # convert ml to Litres
            notifications=notifications,
            trend_dates=trend_dates,
            trend_heights=trend_heights,
            plants=plants[:5]  # Limit to 5 plants in dashboard list
        )
