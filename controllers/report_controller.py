from flask import send_file, flash, redirect, url_for
from flask_login import current_user, login_required
from models.plant import Plant
from models.sensor import SensorReading
from models.disease import DiseaseDiagnosis
from models.prediction import GrowthPrediction
from services.report_service import ReportService

class ReportController:
    @staticmethod
    def download_report(plant_id):
        """Generate and serve a downloadable PDF summary sheet for a plant"""
        plant = Plant.query.get_or_404(plant_id)
        
        # Verify access
        if current_user.role != 'Admin' and plant.user_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for('plant.list_plants'))
            
        # Get historical records
        readings = SensorReading.query.filter_by(plant_id=plant.id).order_by(
            SensorReading.timestamp.desc()
        ).all()
        
        diagnoses = DiseaseDiagnosis.query.filter_by(plant_id=plant.id).order_by(
            DiseaseDiagnosis.timestamp.desc()
        ).all()
        
        predictions = GrowthPrediction.query.filter_by(plant_id=plant.id).order_by(
            GrowthPrediction.timestamp.desc()
        ).all()
        
        # Build PDF using ReportService
        pdf_buffer = ReportService.generate_plant_pdf(
            plant=plant,
            readings=readings,
            diagnoses=diagnoses,
            predictions=predictions
        )
        
        filename = f"plant_{plant.id}_report_{datetime_now_str()}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

def datetime_now_str():
    from datetime import datetime
    return datetime.utcnow().strftime('%Y%m%d_%H%M%S')


















