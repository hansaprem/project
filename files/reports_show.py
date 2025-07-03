from flask import Blueprint, render_template

report_page_bp = Blueprint('report_page_bp', __name__)

@report_page_bp.route('/reports')
def show_reports():
    return render_template('reports.html')

