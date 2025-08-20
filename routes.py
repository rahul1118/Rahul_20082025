import uuid
from flask import Blueprint, jsonify, send_file, request
from .db import db
from .models import Report
from .report_generator import generate_report

report_bp = Blueprint('report', __name__)

@report_bp.route('/trigger_report', methods=['POST'])
def trigger_report():
    report_id = str(uuid.uuid4())
    report = Report(report_id=report_id, status='Running')
    db.session.add(report)
    db.session.commit()

    # run report generation in background (simple way)
    generate_report(report_id)  # synchronous for simplicity

    return jsonify({"report_id": report_id})

@report_bp.route('/get_report', methods=['GET'])
def get_report():
    report_id = request.args.get('report_id')
    report = Report.query.filter_by(report_id=report_id).first()
    if not report:
        return "Invalid report_id", 404
    if report.status != 'Complete':
        return "Running"
    return send_file(report.csv_path, mimetype='text/csv', as_attachment=True)
