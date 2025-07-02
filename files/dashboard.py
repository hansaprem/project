from flask import Blueprint, render_template, jsonify
from datetime import date
import MySQLdb
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB


dash_bp = Blueprint('dash_bp', __name__)

db = MySQLdb.connect(host="localhost", user="root", password="hansa123456", database="employee_system")
cursor = db.cursor()

@dash_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@dash_bp.route('/api/summary')
def api_summary():
    today = date.today().isoformat()
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=%s", (today,))
    present = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM employees")
    total = cursor.fetchone()[0]
    absent = total - present

    cursor.execute("SELECT date, COUNT(*) FROM attendance GROUP BY date ORDER BY date")
    trend = [{'date': row[0].isoformat(), 'count': row[1]} for row in cursor.fetchall()]

    return jsonify({'present': present, 'absent': absent, 'trend': trend})
