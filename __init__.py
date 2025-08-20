from flask import Flask
from .db import db, init_db
from .routes import report_bp

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/store_monitor'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        init_db()

    app.register_blueprint(report_bp)

    return app
