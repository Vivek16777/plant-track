from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize database and create instance folder if needed"""
    import os
    # Ensure the instance directory exists for SQLite db file
    os.makedirs(os.path.join(app.config['BASE_DIR'], 'instance'), exist_ok=True)
    db.init_app(app)
