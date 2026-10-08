from flask import Blueprint, request
from flask_login import login_required
from controllers.plant_controller import PlantController
from controllers.report_controller import ReportController

plant_bp = Blueprint('plant', __name__)

@plant_bp.route('/plants')
@login_required
def list_plants():
    return PlantController.show_plant_list()

@plant_bp.route('/plants/add', methods=['GET', 'POST'])
@login_required
def add_plant():
    return PlantController.add_plant()

@plant_bp.route('/plants/<int:plant_id>/delete', methods=['POST'])
@login_required
def delete_plant(plant_id):
    return PlantController.delete_plant(plant_id)

@plant_bp.route('/plants/<int:plant_id>')
@login_required
def plant_detail(plant_id):
    return PlantController.show_plant_detail(plant_id)

@plant_bp.route('/plants/<int:plant_id>/predict', methods=['POST'])
@login_required
def predict_growth(plant_id):
    return PlantController.run_prediction(plant_id)

@plant_bp.route('/plants/<int:plant_id>/diagnose', methods=['POST'])
@login_required
def diagnose_disease(plant_id):
    return PlantController.diagnose_disease(plant_id)

@plant_bp.route('/plants/<int:plant_id>/report', methods=['GET'])
@login_required
def download_report(plant_id):
    return ReportController.download_report(plant_id)
