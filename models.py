from .db import db
from datetime import datetime

class StoreStatusPing(db.Model):
    __tablename__ = 'store_status_pings'
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, nullable=False)
    timestamp_utc = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # active/inactive

class BusinessHour(db.Model):
    __tablename__ = 'business_hours'
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6
    start_time_local = db.Column(db.Time, nullable=False)
    end_time_local = db.Column(db.Time, nullable=False)

class StoreTimezone(db.Model):
    __tablename__ = 'store_timezones'
    store_id = db.Column(db.Integer, primary_key=True)
    timezone_str = db.Column(db.String(64), nullable=False)

class Report(db.Model):
    __tablename__ = 'reports'
    report_id = db.Column(db.String(36), primary_key=True)
    status = db.Column(db.String(20), default='Running')
    csv_path = db.Column(db.String(256), nullable=True)
