from flask import Blueprint, render_template, jsonify, request
from datetime import datetime, date
import MySQLdb
from config import *

att_bp = Blueprint('att_bp', __name__)

db = MySQLdb.connect(host="localhost", user="root", password="hansa123456", database="employee_system")
cursor = db.cursor()

@att_bp.route('/scan')
def scan():
    return render_template('scan.html')

@att_bp.route('/scan_qr', methods=['POST'])
def scan_qr():
    data = request.get_json()
    username = data['employee_id']
    today = date.today().isoformat()
    now = datetime.now().strftime('%H:%M')

    cursor.execute("SELECT id FROM employees WHERE username=%s", (username,))
    employee = cursor.fetchone()
    if not employee:
        return jsonify({'status': 'error', 'message': 'Employee not found'})

    emp_id = employee[0]
    cursor.execute("SELECT * FROM attendance WHERE employee_id=%s AND date=%s", (emp_id, today))
    record = cursor.fetchone()

    if not record:
        cursor.execute("INSERT INTO attendance (employee_id, date, sign_in) VALUES (%s, %s, %s)",
                       (emp_id, today, now))
        db.commit()
        return jsonify({'status': 'success', 'message': f'Signed in at {now}'})
    elif record and not record[4]:
        cursor.execute("UPDATE attendance SET sign_out=%s WHERE id=%s", (now, record[0]))
        db.commit()
        return jsonify({'status': 'success', 'message': f'Signed out at {now}'})
    else:
        return jsonify({'status': 'info', 'message': 'Already signed out'})
