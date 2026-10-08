import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'precis-agri-secret-key-12345')
    
    # Base directory of the application
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Database configuration (defaulting to SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'smart_agriculture.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configurations
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # API configuration
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')  # Add your API key here
    
    # Machine Learning paths
    SEED_MODEL_PATH = os.path.join(BASE_DIR, 'agricultural_models.pkl')
    SEED_VALUES_PATH = os.path.join(BASE_DIR, 'unique_values.pkl')
    GROWTH_MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'plant_growth_model.pkl')
