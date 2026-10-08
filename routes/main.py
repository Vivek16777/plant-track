from flask import Blueprint, redirect, url_for, render_template, request, jsonify
from flask_login import login_required, current_user
from controllers.dashboard_controller import DashboardController
from controllers.iot_controller import IotController
from ml.seed_model import SeedSowingModel
from services.advice_service import AdviceService

main_bp = Blueprint('main', __name__)
seed_sowing_model = SeedSowingModel()

@main_bp.route('/')
def index():
    """Redirect to dashboard if logged in, otherwise to login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return DashboardController.get_dashboard_data()

@main_bp.route('/iot')
@login_required
def iot_cockpit():
    return IotController.show_iot_page()

@main_bp.route('/seed_size')
@login_required
def seed_size():
    dropdown_vals = seed_sowing_model.get_dropdown_values()
    
    # Render using the list of soils and their descriptions
    from app import soil_types_data
    return render_template(
        'seed_size.html',
        crops=dropdown_vals['Crop Name'],
        regions=dropdown_vals['Region'],
        seasons=dropdown_vals['Season'],
        soil_types=dropdown_vals['Soil Type'],
        soil_data=soil_types_data
    )

@main_bp.route('/seed_size/predict', methods=['POST'])
@login_required
def seed_predict():
    if not seed_sowing_model.is_loaded:
        return jsonify({'error': 'Sowing models not loaded, check server logs.'}), 500
        
    try:
        crop_name = request.form['crop_name']
        region = request.form['region']
        season = request.form['season']
        temperature = float(request.form.get('temperature', 0))
        moisture = float(request.form.get('moisture', 0))
        soil_type = request.form['soil_type']
        soil_ph = float(request.form['soil_ph'])
        
        pred = seed_sowing_model.predict(
            crop_name, region, season, temperature, moisture, soil_type, soil_ph
        )
        
        if pred is None:
            return jsonify({'error': 'Failed to execute machine learning model prediction.'}), 500
            
        # Get soil analysis details using AdviceService
        soil_analysis = AdviceService.get_soil_analysis(soil_type, soil_ph)
        
        return jsonify({
            'seed_size': pred['seed_size'],
            'sowing_depth': pred['sowing_depth'],
            'spacing': pred['spacing'],
            'selected_soil_type': soil_type,
            'soil_description': soil_analysis['soil_quality'],
            'recommended_crops': soil_analysis['suitable_crops']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@main_bp.route('/sensor_docs')
@login_required
def sensor_docs():
    return render_template('sensor_docs.html')
