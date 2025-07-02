from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import MySQLdb
from files.qrcodes import generate_qr_code
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

emp_bp = Blueprint('emp_bp', __name__)

# DB connection
db = MySQLdb.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
cursor = db.cursor()

@emp_bp.route('/main')
def main():
    if 'admin' not in session:
        return redirect('/')
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    return render_template('main.html', employees=employees)

@emp_bp.route('/edit/<int:id>')
def edit(id):
    cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
    employee = cursor.fetchone()
    return render_template('edit_form.html', employee=employee)

@emp_bp.route('/update/<int:id>', methods=['POST'])
def update_employee(id):
    name = request.form['name']
    username = request.form['username']
    email = request.form['email']
    city = request.form['city']
    photo = request.files['photo']

    if photo and photo.filename != '':
        filename = secure_filename(photo.filename)
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)
        cursor.execute(
            "UPDATE employees SET name=%s, username=%s, email=%s, city=%s, photo=%s WHERE id=%s",
            (name, username, email, city, filename, id)
        )
    else:
        cursor.execute(
            "UPDATE employees SET name=%s, username=%s, email=%s, city=%s WHERE id=%s",
            (name, username, email, city, id)
        )
    db.commit()
    return redirect(url_for('emp_bp.main'))

@emp_bp.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    city = request.form['city']
    photo = request.files['photo']

    filename = secure_filename(photo.filename)
    photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    photo.save(photo_path)

    cursor.execute(
        "INSERT INTO employees (name, username, email, password, city, photo) VALUES (%s, %s, %s, %s, %s, %s)",
        (name, username, email, password, city, filename)
    )
    db.commit()
    generate_qr_code(username)

    return redirect(url_for('emp_bp.main'))

@emp_bp.route('/delete/<int:id>')
def delete_employee(id):
    cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
    db.commit()
    return redirect(url_for('emp_bp.main'))

@emp_bp.route('/generate_qr/<username>')
def generate_qr(username):
    path = generate_qr_code(username)
    return jsonify({"status": "success", "message": f"QR generated at {path}"})
