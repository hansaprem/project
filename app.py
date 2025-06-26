from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'project123'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'hansa123456'
app.config['MYSQL_DB'] = 'employee_system'

mysql = MySQL(app)

# Upload Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Main Route (Login + Add + View/Search)
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if 'login' in request.form:
            username = request.form['username']
            password = request.form['password']
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, username, password FROM employees WHERE username = %s", (username,))
            user = cur.fetchone()
            cur.close()
            if user and user[2] == password:
                session['user_id'] = user[0]
                session['username'] = user[1]
                flash('Login successful!', 'success')
            else:
                flash('Invalid credentials', 'danger')
            return redirect(url_for('main'))

        if 'add_employee' in request.form:
            name = request.form['name']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']  # 👈 stored as plain-text
            city = request.form['city']
            photo = request.files['photo']
            filename = None
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO employees (name, username, email, password, city, photo) VALUES (%s, %s, %s, %s, %s, %s)",
                        (name, username, email, password, city, filename))
            mysql.connection.commit()
            cur.close()
            flash('Employee added successfully!', 'success')
            return redirect(url_for('main'))

    search = request.args.get('search', '')
    cur = mysql.connection.cursor()
    if search:
        cur.execute("SELECT id, name, username, email, city, photo FROM employees WHERE name LIKE %s OR city LIKE %s",
                    (f"%{search}%", f"%{search}%"))
    else:
        cur.execute("SELECT id, name, username, email, city, photo FROM employees")
    employees = cur.fetchall()
    cur.close()
    return render_template('main.html', employees=employees, search=search, username=session.get('username'))

# ✅ Update
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('main'))

    name = request.form['name']
    username = request.form['username']
    email = request.form['email']
    city = request.form['city']
    photo = request.files.get('photo')
    filename = None

    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        query = "UPDATE employees SET name=%s, username=%s, email=%s, city=%s, photo=%s WHERE id=%s"
        values = (name, username, email, city, filename, id)
    else:
        query = "UPDATE employees SET name=%s, username=%s, email=%s, city=%s WHERE id=%s"
        values = (name, username, email, city, id)

    cur = mysql.connection.cursor()
    cur.execute(query, values)
    mysql.connection.commit()
    cur.close()

    flash('Employee updated successfully!', 'success')
    return redirect(url_for('main'))

# ✅ Delete
@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('main'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT photo FROM employees WHERE id = %s", (id,))
    photo = cur.fetchone()
    if photo and photo[0]:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo[0]))
        except:
            pass

    cur.execute("DELETE FROM employees WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Employee deleted successfully!', 'success')
    return redirect(url_for('main'))

# ✅ Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('main'))

# ✅ Edit Form Loader
@app.route('/edit/<int:id>')
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('main'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, username, email, city, photo FROM employees WHERE id = %s", (id,))
    employee = cur.fetchone()
    cur.close()
    return render_template('edit_form.html', employee=employee)

if __name__ == '__main__':
    app.run(debug=True)
