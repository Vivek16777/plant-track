import os
from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager
from config.config import Config
from database.connection import db, init_db
from models.user import User

# Blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.api import api_bp
from routes.plant import plant_bp

# Static detailed soil database
soil_types_data = [
    {
        "id": "black_soil",
        "name": "Black Soil",
        "description": "Black soil, or Regur soil, is rich in clay minerals, calcium carbonate, magnesium, potash, and lime. It has excellent water retention capacity and is highly suitable for cotton cultivation.",
        "color": "#2d2d2d",
        "characteristics": ["High water retention", "Rich in nutrients", "Clay-like texture", "Self-ploughing nature"],
        "suitable_crops": [],
        "regions": ["Vidarbha", "Marathwada"]
    },
    {
        "id": "red_soil",
        "name": "Red Soil",
        "description": "Red soil gets its color from iron oxide. It is generally poor in nitrogen, phosphoric acid, and organic matter but rich in potash. It's porous with good drainage properties.",
        "color": "#8B2500",
        "characteristics": ["Porous and well-drained", "Rich in iron oxides", "Poor in nitrogen", "Sandy to clayey texture"],
        "suitable_crops": [],
        "regions": ["Western Maharashtra"]
    },
    {
        "id": "laterite_soil",
        "name": "Laterite Soil",
        "description": "Laterite soil is formed under tropical conditions due to intense weathering. It's rich in iron and aluminum but poor in nitrogen, potash, potassium, lime, and magnesium.",
        "color": "#BA8759",
        "characteristics": ["Highly weathered", "Rich in iron and aluminum", "Poor in organic matter", "Acidic nature"],
        "suitable_crops": [],
        "regions": ["Konkan"]
    },
    {
        "id": "medium_black_soil",
        "name": "Medium Black Soil",
        "description": "Medium black soil is less clayey than pure black soil but still has good moisture retention and nutrient content. It's versatile and supports a wide range of crops.",
        "color": "#4A4A4A",
        "characteristics": ["Moderate water retention", "Well-balanced texture", "Good fertility", "Mixed clayey and loamy"],
        "suitable_crops": [],
        "regions": ["North Maharashtra"]
    },
    {
        "id": "alluvial_soil",
        "name": "Alluvial Soil",
        "description": "Alluvial soil is formed by sediment deposited by rivers. It's extremely fertile with high amounts of potash, phosphoric acid, and lime but varying proportions of organic matter.",
        "color": "#D3C1AD",
        "characteristics": ["Very fertile", "Rich in minerals", "Variable texture", "Renewable fertility"],
        "suitable_crops": [],
        "regions": ["Various river basins in Maharashtra"]
    },
    {
        "id": "sandy_soil",
        "name": "Sandy Soil",
        "description": "Sandy soil has large particles with excellent drainage but poor water and nutrient retention. It warms quickly in spring and is typically acidic. Suitable for early planting, root vegetables, and drought-resistant plants.",
        "color": "#E6CC8A",
        "characteristics": ["Excellent drainage", "Poor water retention", "Low nutrient content", "Warms quickly"],
        "suitable_crops": [],
        "regions": ["Arid and semi-arid areas, river banks"]
    }
]

def create_app():
    """Application factory for the Intelligent Plant Growth Framework"""
    app = Flask(__name__)
    CORS(app) # Enable CORS for all routes
    app.config.from_object(Config)
    
    # Initialize database
    init_db(app)
    
    # Configure Flask-Login Session Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(plant_bp)
    
    # Database migration & seed logic
    with app.app_context():
        db.create_all()
        # Seed default users if empty
        if User.query.count() == 0:
            print("Database is empty. Seeding default demo accounts...")
            
            # Admin account
            admin = User(username='admin', email='admin@agri.com', role='Admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Farmer account
            farmer = User(username='farmer', email='farmer@agri.com', role='Farmer')
            farmer.set_password('farmer123')
            db.session.add(farmer)
            
            db.session.commit()
            print("Demo accounts created: admin (admin123), farmer (farmer123)")
            
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    # Run the server
    app.run(host='0.0.0.0', port=port, debug=False)
