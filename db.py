from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db():
    from .models import StoreStatusPing, BusinessHour, StoreTimezone, Report
    db.create_all()
