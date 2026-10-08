from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from controllers.iot_controller import IotController
from services.weather_service import WeatherService

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/telemetry', methods=['POST'])
def receive_telemetry():
    return IotController.receive_telemetry()

@api_bp.route('/api/telemetry/simulate', methods=['POST'])
@login_required
def simulate_telemetry():
    return IotController.simulate_telemetry_batch()

@api_bp.route('/api/weather-proxy', methods=['GET'])
@login_required
def weather_proxy():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude are required.'}), 400
        
    api_key = current_app.config.get('OPENWEATHER_API_KEY', '')
    weather_svc = WeatherService(api_key=api_key)
    res = weather_svc.get_weather(lat, lon)
    
    if res.get('success', False):
        # Generate weather-based farming recommendations
        tips = WeatherService.get_farming_recommendations(
            res['temperature'], 
            res['humidity'], 
            res['rain_probability']
        )
        res['recommendations'] = tips
        return jsonify(res)
    else:
        return jsonify({'error': res.get('error', 'Weather fetch failed')}), 500

@api_bp.route('/api/soil-types', methods=['GET'])
@login_required
def get_soil_types():
    from app import soil_types_data
    return jsonify(soil_types_data)
