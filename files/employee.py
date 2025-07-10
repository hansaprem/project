from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app,flash
from werkzeug.utils import secure_filename
import os
import MySQLdb
from files.qrcodes import generate_qr_code
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

emp_bp = Blueprint('emp_bp', __name__)

db = MySQLdb.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB)
cursor = db.cursor()
@emp_bp.route('/main')
def main():
    if 'admin' not in session:
        return redirect('/')
    cursor.execute("SELECT id, name, username, email, city, photo, qr_code FROM employees")
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
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'],filename)
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
    print("Photo saved at:", photo_path)
    db.commit()
    return redirect(url_for('emp_bp.main'))

@emp_bp.route('/add_employee', methods=['POST'])
def add_employee():
    try:
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        city = request.form.get('city')
        photo = request.files.get('photo')

        if not all([name, username, email, password, city, photo]):
            flash('All fields are required', 'error')
            return redirect(url_for('emp_bp.main'))

        photo_filename = secure_filename(photo.filename)
        if not photo_filename:
            flash('Invalid photo file', 'error')
            return redirect(url_for('emp_bp.main'))

        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        qr_filename = f"{username}.png"
        qr_dir = os.path.join('static', 'uploads', 'qr_codes')
        qr_path = os.path.join(qr_dir, qr_filename)
        os.makedirs(qr_dir, exist_ok=True)

        try:
           qr_img = generate_qr_code(username)
           qr_img.save(qr_path)
        except Exception as e:
            flash(f'QR code generation failed: {str(e)}', 'error')
            qr_filename = None

        
        cursor.execute(
            """INSERT INTO employees 
            (name, username, email, password, city, photo, qr_code) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (name, username, email, password, city, photo_filename, qr_filename)
        )
       
        print("QR saved at:", qr_path)

        db.commit()
        flash('Employee added successfully!', 'success')
        return redirect(url_for('emp_bp.main'))

    except Exception as e:
        db.rollback()
        flash(f'Error adding employee: {str(e)}', 'error')
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


@emp_bp.route('/employees')
def employee_cards():
    cursor = db.cursor()
    cursor.execute("SELECT id, name, username, email, city, photo, qr_code FROM employees")
    employees = cursor.fetchall()
    return render_template('employee_cards.html', employees=employees)
